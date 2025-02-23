import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import subprocess
import time
import concurrent.futures
import argparse
import os
# import random

class ParfumoScraper:
    def __init__(self):
        return

    def get_classification_pie(self, referrer):
        curl_command = [
            "curl", "-X", "POST", "https://www.parfumo.de/action/perfume/get_classification_pie.php",
            "-H", "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
            "-H", "Cookie: PHPSESSID=h1ug0djf4v2603la1ai6t8ic1e; _ga=GA1.1.297718056.1739031516; _sp_su=false; _sp_enable_dfp_personalized_ads=true; euconsent-v2=CQMgjEAQMgjEAAGABCENBbFsAP_gAAAAAAYgIzAB5C7cTWFhcHhXAaMAaIwc1xABJkAAAhKAAaABSBIAcIQEkiACMAyAAAACAAAAIABAAAAgAABAAQAAAIgAAAAEAAAEAAAIICAEAAERQgAACAAICAAAAQAIAAABAgEAiACAQQKERFgAgIAgBAAAAIAgAIABAgMAAAAAAAAAAAAAAgAAgQAAAAAAAAACABAAAAeEgNAALAAqABwADwAIIAZABqADwAIgATAA3gB-AEJAIYAiQBHACaAGGAO6AfgB-gG0AUeAvMBkgDLgGsANzAgmEAEgAkACOAH8Ac4BKQCdgI9AXUAyEQABABIKAAgI9GAAQEejoDoACwAKgAcABBADIANQAeABEACYAF0AMQAbwA_QCGAIkATQAw4B-AH6ARYAjoBtAEXgJkAUeAvMBkkDLAMuAaaA1gBxYEARwBAAC4AJAAjgBQAD-AI6AcgBzgDuAIQASkAnYCPQExALqAZCA3MhAIAAWADUAMQAbwBHADuAJSAbQgAFAD_AOQA5wEegJiAiySgHgALAA4ADwAIgATAAxQCGAIkARwA_AEXgKPAXmAyQBrAEASQAcAC4ARwB3AHbAR6AmIBlhSAsAAsACoAHAAQQAyADQAHgARAAmABSADEAH6AQwBEwD8AP0AiwBHQDaAIvAXmAySBlgGXANYAgmUAJAAKAAuACQAI4AWwA2gCOgHIAc4A7gCUgF1ANeAdsBHoCYgFZANzAiyWgBAA1AHcWABAI9ATE.YAAAAAAAAAAA; consentUUID=1d2e9edf-2585-4ab3-9484-05914090a08d_40; consentDate=2025-02-08T16:18:39.046Z; uniqueUser=e4d729908c0c5217dd4073f78b9f6805c2d283c97809576dda6c2b21d2151d5c; _ga_DVZQF4Y622=GS1.1.1739482214.5.1.1739482214.0.0.0"
            "-H", "DNT: 1",
            "-H", "Origin: https://www.parfumo.de",
            "-H", f"Referer: {referrer}",
            "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "--data-urlencode", f"p={self.p}",
            "--data-urlencode", f"h={self.h_pie}",
            "--data-urlencode", f"csrf_key={self.csrf_token}",
            "--write-out", "HTTP Status: %{http_code}",
            "--silent", "--show-error"
        ]

        result = subprocess.run(curl_command, capture_output=True, text=True)
        response_body, _, status_code = result.stdout.rpartition("HTTP Status: ")

        self.classification_response_body = response_body.strip()
        self.classification_status_code = status_code.strip()

    def get_classification_pie_req(self, referrer):

        url = "https://www.parfumo.de/action/perfume/get_classification_pie.php"

        payload = {'p': self.p,
        'h': self.h_pie,
        'csrf_key': self.csrf_token}
        files=[

        ]
        headers = {
        'content-type': ' application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': ' PHPSESSID=h1ug0djf4v2603la1ai6t8ic1e; _ga=GA1.1.297718056.1739031516; _sp_su=false; _sp_enable_dfp_personalized_ads=true; euconsent-v2=CQMgjEAQMgjEAAGABCENBbFsAP_gAAAAAAYgIzAB5C7cTWFhcHhXAaMAaIwc1xABJkAAAhKAAaABSBIAcIQEkiACMAyAAAACAAAAIABAAAAgAABAAQAAAIgAAAAEAAAEAAAIICAEAAERQgAACAAICAAAAQAIAAABAgEAiACAQQKERFgAgIAgBAAAAIAgAIABAgMAAAAAAAAAAAAAAgAAgQAAAAAAAAACABAAAAeEgNAALAAqABwADwAIIAZABqADwAIgATAA3gB-AEJAIYAiQBHACaAGGAO6AfgB-gG0AUeAvMBkgDLgGsANzAgmEAEgAkACOAH8Ac4BKQCdgI9AXUAyEQABABIKAAgI9GAAQEejoDoACwAKgAcABBADIANQAeABEACYAF0AMQAbwA_QCGAIkATQAw4B-AH6ARYAjoBtAEXgJkAUeAvMBkkDLAMuAaaA1gBxYEARwBAAC4AJAAjgBQAD-AI6AcgBzgDuAIQASkAnYCPQExALqAZCA3MhAIAAWADUAMQAbwBHADuAJSAbQgAFAD_AOQA5wEegJiAiySgHgALAA4ADwAIgATAAxQCGAIkARwA_AEXgKPAXmAyQBrAEASQAcAC4ARwB3AHbAR6AmIBlhSAsAAsACoAHAAQQAyADQAHgARAAmABSADEAH6AQwBEwD8AP0AiwBHQDaAIvAXmAySBlgGXANYAgmUAJAAKAAuACQAI4AWwA2gCOgHIAc4A7gCUgF1ANeAdsBHoCYgFZANzAiyWgBAA1AHcWABAI9ATE.YAAAAAAAAAAA; consentUUID=1d2e9edf-2585-4ab3-9484-05914090a08d_40; consentDate=2025-02-08T16:18:39.046Z; uniqueUser=e4d729908c0c5217dd4073f78b9f6805c2d283c97809576dda6c2b21d2151d5c; _ga_DVZQF4Y622=GS1.1.1739482214.5.1.1739482214.0.0.0; PHPSESSID=m1tlk8lfac5kmoqjtb2j2j4kor',
        'dnt': ' 1',
        'origin': ' https://www.parfumo.de',
        'referer': f'{referrer}',
        'sec-ch-ua': ' "Chromium";v="133", "Not(A:Brand";v="99"',
        'sec-ch-ua-mobile': ' ?0',
        'sec-ch-ua-platform': ' "macOS"',
        'sec-fetch-dest': ' empty',
        'sec-fetch-mode': ' cors',
        'sec-fetch-site': ' same-origin',
        'user-agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'x-requested-with': ' XMLHttpRequest',
        'cache-control': ' no-cache',
        'pragma': ' no-cache'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        self.classification_response_body = response.text()
        self.classification_status_code = response.status_code()

    def get_ratings_details_request(self, referrer, type):
        url = "https://www.parfumo.de/action/_get_ratings_details.php"

        payload = {'type': type,
        'p_id': self.p,
        'dist': self.dist_token_dic[type],
        'csrf_key': self.csrf_token,
        'h': self.h_ratings}
        files=[

        ]
        headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'PHPSESSID=h1ug0djf4v2603la1ai6t8ic1e; _ga=GA1.1.297718056.1739031516; _sp_su=false; _sp_enable_dfp_personalized_ads=true; euconsent-v2=CQMgjEAQMgjEAAGABCENBbFsAP_gAAAAAAYgIzAB5C7cTWFhcHhXAaMAaIwc1xABJkAAAhKAAaABSBIAcIQEkiACMAyAAAACAAAAIABAAAAgAABAAQAAAIgAAAAEAAAEAAAIICAEAAERQgAACAAICAAAAQAIAAABAgEAi ACAQQKERFgAgIAgBAAAAIAgAIABAgMAAAAAAAAAAAAAAgAAgQAAAAAAAAACABAAAAeEgNAALAAqABwADwAIIAZABqADwAIgATAA3gB-AEJAIYAiQBHACaAGGAO6AfgB-gG0AUeAvMBkgDLgGsANzAgmEAEgAkACOAH8Ac4BKQCdgI9AXUAyEQABABIKAAgI9GAAQEejoDoACwAKgAcABBADIANQAeABEACYAF0AMQAbwA_QCGAIkATQAw4B-AH6ARYAjoBtAEXgJkAUeAvMBkkDLAMuAaaA1gBxYEARwBAAC4AJAAjgBQAD-AI6AcgBzgDuAIQASkAnYCPQExALqAZCA3MhAIAAWADUAMQAbwBHADuAJSAbQgAFAD_AOQA5wEegJiAiySgHgALAA4ADwAIgATAAxQCGAIkARwA_AEXgKPAXmAyQBrAEASQAcAC4ARwB3AHbAR6AmIBlhSAsAAsACoAHAAQQAyADQAHgARAAmABSADEAH6AQwBEwD8AP0AiwBHQDaAIvAXmAySBlgGXANYAgmUAJAAKAAuACQAI4AWwA2gCOgHIAc4A7gCUgF1ANeAdsBHoCYgFZANzAiyWgBAA1AHcWABAI9ATE.YAAAAAAAAAAA; consentUUID=1d2e9edf-2585-4ab3-9484-05914090a08d_40; consentDate=2025-02-08T16:18:39.046Z; uniqueUser=e4d729908c0c5217dd4073f78b9f6805c2d283c97809576dda6c2b21d2151d5c; _ga_DVZQF4Y622=GS1.1.1739570633.10.1.1739572293.0.0.0; PHPSESSID=m1tlk8lfac5kmoqjtb2j2j4kor',
        'dnt': '1',
        'origin': 'https://www.parfumo.de',
        'referer': referrer,
        'sec-ch-ua': '"Chromium";v="133", "Not(A:Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files) 
        return response.text, response.status_code
    
    def get_classification_dict(self):
        # Regex pattern to extract chart data
        pattern = re.compile(r'chart(\d+)\.data\s*=\s*(\[.*?\]);', re.DOTALL)

        # Dictionary to store parsed data
        charts_dict = {}

        # Extract matches
        for match in pattern.finditer(self.classification_response_body):
            chart_number = match.group(1)
            chart_data = json.loads(match.group(2))  # Convert JSON string to Python object
            
            if chart_number == "1":
                # Separate "Herren" & "Damen" and "Klassisch" & "Modern"
                group1 = ["Herren", "Damen"]
                group2 = ["Klassisch", "Modern"]
                
                total1 = sum(int(item["votes"]) for item in chart_data if item["ct_name"] in group1)
                total2 = sum(int(item["votes"]) for item in chart_data if item["ct_name"] in group2)

                for item in chart_data:
                    if item["ct_name"] in group1:
                        charts_dict[item["ct_name"]] = round((int(item["votes"]) / total1) * 100, 2)
                    elif item["ct_name"] in group2:
                        charts_dict[item["ct_name"]] = round((int(item["votes"]) / total2) * 100, 2)
            
            else:
                # Compute the total votes for normalization
                total_votes = sum(int(item["votes"]) for item in chart_data)
                
                # Convert to relative percentages
                for item in chart_data:
                    charts_dict[item["ct_name"]] = round((int(item["votes"]) / total_votes) * 100, 2)  # Round to 2 decimals
        
        return charts_dict

    def get_tokens(self):

        p = re.search(r"getClassificationChart\('([^']+)',(\d+),'([^']+)'\)", self.main_html).group(2)
        h_pie = re.search(r"getClassificationChart\('([^']+)',(\d+),'([^']+)'\)", self.main_html).group(3)
        csrf_token = re.search(r"csrf_key:'(.*?)'", self.main_html).group(1)

        matches = re.findall(r'data-type=\"([^\"]+)\"[^>]+data-voting_distribution=\"([^\"]+)\"', self.main_html)
        dic = {}
        for pair in matches:
            dic[pair[0]] = pair[1]

        match = re.findall(r'data-h="([^"]+)"', self.main_html)
        if match:
            h_ratings = match[1]
        else:
            print(r"data-h that is needed for the 'get_ratings_details.php' request not found")

        self.dist_token_dic = dic
        self.h_ratings = h_ratings
        self.p, self.h_pie, self.csrf_token = p, h_pie, csrf_token

    
    def get_base_response(self, url):
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "dnt": "1",
            "origin": "https://www.parfumo.de",
            "referer": f"{url}",
            "sec-ch-ua": '"Chromium";v="133", "Not(A:Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "cookie": "PHPSESSID=h1ug0djf4v2603la1ai6t8ic1e; _ga=GA1.1.297718056.1739031516; _sp_su=false; _sp_enable_dfp_personalized_ads=true; euconsent-v2=CQMgjEAQMgjEAAGABCENBbFsAP_gAAAAAAYgIzAB5C7cTWFhcHhXAaMAaIwc1xABJkAAAhKAAaABSBIAcIQEkiACMAyAAAACAAAAIABAAAAgAABAAQAAAIgAAAAEAAAEAAAIICAEAAERQgAACAAICAAAAQAIAAABAgEAiACAQQKERFgAgIAgBAAAAIAgAIABAgMAAAAAAAAAAAAAAgAAgQAAAAAAAAACABAAAAeEgNAALAAqABwADwAIIAZABqADwAIgATAA3gB-AEJAIYAiQBHACaAGGAO6AfgB-gG0AUeAvMBkgDLgGsANzAgmEAEgAkACOAH8Ac4BKQCdgI9AXUAyEQABABIKAAgI9GAAQEejoDoACwAKgAcABBADIANQAeABEACYAF0AMQAbwA_QCGAIkATQAw4B-AH6ARYAjoBtAEXgJkAUeAvMBkkDLAMuAaaA1gBxYEARwBAAC4AJAAjgBQAD-AI6AcgBzgDuAIQASkAnYCPQExALqAZCA3MhAIAAWADUAMQAbwBHADuAJSAbQgAFAD_AOQA5wEegJiAiySgHgALAA4ADwAIgATAAxQCGAIkARwA_AEXgKPAXmAyQBrAEASQAcAC4ARwB3AHbAR6AmIBlhSAsAAsACoAHAAQQAyADQAHgARAAmABSADEAH6AQwBEwD8AP0AiwBHQDaAIvAXmAySBlgGXANYAgmUAJAAKAAuACQAI4AWwA2gCOgHIAc4A7gCUgF1ANeAdsBHoCYgFZANzAiyWgBAA1AHcWABAI9ATE.YAAAAAAAAAAA; consentUUID=1d2e9edf-2585-4ab3-9484-05914090a08d_40; consentDate=2025-02-08T16:18:39.046Z; uniqueUser=e4d729908c0c5217dd4073f78b9f6805c2d283c97809576dda6c2b21d2151d5c; _ga_DVZQF4Y622=GS1.1.1739490354.7.1.1739490554.0.0.0",
            "cache-control": "no-cache",
            "pragma": "no-cache"
        }

        self.main_response = requests.get(url=url, headers=headers)
        # return response

    def get_soup(self, url):
        """Make request and return BeautifulSoup object"""
        try:
            self.get_base_response(url)
            self.main_html = self.main_response.text
            return BeautifulSoup(self.main_html, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_basic_info(self, soup):
        """Extract basic perfume information"""
        if not soup:
            return {}
            
        try:
            collection_element = soup.select_one("div.text-sm.grey.upper.mb-0-5")
            name_element = soup.select_one("h1.p_name_h1")
            brand_element = soup.select_one("span.p_brand_name span[itemprop='name']")
            year_element = soup.select_one("span.label_a")
            flakon_designer_element = soup.find("div", class_="text-xs lightgrey pt-1 pb-1")
            perfumer_element = soup.select_one("div.w-100.mt-0-5.mb-3 a")

            
            return {
                "name": name_element.text.strip().split("  ")[0] if name_element else None,
                "brand": brand_element.text.strip() if brand_element else None,
                "year": int(year_element.text.strip()) if year_element else None,
                "collection": collection_element.text.strip() if collection_element else None,
                "flakon_designer": flakon_designer_element.text.strip().removeprefix("Flakondesign  ") if flakon_designer_element else None,
                "perfumer": perfumer_element.text.strip() if perfumer_element else None
            }
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            return {}


    def extract_scent_notes(self, soup, category_class):
        """Extract scent notes for a specific category"""
        if not soup:
            return []
            
        try:
            category_block = soup.find(class_=category_class)
            if category_block:
                scent_note_elements = category_block.select('span.clickable_note_img span.nowrap.pointer')
                return [element.text.strip() for element in scent_note_elements if element.text.strip()]
            return []
        except Exception as e:
            print(f"Error extracting {category_class} notes: {e}")
            return []

    def get_scent_strength(self, soup):
        """Extract scent strength information"""
        if not soup:
            return {}
            
        try:
            scent_data = {}
            containers = soup.select(".s-circle-container")
            
            for container in containers:
                try:
                    scent_name = container.select_one(".text-xs.grey").text.strip()
                    circle = container.select_one(".s-circle")
                    if circle:
                        size_classes = [cls for cls in circle['class'] if "s-circle_" in cls]
                        if size_classes:
                            size = size_classes[0].split("_")[-1]
                            scent_data[scent_name] = size
                except Exception:
                    continue
                    
            return scent_data
        except Exception as e:
            print(f"Error extracting scent strength: {e}")
            return {}

    def get_ratings(self, soup):
        """Extract detailed ratings information"""
        if not soup:
            return {}
            
        try:
            detailed_ratings = {}
            rating_elements = soup.select(".barfiller_element")

            for element in rating_elements:
                try:
                    category = element.select_one(".text-xs.upper.grey").text.strip()
                    rating_value = element.select_one(".text-lg.bold").text.strip()
                    num_ratings_element = element.select_one(".lightgrey.text-2xs.upper")
                    num_ratings = num_ratings_element.text.strip().split()[0] if num_ratings_element else None

                    detailed_ratings[category] = {
                        "rating": float(rating_value),
                        "number_of_ratings": int(num_ratings),
                    }
                except Exception as e:
                    print(f"Error extracting ratings for category {category}: {e}")
                    continue

            return detailed_ratings
        except Exception as e:
            print(f"Error extracting detailed ratings: {e}")
            return {}

    def get_rating_details(self, referrer, type):
        try:
            response_string, reponse_status = self.get_ratings_details_request(referrer, type) 
            response_dict = json.loads(response_string)
            return response_dict["dist"]
        except:
            return None


    def scrape_perfume(self, url):
        """Scrape all information for a single perfume"""
        try:
            print(f"\nScraping: {url}")
            self.get_base_response(url)
            time.sleep(1)
            
            # Get main page
            main_soup = self.get_soup(url)
            if not main_soup:
                return None

            self.get_tokens()

            # Extract data from main page
            basic_info = self.get_basic_info(main_soup)
            detailed_ratings = {
                "scent": self.get_rating_details(url, type="scent"),
                "durability": self.get_rating_details(url, type="durability"),
                "sillage": self.get_rating_details(url, type="sillage"),
                "bottle": self.get_rating_details(url, type="bottle"),
                "pricing": self.get_rating_details(url, type="pricing")
            }
            ratings = self.get_ratings(main_soup)
            # scent_strength = self.get_scent_strength(main_soup)
            top_notes = self.extract_scent_notes(main_soup, 'nb_t')
            middle_notes = self.extract_scent_notes(main_soup, 'nb_m')
            base_notes = self.extract_scent_notes(main_soup, 'nb_b')

            # Get all notes if structured notes fail
            all_notes = None
            if not (top_notes or middle_notes or base_notes):
                all_notes = [el.text.strip() for el in main_soup.select('span.clickable_note_img span.nowrap.pointer') if el.text.strip()]

            self.get_classification_pie(referrer = url)

            try:
                scent_types = self.get_classification_dict() 
            except:
                scent_types = {}

            time.sleep(1)

            return {
                **basic_info,
                "ratings": ratings,
                "detailed_ratings": detailed_ratings,
                # "scent_strength": scent_strength,
                "top_notes": top_notes if top_notes else None,
                "middle_notes": middle_notes if middle_notes else None,
                "base_notes": base_notes if base_notes else None,
                "all_notes": all_notes,
                "scent_types": scent_types,
                "url": url
            }

        except Exception as e:
            print(f"Error scraping perfume {url}: {e}")
            return None

    # def scrape_all_perfumes(self):
    #     """Scrape all perfumes with chunking support"""
    #     results = []
    #     try:
    #         with open(self.links_file, 'r') as file:
    #             links = json.load(file)
            
    #         chunk_size = len(links) // 8
    #         chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]
            
    #         while True:
    #             try:
    #                 # index = int(input("Enter an index between 1 and 8: "))
    #                 index = 1
    #                 if 1 <= index <= 8:
    #                     break
    #                 print("Index must be between 1 and 8.")
    #             except ValueError:
    #                 print("Please enter a valid integer.")
            
    #         selected_chunk = chunks[index - 1]
    #         for i, link in enumerate(selected_chunk, 1):
    #             print(f"\nProcessing perfume {i} of {len(selected_chunk)}")
    #             perfume_data = self.scrape_perfume(link)
    #             if perfume_data:
    #                 results.append(perfume_data)
    #                 self.save_results(results, f'perfumes_data_partial_chunk_{index}.json')
    #             # time.sleep(2)
    #             if i == 3:
    #                 break
                    
    #         return results
    #     except Exception as e:
    #         print(f"Error scraping all perfumes: {e}")
    #         return results

    def scrape_chunk(self, chunk, index):
        """Scrape a single chunk of perfumes."""
        results = []
        print(f"Starting chunk {index} with {len(chunk)} perfumes...")

        for i, link in enumerate(chunk, 1):
            print(f"\n[Chunk {index}] Processing perfume {i} of {len(chunk)}")
            perfume_data = self.scrape_perfume(link)
            if perfume_data:
                results.append(perfume_data)
                # self.save_results(results, f'perfumes_data_partial_chunk_{index}.json')
            else:
                break

        return results

    def scrape_all_perfumes(self, num_chunks):
        """Scrape all perfumes in parallel across 8 chunks."""
        results = []
        try:
            # get relevant links
            with open(self.links_file, 'r') as file:
                links = json.load(file)
            
            links = self.get_list2scrape()

            chunk_size = len(links) // num_chunks
            chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_chunks) as executor:
                futures = {executor.submit(self.scrape_chunk, chunks[i], i + 1): i for i in range(len(chunks))}

                for future in concurrent.futures.as_completed(futures):
                    try:
                        results.extend(future.result())
                    except Exception as e:
                        print(f"Error in chunk {futures[future] + 1}: {e}")

            return results
        except Exception as e:
            print(f"Error scraping all perfumes: {e}")
            return results

    def get_list2scrape(self):
        with open(self.links_file, 'r') as f:
            input_list = json.load(f)
        with open(self.output_file, 'r') as f:
            compare_list = json.load(f)

        compare_list = [element['url'] for element in compare_list]
        diff = list(set(input_list) - set(compare_list))
        return diff[:self.num_elements2scrape] if len(diff) > self.num_elements2scrape else diff

    # def save_results(self, results):
    #     """Save results to JSON file"""
    #     # try:
    #     #     with open(self.output_file, 'w', encoding='utf-8') as f:
    #     #         json.dump(results, f, ensure_ascii=False, indent=2)
    #     #     print(f"Results saved to {self.output_file}")
    #     # except Exception as e:
    #     #     print(f"Error saving results: {e}")

    #     with open(self.output_file, "r+", encoding="utf-8") as file:
    #         file.seek(0, 2)  # Move to the end of the file
    #         position = file.tell()
            
    #         if position > 2:  # If file is not empty, remove the last ']'
    #             file.seek(position - 2)
    #             file.truncate()
    #             file.write(",\n" + json.dumps(results, indent=4)[1:])  # Append new items
    #         else:
    #             file.write(json.dumps(results, indent=4)) 

    def save_results(self, results):
        """Save results to JSON file without adding trailing commas"""

        if not os.path.exists(self.output_file):  # Handle case where file doesn't exist
            with open(self.output_file, "w", encoding="utf-8") as file:
                json.dump([results], file, indent=4)
            return

        try:
            with open(self.output_file, "r+", encoding="utf-8") as file:
                try:
                    data = json.load(file)  # Load existing JSON data
                    if not isinstance(data, list):  # Ensure it's a list
                        print(f"Error: Expected a list in {self.output_file}, but found {type(data).__name__}.")
                        return  # Don't write anything if the structure is invalid
                except json.JSONDecodeError:
                    print(f"Error: Corrupted JSON file {self.output_file}. Skipping save.")
                    return  # Exit without modifying the file

                if results not in data:  # Prevent duplicate entries
                    data.append(results)
                    file.seek(0)  # Move to the start of the file
                    json.dump(data, file, indent=4)  # Overwrite with updated list
                    file.truncate()  # Ensure old content is removed

        except Exception as e:
            print(f"Error saving results: {e}")


    def get_proxies(self):
        return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_chunks", type=int, default=1)    
    parser.add_argument("--input", "-i", type=str, default="links.json")    
    parser.add_argument("--output", "-o", type=str, default='completed_perfumes.json')    
    parser.add_argument("--num_elements", "-n", type=int, default=250)    
    parser.add_argument("--proxies", "-p", type=str, default='valid_proxies.txt')    

    args = parser.parse_args()

    scraper = ParfumoScraper()
    scraper.links_file = args.input
    scraper.output_file = args.output
    scraper.num_elements2scrape = args.num_elements
    scraper.proxies = [line.strip() for line in open(args.proxies) if line.strip()]

    try:
        results = scraper.scrape_all_perfumes(num_chunks=args.num_chunks)
        scraper.save_results(results)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

