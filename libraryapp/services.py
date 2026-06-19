# libraryapp/services.py

import requests
from datetime import datetime


def fetch_book_by_isbn(isbn):
    """
    openBD APIから書誌情報を取得
    """

    clean_isbn = isbn.replace("-", "")

    url = f"https://api.openbd.jp/v1/get?isbn={clean_isbn}"

    response = requests.get(url)

    if response.status_code != 200: # エラーチェック
        return None

    data = response.json()

    if not data or data[0] is None:
        return None

    book = data[0]
    summary = book.get("summary", {})

    publication_date = None
    pubdate = summary.get("pubdate", "")

    # openBDの日付整形
    # 202401 → 2024-01-01
    # 20240115 → 2024-01-15
    try:
        if len(pubdate) == 8:
            publication_date = datetime.strptime(
                pubdate,
                "%Y%m%d"
            ).date()

        elif len(pubdate) == 6:
            publication_date = datetime.strptime(
                pubdate,
                "%Y%m"
            ).date()

        elif len(pubdate) == 4:
            publication_date = datetime.strptime(
                pubdate,
                "%Y"
            ).date()

    except Exception:
        publication_date = None
    
    cover_url = summary.get("cover", "")
    
    if not cover_url:
        cover_url = fetch_google_books_cover(clean_isbn)

    return {
        "title": summary.get("title", ""),
        "author": summary.get("author", ""),
        "publisher": summary.get("publisher", ""),
        "publication_date": publication_date,
        "cover_url": cover_url,
    }

def fetch_google_books_cover(isbn):

    #print("google function called")

    url = (
        "https://www.googleapis.com/books/v1/volumes"
        f"?q=isbn:{isbn}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return ""

    data = response.json()
    #print(data)
    items = data.get("items")

    if not items:
        return ""

    volume_info = items[0].get("volumeInfo", {})

    image_links = volume_info.get("imageLinks", {})

    cover_url = (
        image_links.get("thumbnail")
        or image_links.get("smallThumbnail")
        or ""
    )

    return cover_url.replace("http://", "https://")
