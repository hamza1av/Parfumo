from bs4 import BeautifulSoup
import json

# Read the HTML file
with open("brand_keys.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Extract brand names and URLs
brands = {}
for link in soup.find_all("a", class_="facet-option"):
    brand_name = link.find("div", class_="facet-option__label").get_text(strip=True)
    brand_url = link.get("href")
    if brand_name and brand_url:
        brands[brand_name] = brand_url

# Save to a JSON file
with open("brands.json", "w", encoding="utf-8") as json_file:
    json.dump(brands, json_file, ensure_ascii=False, indent=4)

print("Extraction complete. Data saved to brands.json.")
