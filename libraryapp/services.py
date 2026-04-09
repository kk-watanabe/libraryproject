"""
import requests

def fetch_book_by_isbn(isbn):
    url = f"https://api.openbd.jp/v1/get?isbn={isbn}"
    response = requests.get(url)

    if response.status_code != 200:
        return None
    
    book = response.json()[0]
    if not book:
        return None
    
    summary = book["summary"]

    return {
        "title": summary.get("title", ""),
        "author": summary.get("author", ""),
        "publisher": summary.get("publisher", ""),
        "publication_date": summary.get("pubdate", ""),
        "image_url": summary.get("cover", "")
    }

"""