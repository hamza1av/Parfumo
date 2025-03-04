from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
import re

def get_first_relevant_link(query: str, url_prefix: str) -> str | None:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=50)  # Fetch up to 10 results

    for result in results:
        url = result.get("href") or result.get("url")  # Handle possible key variations
        if url and url.startswith(url_prefix):
            return url

    return None  # Return None if no matching link is found

def extract_douglas_prices(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    size_price_dict = {}

    for variant in soup.find_all("div", class_="product-detail__variant"):
        size_element = variant.find("div", class_="product-detail__variant-name")
        price_element = variant.find("span", class_="product-price__price")

        if size_element and price_element:
            size = size_element.get_text(strip=True)
            price = price_element.get_text(strip=True).replace("\u00a0", " ")  # Replace non-breaking spaces
            size_price_dict[size] = price

    return size_price_dict

def extract_flaconi_prices(html):
    soup = BeautifulSoup(html, "html.parser")
    prices = {}

    for label in soup.find_all("label", {"data-product-sku": True}):
        # Extract size
        size_span = label.select_one("[data-qa-block='product_variant_quantity'] span")
        unit_span = label.select_one("[data-qa-block='product_variant_quantity'] .ProductTitlestyle__Unit-sc-1l1zzjt-2")
        
        if size_span and unit_span:
            size = f"{size_span.text.strip()} {unit_span.text.strip()}"
        else:
            continue

        # Extract UVP price
        uvp_label = label.select_one("[data-qa-block='variant_discount'] label")
        if uvp_label:
            price_text = uvp_label.text.replace("UVP €", "").strip().replace(",", ".")
        else:
            # Fall back to normal price if UVP is not found
            price_span = label.select_one("[data-qa-block='product_variant_price']")
            if price_span:
                price_text = price_span.text.replace("€", "").strip().replace(",", ".")
            else:
                continue

        # Convert price to float
        price = float(re.sub(r"[^\d.]", "", price_text))
        prices[size] = price

    return prices

def fetch_douglas_page(url):
    headers = {
        "Host": "www.douglas.de",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Sec-GPC": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive"
    }
        # "Cookie": "_abck=11DDF2720A6ADC99C2E572E46C3F0009~0~YAAQOVITAuJvZEmVAQAAmxajXA2Vzya5YgnQCFFg..."  # Truncated for security
    # }

    print(url) 
    response = requests.get(url, headers=headers)
    return response.text

def fetch_flaconi_content(url: str) -> str:
    """Fetches the HTML content of a given URL."""

    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    #     "Accept-Language": "en-US,en;q=0.5",
    #     "Accept-Encoding": "gzip, deflate, br, zstd",
    #     "Sec-GPC": "1",
    #     "Upgrade-Insecure-Requests": "1",
    #     "Sec-Fetch-Dest": "document",
    #     "Sec-Fetch-Mode": "navigate",
    #     "Sec-Fetch-Site": "cross-site",
    #     "Connection": "keep-alive",
    #     "Cookie": "__cf_bm=mvMgJRFy2atrDqlzHeZ5Tw18Is.dr0BMzNwDaAQH0As-1741037532-1.0.1.1-zOCZf1NmEHXQkqsYBL7Y3JjT2m2_90SLwP0LNdUJLVAhrrbWmgS0Madf9cyDZNnL7V4p4P5FxNA5APJWxL3wYBeHNe7pReaHTbrQ.IlG5CU"
    # }

    headers = {
        'Host': 'www.flaconi.de',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Connection': 'keep-alive',
        'Priority': 'u=0, i',
        'TE': 'trailers'
    }

        # 'Cookie': 'FCSESSID0815=b372f43c090ef1780ed06ec5e48140b8; paidmktCS=psm; flaconi_criteo=criteo-flaconiOlwRjRPw91wL5heiSvjHqQiJu6J2WduMTQ7r2LEllrg6KRD4y; _sp_id.3fa7=af598c27e5135fc8.1740943884.5.1741036265.1741026596; yotpo_pixel=3194d7b6-88fd-4094-af70-0c975b04d008; cf_clearance=LQGKkSoKBT_0BZFsZAEwwN3VRJShHCAuvfWQQId5rFU-1741026529-1.2.1.1-ATivHq0xd9U0SwnICSo0EP1NC.0ciLhpwq.Rn8eZj0h1qgn8KN7Kdd5YmVgOa7z6L4gmR4_Dq4HEQ2k7pAJvolhKQVCIpPiX.Q5xQNfOQMiS6HiWCk7eCA3_z.7axWBh1UCY0wChyQ4t8AJb6fghouOJigBIe9VDtNedrtwytj5nB2DkWsWH8r9tlxNOuMd7_Rl5Xi0kKPwAmfy3cWQaZSRK6_WPT.voqqqbKQQ2bAHQjl8XhkERYB.m0lsGFQ1D1d0TCidn19CKpMLJA7K9whoD_2uYugHfXXZDYqHYrsTyM3X2__wmqjNgGCuqfZBSGNZ8DnqU9M8mhQ_zuzd0hrV4RlTgYlXah9mMzoID2pJSpdpGc1Of2RnCVZz2nm5ae9sVIsgi2q2cd3ALjZpj6JIRiI81wbEDKOHdCLgTheA; _sp_ses.3fa7=*; nr-user-session=15725657-128e-4794-a28a-02933c729f9e; __cf_bm=N3G3v.MGWuikzR2glT_GYrBbUMMisLymoJmf6e1Hhpc-1741036264-1.0.1.1-azJ431VZccrhTgjnKE_cFb143.NDSnEne4OPNwBfP_dQvG9lXkoTJANnbYKoYedc6v7TW_re3S7HVV9VHoSx63rNoriQan_DUuXLxu8Ua4k; __cf_bm=mvMgJRFy2atrDqlzHeZ5Tw18Is.dr0BMzNwDaAQH0As-1741037532-1.0.1.1-zOCZf1NmEHXQkqsYBL7Y3JjT2m2_90SLwP0LNdUJLVAhrrbWmgS0Madf9cyDZNnL7V4p4P5FxNA5APJWxL3wYBeHNe7pReaHTbrQ.IlG5CU',
        # "Cookie": "flaconi_criteo=criteo-flaconiJtiAgroGPYChvejZB2BoQIAhxjB3EC0hrTiqTFn2MPs11YQD2; FCSESSID0815=76084a77b0a81f4c304ebb35e3358290; __cf_bm=ZFm_TjmlFyko8qDxOtEYTGY8Vkp4Eep0Ogkk9ELHhRw-1741025689-1.0.1.1-aJmcvusQIGxeECmtJeO37mlH9qaQwp3LUpWTxrBGM6AspC7iHIBwl93rH4BxdwBfyE5XIAIFB5FUhxrMY2lkHCKATmz8Vk9oW51Cc1ahoRU;"  # Modify as needed
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"


if __name__ == "__main__":
    query = "Jean Paul Gaultier Le Male Elixir Douglas"
    # query: str = "Jean Paul Gaultier Le Male Elixir flaconi.de"
    url_prefix = "https://www.douglas.de/de/p"
    # url_prefix: str = "https://www.flaconi.de/parfum"


    url: str = get_first_relevant_link(query, url_prefix)
    html = fetch_douglas_page(url)
    # html: str = fetch_flaconi_content(url)
    result = extract_douglas_prices(html)
    # result: dict = extract_flaconi_prices(html)

    print(result)
