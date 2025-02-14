import requests
import json


def save_rendered_page(url, output_file="rendered_page.html"):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
        response = requests.get(url, headers=headers)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(response.text)
        
        print(f"Page saved as {output_file}")
    except KeyError as e:
        print(e)

    
# with open("links.json") as f:
#     liste = json.load(f)

# # Example usage
# for i, url in enumerate(liste):
#     save_rendered_page(url , output_file=f'save_htmls/page_{i}.html')
#     if i == 10:
#         break

url = 'https://www.fragrantica.de/Parfum/Dior/Dior-Homme-2020-58714.html'
save_rendered_page(url, output_file='fragrantica.html')
