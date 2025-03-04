import requests
import json
import time
import os

def make_request(curr_page, brand_code):
    url = f"https://www.douglas.de/jsapi/v2/products/search/category/01?currentPage={curr_page}&fields=FULL&isApp=false&isAppleDevice=false&isCriteoConsent=false&isCriteoEnabled=true&isMobile=true&isOwnBrandEnabled=false&isSSR=false&pageSize=129&query=:relevance:brand:{brand_code}"

    payload = {}
    headers = {
      'Host': 'www.douglas.de',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0',
      'Accept': 'application/json',
      'Accept-Language': 'de',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Referer': 'https://www.douglas.de/de/c/parfum/01?q=:relevance:brand:bd899&page=2',
      'content-type': 'application/json',
      'lastactive': 'false',
      'x-cc-user-id': 'anonymous',
      'x-csrf-token': 'sFN08jg0kCQ8cvrITu-qGJcvMAXvsR9yWGGlrfpPO8n',
      'Sec-GPC': '1',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Connection': 'keep-alive',
      'Priority': 'u=4',
      'TE': 'trailers'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "../brands.json")

with open(file_path, 'r') as f:
    brands = json.load(f)

for brand_name, brand_code in brands.items():
    print(f'processing {brand_name}') 
    response_code = 200
    brand_prices = {}
    curr_page = 0
    while response_code == 200:
        r = make_request(curr_page, brand_code)
        time.sleep(1)
        if r.status_code == 200:
            brand_prices[f'page_{curr_page}'] = r.json()
        response_code = r.status_code
        curr_page += 1

    with open(f'brands_data/{brand_name}.json', 'w') as f:
        json.dump(brand_prices, f, indent=4)


