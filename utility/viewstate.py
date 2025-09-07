from bs4 import BeautifulSoup
from requests import Session, Response
from typing import Dict
import logging

search_url = "https://applications.fairtrading.nsw.gov.au/assocregister/default.aspx"

session = Session()

def get_viewstate_fields(search_url: str = search_url) -> Dict[str, str]:
    try:
        page: Response = session.get(search_url)
        page.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch viewstate fields: {e}")
        return {}

    soup = BeautifulSoup(page.text, "html.parser")

    def safe_extract(field_id: str) -> str:
        tag = soup.find(id=field_id)
        # Ensure tag is a Tag, not a NavigableString
        from bs4.element import Tag
        if isinstance(tag, Tag) and "value" in tag.attrs:
            value = tag["value"]
            return str(value) if value is not None else ""
        return ""

    return {
        "__VIEWSTATE": safe_extract("__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": safe_extract("__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": safe_extract("__EVENTVALIDATION")
    }