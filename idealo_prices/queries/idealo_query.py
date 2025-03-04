import requests
import re

def get_url(query):
    url = f"https://www.idealo.de/suggest?q={query}&max=10"

    payload = {}
    headers = {
      'Host': 'www.idealo.de',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Referer': 'https://www.idealo.de/',
      'Sec-GPC': '1',
      'Connection': 'keep-alive',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'Priority': 'u=0',
      'TE': 'trailers'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    first_element = response.json()
    if first_element['groups'][0]["items"][0]:
        first_element = first_element['groups'][0]["items"][0]
        return first_element["url"]
    else:
        return None

def get_price(product_id, referrer):
    url = f"https://www.idealo.de/price-chart/sites/1/products/{product_id}/history"

    payload = {}
    headers = {
      'Host': 'www.idealo.de',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0',
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Sec-GPC': '1',
      'Connection': 'keep-alive',
      'Referer': referrer,
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'TE': 'trailers'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response


def make_request(query):
    url = get_url(query)

    if url:

        match = re.search(r"/(\d+)_-", url)

        if match:
            product_id = match.group(1)  # Extract the first captured group

        resp = get_price(product_id, url)
        return resp.json()['statistics']['avgPrice']
    else:
        return None

if __name__ == '__main__':

    price = make_request('Jean Paul Gaultier Le Male Elixir 100 ml')

    print(price)
