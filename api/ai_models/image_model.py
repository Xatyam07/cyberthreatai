from PIL import Image, ImageChops, ImageEnhance
import io
import piexif
import numpy as np

# ---------------------------------------------------
# 1️⃣ EXIF METADATA ANALYSIS
# ---------------------------------------------------
def check_exif(image):
    try:
        exif_dict = piexif.load(image.info["exif"])
        return True   # metadata exists
    except:
        return False  # no metadata → suspicious


# ---------------------------------------------------
# 2️⃣ ERROR LEVEL ANALYSIS (ELA)
# ---------------------------------------------------
def perform_ela(image):
    temp_file = "temp.jpg"

    # Save image with compression
    image.save(temp_file, "JPEG", quality=90)
    compressed = Image.open(temp_file)

    # Difference between original & compressed
    ela_image = ImageChops.difference(image, compressed)

    # Enhance differences
    enhancer = ImageEnhance.Brightness(ela_image)
    ela_image = enhancer.enhance(20)

    # Convert to numpy to calculate brightness
    ela_array = np.array(ela_image)
    ela_score = ela_array.mean()

    return ela_score


# ---------------------------------------------------
# 3️⃣ FINAL IMAGE ANALYSIS FUNCTION
# ---------------------------------------------------
def analyze_image(file_bytes):

    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")

    risk = 0
    reasons = []

    # ---- EXIF CHECK ----
    has_exif = check_exif(image)
    if not has_exif:
        risk += 25
        reasons.append("Metadata missing (possible screenshot/download)")

    # ---- ELA CHECK ----
    ela_score = perform_ela(image)
    if ela_score > 15:
        risk += 40
        reasons.append("Editing traces detected using ELA")

    # Normalize score
    risk = min(risk, 95)

    if risk < 30:
        reasons.append("No strong manipulation signs")

    return {
        "score": risk,
        "reasons": reasons
    }
