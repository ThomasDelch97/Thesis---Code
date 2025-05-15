import requests
import time
def fetch_html(url, session, REQUEST_DELAY):
    """Fetch HTML content with robust error handling and rate limiting"""
    time.sleep(REQUEST_DELAY)  # Maintain rate limiting
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None
    

def cleanName(df, column, value):
    try:
        clean = df[column].str.strip().str.replace(value, '').str.lower()
    except:
        return "Not a Series with string only, look here dumbass:", df[column].dtype()
    return clean