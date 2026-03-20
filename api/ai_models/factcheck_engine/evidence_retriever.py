from googlesearch import search

def get_urls(query: str, n_results=5):
    """
    Retrieves top web URLs related to the claim.
    """

    urls = []
    try:
        for url in search(query, num_results=n_results):
            urls.append(url)
    except Exception:
        pass

    return urls
