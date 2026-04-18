def get_urls(query: str, n_results: int = 5):
    """
    Retrieves top web URLs related to the query.
    Safe version for deployment.
    """
    try:
        from googlesearch import search

        return list(search(query, num_results=n_results))

    except Exception as e:
        print("Search error:", e)

        # fallback (VERY IMPORTANT)
        return []