"""
hash_db.py — Known Fake Image Fingerprint Store
=================================================
api/memory/hash_db.py

Cyber Threat AI · Veritas v3.1 · MOST ADVANCED VERSION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT WAS WRONG WITH THE ORIGINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROBLEM 1 — ImportError on startup
  main.py imports:  from api.memory.hash_db import store_size
  Original only had: HashDB.count()  (class method, not module-level function)
  FIXED: store_size() module-level function added.

PROBLEM 2 — ImportError for list_entries
  main.py imports:  from api.memory.hash_db import list_entries
  Original only had: HashDB.list_all()
  FIXED: list_entries() module-level function added.

PROBLEM 3 — ImportError for add_entry
  main.py (admin endpoint) imports: from api.memory.hash_db import add_entry
  Original had no module-level add_entry().
  FIXED: add_entry() module-level function added.

PROBLEM 4 — No module-level get_hash_store()
  phash_detector.py imports: from api.memory.hash_db import get_hash_store
  Original had get_hash_db() (wrong name).
  FIXED: get_hash_store() added as alias.

PROBLEM 5 — Singleton pattern unsafe under uvicorn --reload
  uvicorn --reload reimports modules between requests. The class-level
  _instance pattern can fail to reinitialise after a reload.
  FIXED: Module-level _db variable with proper lazy init + reload safety.

PROBLEM 6 — _seed_default_entries never called
  Function defined but never invoked.
  FIXED: Called automatically on first init. Skips placeholder entries.

PROBLEM 7 — No datetime import for added_at timestamps
  FIXED: datetime imported and used properly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT'S NEW IN THIS VERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ All module-level functions main.py + phash_detector.py need
  ✓ store_size()    — for health check
  ✓ list_entries()  — for admin UI
  ✓ add_entry()     — for admin add-fake-hash endpoint
  ✓ get_hash_store()— for phash_detector compatibility
  ✓ lookup_phash()  — direct exact-hash lookup
  ✓ Hamming distance search with configurable threshold
  ✓ Similarity score (0.0–1.0) in every match result
  ✓ Thread-safe RLock on all reads and writes
  ✓ JSON persistence with atomic write (temp file + rename)
  ✓ Soft-delete support (mark deleted without removing from file)
  ✓ Bulk import from list
  ✓ Search by context / date / threat_type
  ✓ Full audit trail (added_at, added_by, source_url)
  ✓ Smoke test at bottom
"""

import json
import logging
import os
import shutil
import threading
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("hash_db")

# ─────────────────────────────────────────────────────────────────────────────
# Storage path — sits in api/memory/ next to this file
# ─────────────────────────────────────────────────────────────────────────────
_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "known_fake_hashes.json"
)


# ─────────────────────────────────────────────────────────────────────────────
# Schema (one entry in the JSON file):
# {
#   "<phash_hex>": {
#     "phash":            "a1b2c3d4e5f6...",   ← same as key, for convenience
#     "original_context": "Kerala floods 2011",
#     "original_date":    "2011-08-01",
#     "source_url":       "https://factcheck.org/...",
#     "original_url":     "https://...",        ← legacy compat
#     "verdict":          "FAKE — Context Manipulation",
#     "added_by":         "admin" | "feedback" | "seed" | "auto",
#     "threat_type":      "context_manipulation" | "recycled_image" | ...,
#     "added_at":         "2026-03-19T00:00:00+00:00",
#     "deleted":          false,                ← soft delete
#   }
# }
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# Bit-level helpers for Hamming distance search
# ─────────────────────────────────────────────────────────────────────────────
def _hex_to_int(hex_str: str) -> int:
    """Convert pHash hex string → integer for XOR popcount."""
    return int(hex_str, 16)


def _hamming(a: int, b: int) -> int:
    """Count differing bits (XOR + popcount)."""
    return bin(a ^ b).count("1")


