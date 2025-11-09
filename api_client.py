import requests
from config import API_URL

# Simple in-memory cache (you can later switch to file-based)
_cache = {}

def api_lookup(word):
    """
    Fetches the dictionary entry for a word from the Free Dictionary API.
    Uses caching to avoid repeated API calls and sets a short timeout.
    Returns the first entry data or None on failure.
    """
    word = word.lower().strip()
    if not word:
        return None

    # ✅ Step 1: Check cache first (instant response for repeated words)
    if word in _cache:
        return _cache[word]

    # ✅ Step 2: Fetch from API
    try:
        print(f"🔍 Looking up '{word}' ...")
        response = requests.get(API_URL + word, timeout=2)  # shorter timeout (2s)
        response.raise_for_status()  # Raise error for 4xx/5xx

        data = response.json()
        if data and isinstance(data, list):
            _cache[word] = data[0]  # Save in cache
            return data[0]

        return None

    except requests.exceptions.Timeout:
        print("⏱️ Request timed out. The API took too long to respond.")
        return None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return None  # word not found
        print(f"❌ HTTP error fetching '{word}': {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network error fetching '{word}': {e}")
        return None
