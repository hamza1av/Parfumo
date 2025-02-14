import requests

def crawl_url(url, status=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if status == True:
        return response.status_code
    else:
        with open('test.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        return response.content
        

url = r'https://www.parfumo.de/Parfums/Dior/Sauvage_Eau_de_Toilette'
crawl_url(url)