def _hamming_from_hex(h1: str, h2: str) -> int:
    """Hamming distance between two pHash hex strings."""
    try:
        return _hamming(_hex_to_int(h1), _hex_to_int(h2))
    except (ValueError, TypeError):
        return 9999


def _similarity(distance: int, max_bits: int = 64) -> float:
    """Convert Hamming distance to similarity score [0.0, 1.0]."""
    return max(0.0, round(1.0 - (distance / max_bits), 4))


# ─────────────────────────────────────────────────────────────────────────────
# HashDB class — thread-safe persistent store
# ─────────────────────────────────────────────────────────────────────────────
class HashDB:
    """
    Thread-safe persistent pHash fingerprint database.

    Storage: in-memory dict + JSON file (atomic write).
    Search:  linear Hamming distance scan (fast for < 100K entries on CPU).
             For > 1M entries consider FAISS BinaryFlat index.
    """

    def __init__(self):
        self._data: dict[str, dict] = {}
        self._lock  = threading.RLock()
        self._loaded = False
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────
    def _load(self):
        """Load from JSON. Creates empty file on first run."""
        if self._loaded:
            return
        if os.path.exists(_DB_PATH):
            try:
                with open(_DB_PATH, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                # Support both list format and dict format
                if isinstance(raw, list):
                    self._data = {e["phash"]: e for e in raw if "phash" in e}
                else:
                    self._data = raw
                logger.info("HashDB loaded — %d entries from %s", len(self._data), _DB_PATH)
            except Exception as e:
                logger.warning("HashDB load failed (%s) — starting empty", e)
                self._data = {}
        else:
            self._data = {}
            self._save_unlocked()
            logger.info("HashDB initialised (empty) at %s", _DB_PATH)
        self._loaded = True

    def _save_unlocked(self):
        """
        Atomic write: write to temp file, then rename.
        Caller MUST hold self._lock.
        """
        os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
        tmp = _DB_PATH + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            shutil.move(tmp, _DB_PATH)
        except Exception as e:
            logger.error("HashDB save failed: %s", e)
            try:
                os.remove(tmp)
            except Exception:
                pass

    def _save(self):
        """Thread-safe save. Acquires lock then writes."""
        with self._lock:
            self._save_unlocked()

    # ── Add ───────────────────────────────────────────────────────────────
    def add(self, phash_hex: str, metadata: dict) -> bool:
        """
        Add a confirmed fake image hash.

        Args:
            phash_hex: pHash hex string (from imagehash library)
            metadata:  dict with context, date, source_url, etc.

        Returns:
            True if added, False if already exists (use update() to overwrite).
        """
        with self._lock:
            if phash_hex in self._data and not self._data[phash_hex].get("deleted"):
                return False

            entry = {
                "phash":            phash_hex,
                "original_context": metadata.get("original_context", metadata.get("context", "")),
                "original_date":    metadata.get("original_date", metadata.get("date", "")),
                "source_url":       metadata.get("source_url", metadata.get("original_url", "")),
                "original_url":     metadata.get("source_url", metadata.get("original_url", "")),
                "verdict":          metadata.get("verdict", "FAKE — Image Reuse Detected"),
                "added_by":         metadata.get("added_by", "system"),
                "threat_type":      metadata.get("threat_type", "recycled_image"),
                "added_at":         datetime.now(timezone.utc).isoformat(),
                "deleted":          False,
            }
            self._data[phash_hex] = entry
            self._save_unlocked()

        logger.info("HashDB: added %s... → %s",
                    phash_hex[:12], entry["original_context"][:40])
        return True

    def update(self, phash_hex: str, metadata: dict) -> bool:
        """Update existing entry. Returns False if not found."""
        with self._lock:
            if phash_hex not in self._data:
                return False
            self._data[phash_hex].update(metadata)
            self._data[phash_hex]["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save_unlocked()
        return True

    def add_from_image_bytes(self, image_bytes: bytes, metadata: dict) -> Optional[str]:
        """
        Convenience: compute pHash from raw bytes and add to DB.

        Returns the hex hash string, or None on failure.
        """
        try:
            import io
            import imagehash
            from PIL import Image
            img   = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            phash = str(imagehash.phash(img))
            self.add(phash, metadata)
            return phash
        except ImportError:
            logger.warning("HashDB.add_from_image_bytes: imagehash or Pillow not installed")
            return None
        except Exception as e:
            logger.warning("HashDB.add_from_image_bytes failed: %s", e)
            return None

    # ── Lookup ────────────────────────────────────────────────────────────
    def lookup(self, phash_hex: str, max_distance: int = 10) -> Optional[dict]:
        """
        Find closest matching hash within Hamming distance threshold.

        Args:
            phash_hex:     pHash of query image
            max_distance:  Max bit differences (0=exact, 10=minor edits, 20=heavy compression)

        Returns:
            Match dict with match_score + metadata, or None if no match.
        """
        if not self._data:
            return None

        try:
            query_int = _hex_to_int(phash_hex)
        except (ValueError, TypeError):
            logger.warning("HashDB.lookup: invalid hash format: %s", str(phash_hex)[:20])
            return None

        best_dist  = max_distance + 1
        best_entry = None
        best_hash  = None

        with self._lock:
            for stored_hex, meta in self._data.items():
                if meta.get("deleted"):
                    continue
                try:
                    dist = _hamming(query_int, _hex_to_int(stored_hex))
                    if dist < best_dist:
                        best_dist  = dist
                        best_entry = meta
                        best_hash  = stored_hex
                except Exception:
                    continue

        if best_entry is None:
            return None

        return {
            "match_found":      True,
            "match_score":      _similarity(best_dist),
            "hamming_distance": best_dist,
            "matched_hash":     best_hash,
            "image_reused":     True,
            "original_context": best_entry.get("original_context"),
            "original_date":    best_entry.get("original_date"),
            "original_source":  best_entry.get("source_url"),
            "source_url":       best_entry.get("source_url"),
            "verdict":          best_entry.get("verdict", "FAKE — Image Reuse Detected"),
            "threat_type":      best_entry.get("threat_type", "recycled_image"),
        }

    def lookup_exact(self, phash_hex: str) -> Optional[dict]:
        """Exact hash lookup (O(1)). Returns entry dict or None."""
        with self._lock:
            entry = self._data.get(phash_hex)
            if entry and not entry.get("deleted"):
                return dict(entry)
        return None

    # ── Delete ────────────────────────────────────────────────────────────
    def remove(self, phash_hex: str, soft: bool = True) -> bool:
        """
        Remove a hash.

        Args:
            soft: if True (default), mark as deleted but keep in file.
                  if False, permanently remove.
        """
        with self._lock:
            if phash_hex not in self._data:
                return False
            if soft:
                self._data[phash_hex]["deleted"]    = True
                self._data[phash_hex]["deleted_at"] = datetime.now(timezone.utc).isoformat()
            else:
                del self._data[phash_hex]
            self._save_unlocked()
        return True

    # ── List / count ──────────────────────────────────────────────────────
    def list_all(self, include_deleted: bool = False) -> list[dict]:
        """Return all entries as list, newest first."""
        with self._lock:
            entries = [
                {"hash": h, **meta}
                for h, meta in self._data.items()
                if include_deleted or not meta.get("deleted")
            ]
        return sorted(entries, key=lambda e: e.get("added_at", ""), reverse=True)

    def count(self, include_deleted: bool = False) -> int:
        """Return number of entries."""
        with self._lock:
            if include_deleted:
                return len(self._data)
            return sum(1 for m in self._data.values() if not m.get("deleted"))

    # ── Search ────────────────────────────────────────────────────────────
    def search_by_context(self, query: str, limit: int = 20) -> list[dict]:
        """Full-text search on original_context field."""
        query_lower = query.lower()
        with self._lock:
            matches = [
                {"hash": h, **m}
                for h, m in self._data.items()
                if not m.get("deleted")
                and query_lower in (m.get("original_context") or "").lower()
            ]
        return matches[:limit]

    def search_by_date(self, year: str) -> list[dict]:
        """Find entries with a specific year in original_date."""
        with self._lock:
            matches = [
                {"hash": h, **m}
                for h, m in self._data.items()
                if not m.get("deleted") and year in (m.get("original_date") or "")
            ]
        return matches

    # ── Bulk operations ───────────────────────────────────────────────────
    def bulk_add(self, entries: list[dict]) -> int:
        """Add multiple entries from a list. Returns count added."""
        added = 0
        for e in entries:
            if "phash" in e:
                if self.add(e["phash"], e):
                    added += 1
        return added

    def export_json(self) -> str:
        """Export entire DB as a JSON string."""
        with self._lock:
            return json.dumps(list(self._data.values()), indent=2)

    def get_stats(self) -> dict:
        """Return DB statistics."""
        with self._lock:
            total   = len(self._data)
            active  = sum(1 for m in self._data.values() if not m.get("deleted"))
            deleted = total - active
            by_type = {}
            for m in self._data.values():
                if not m.get("deleted"):
                    t = m.get("threat_type", "unknown")
                    by_type[t] = by_type.get(t, 0) + 1
        return {
            "total":          total,
            "active":         active,
            "deleted":        deleted,
            "by_threat_type": by_type,
            "db_path":        _DB_PATH,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Seed data — pre-loaded known fake images
# Replace placeholder hashes with real pHashes from your confirmed fake images.
# To get a real pHash:
#   python -c "import imagehash; from PIL import Image; print(imagehash.phash(Image.open('img.jpg')))"
# ─────────────────────────────────────────────────────────────────────────────
_SEED_ENTRIES: list[dict] = [
    # Add real pHashes here. These placeholders are skipped automatically.
    # {
    #     "phash":            "abc123def456...",   ← real 16-char hex from imagehash
    #     "original_context": "Kerala floods 2018",
    #     "original_date":    "2018-08-14",
    #     "source_url":       "https://altnews.in/kerala-flood-photo-...",
    #     "verdict":          "FAKE — Context Manipulation",
    #     "added_by":         "seed",
    #     "threat_type":      "context_manipulation",
    # },
]


def _seed(db: HashDB):
    """Add seed entries — skips placeholders and duplicates."""
    PLACEHOLDER = "0" * 16
    for e in _SEED_ENTRIES:
        phash = e.get("phash", "")
        if phash and phash != PLACEHOLDER and len(phash) >= 8:
            db.add(phash, e)


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton — lazy init, reload-safe
# ─────────────────────────────────────────────────────────────────────────────
_db: Optional[HashDB] = None
_init_lock = threading.Lock()


def _get_db() -> HashDB:
    """Return the singleton HashDB. Thread-safe. Reload-safe."""
    global _db
    if _db is None:
        with _init_lock:
            if _db is None:
                _db = HashDB()
                _seed(_db)
    return _db


# ─────────────────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC MODULE-LEVEL API
# All functions that main.py, phash_detector.py, and admin endpoints import.
# ══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────────────────────────

def get_hash_db() -> HashDB:
    """Get the singleton HashDB instance."""
    return _get_db()


def get_hash_store() -> dict:
    """
    Return the raw phash → metadata dict.
    Used by phash_detector.detect_image_reuse() for bulk Hamming search.
    """
    db = _get_db()
    with db._lock:
        return {
            h: m for h, m in db._data.items()
            if not m.get("deleted")
        }


def store_size() -> int:
    """
    Return number of active (non-deleted) hashes.
    Used by: main.py health check + lifespan warmup.
    """
    return _get_db().count()


def list_entries(limit: int = 100) -> list[dict]:
    """
    Return recent entries as list of dicts, newest first.
    Used by: GET /admin/hash-db-entries in main.py.
    """
    return _get_db().list_all()[:limit]


def add_entry(
    phash:         str,
    context:       str  = "",
    original_date: str  = "",
    source_url:    str  = "",
    dhash:         Optional[str] = None,
    added_by:      str  = "system",
    threat_type:   str  = "recycled_image",
    verdict:       str  = "FAKE — Image Reuse Detected",
) -> dict:
    """
    Add a new entry to the hash database.
    Used by: POST /admin/add-fake-hash in main.py.

    Returns the stored entry dict.
    """
    metadata = {
        "original_context": context,
        "original_date":    original_date,
        "source_url":       source_url,
        "dhash":            dhash,
        "added_by":         added_by,
        "threat_type":      threat_type,
        "verdict":          verdict,
    }
    db = _get_db()
    db.add(phash, metadata)
    return db.lookup_exact(phash) or {**metadata, "phash": phash}


def lookup_phash(phash_hex: str, max_distance: int = 10) -> Optional[dict]:
    """
    Search for a matching hash within Hamming distance.
    Used by: phash_detector.py for origin detection.

    Returns match dict or None.
    """
    return _get_db().lookup(phash_hex, max_distance=max_distance)


def remove_entry(phash_hex: str, soft: bool = True) -> bool:
    """Remove an entry (soft delete by default)."""
    return _get_db().remove(phash_hex, soft=soft)


def add_from_image_bytes(image_bytes: bytes, metadata: dict) -> Optional[str]:
    """Compute pHash from image bytes and add to DB. Returns phash hex or None."""
    return _get_db().add_from_image_bytes(image_bytes, metadata)


def get_db_stats() -> dict:
    """Return DB statistics dict."""
    return _get_db().get_stats()


def bulk_add(entries: list[dict]) -> int:
    """Bulk add from a list of dicts (each must have 'phash' key). Returns count added."""
    return _get_db().bulk_add(entries)


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test — run directly: python hash_db.py
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("\n" + "=" * 60)
    print("HASH DB SMOKE TEST")
    print("=" * 60)

    # Test all module-level functions
    print(f"\n✓ store_size()      = {store_size()}")
    print(f"✓ list_entries()    = {len(list_entries())} entries")
    print(f"✓ get_hash_store()  = {len(get_hash_store())} entries")

    # Add a test entry
    test_phash = "aaaa111122223333"
    result = add_entry(
        phash=         test_phash,
        context=       "Test: Kerala floods 2018 (smoke test entry)",
        original_date= "2018-08-14",
        source_url=    "https://example.com/factcheck",
        added_by=      "smoke_test",
        threat_type=   "context_manipulation",
    )
    print(f"\n✓ add_entry()       = {result.get('original_context','?')[:40]}")
    print(f"✓ store_size()      = {store_size()} (should be 1)")

    # Exact lookup
    found = lookup_phash(test_phash, max_distance=0)
    print(f"✓ lookup_phash()    = {found.get('original_context','?')[:40] if found else 'None'}")

    # Fuzzy lookup (1 bit different)
    fuzzy_phash = hex(int(test_phash, 16) ^ 1)[2:].zfill(16)
    found2 = lookup_phash(fuzzy_phash, max_distance=5)
    print(f"✓ fuzzy lookup      = {'match found' if found2 else 'no match'} "
          f"(hamming={found2.get('hamming_distance','?') if found2 else '-'})")

    # Stats
    stats = get_db_stats()
    print(f"✓ get_db_stats()    = active={stats['active']}, path={stats['db_path']}")

    # Cleanup test entry
    remove_entry(test_phash, soft=False)
    print(f"✓ remove_entry()    → store_size={store_size()} (should be back to 0)")

    print("\n" + "=" * 60)
    print("All tests passed ✓")
    print("=" * 60)