# api_client.py
import requests
from config import API_URL

def api_lookup(word):
    """
    Fetches the dictionary entry for a word from the external API.
    Returns the first entry data or None on failure.
    """
    try:
        response = requests.get(API_URL + word, timeout=5)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        if data and isinstance(data, list):
            return data[0]
        return None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            # Word not found is common, return None without printing a network error
            return None
        print(f"HTTP error fetching '{word}': {e}")
        return None
    except requests.exceptions.RequestException:
        print(f"Network error fetching '{word}'.")
        return None