import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Any
import os
from tqdm import tqdm


def get_max_page(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")

    # Find all <a> tags with "href" attributes containing "current_page="
    page_links = soup.find_all("a", href=re.compile(r"current_page=\d+"))

    # Extract numbers from the href attributes
    page_numbers = []
    for link in page_links:
        match = re.search(r"current_page=(\d+)", link["href"])
        if match:
            page_numbers.append(int(match.group(1)))

    # Return the highest page number found
    return max(page_numbers) if page_numbers else None

def get_links_from_brand(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True) if "Parfums" in a["href"]]
    return links


def append_unique_to_json(file_path: str, new_data: List[Any]) -> None:
    """Appends unique items from new_data to a JSON file without overriding existing entries."""
    
    # Check if file exists; if not, create an empty list
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
                if not isinstance(existing_data, list):
                    raise ValueError("JSON file must contain a list")
            except (json.JSONDecodeError, ValueError):
                existing_data = []
    else:
        existing_data = []

    # Add only unique elements
    unique_data = [item for item in new_data if item not in existing_data]
    
    if unique_data:
        existing_data.extend(unique_data)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4)


headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

def get_list2scrape(input, compare):
    with open(input, 'r') as f:
        input_list = json.load(f)
    with open(compare, 'r') as f:
        compare_list = json.load(f)

    diff = list(set(input_list) - set(compare_list))

    return input_list, compare_list, diff


_, _, brands_list = get_list2scrape("brands.json", "done_brands.json")

for brand_url in tqdm(brands_list, desc="Processing Brands", position=0, leave=True):

    response = requests.get(brand_url, headers=headers)
    if response.status_code == 200:
        max_page = get_max_page(html=response.text)


        valid_links = get_links_from_brand(response.text)

        if max_page == None:
            extracted_links = get_links_from_brand(response.text)

        elif max_page > 1:
            for i in tqdm(range(2, max_page + 1), desc="Fetching Pages", position=1, leave=False):
                curr_url = brand_url + f'/current_page={i}'
                new_response = requests.get(curr_url, headers=headers)
                if new_response.status_code == 200:
                    extracted_links = get_links_from_brand(new_response.text)
                    valid_links.append(extracted_links)
                else:
                    break
    
        append_unique_to_json(file_path='done_brands.json', new_data = [brand_url])
        append_unique_to_json(file_path='extended_perfumes_links.json', new_data=valid_links)
    else:
        break
    