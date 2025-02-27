import numpy as np
best_of_liste = []

years = np.arange(2012,2026,1)
genders = ['Herren', 'Damen', 'Unisex']

baseline_url = 'https://www.parfumo.de/Parfums/Tops/'

for year in years:
    for gender in genders:
        best_of_url = baseline_url + gender + '/' + str(year)
        best_of_liste.append(best_of_url)
        # print(best_of_url)


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1920x1080")

# Start WebDriver
driver = webdriver.Chrome(options=chrome_options)

all_perfumes_list = []
for url in best_of_liste:
    driver.get(url)  # Replace with your target URL

    # print(driver.page_source)

# Wait until at least one link appears
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a"))
    )

# # Extract all matching <a> links dynamically
# for i in range(1, 10):  # Adjust based on the expected number of elements
#     try:
#         xpath = f"/html/body/div[4]/div/div[1]/div[6]/div[2]/div[{i}]/div[2]/a"
#         element = driver.find_element(By.XPATH, xpath)
#         print(element.get_attribute("href"))
#     except:
#         continue  # Skip if the element is not found

    links = driver.find_elements(By.XPATH, "/html/body/div[4]/div/div[1]/div[6]/div[2]/div[*]/div[2]/a")
    for link in links:
        all_perfumes_list.append(link.get_attribute("href"))
        print(link.get_attribute("href"))

# Quit driver
driver.quit()

import json
with open("links.json", "w") as file:
    json.dump(all_perfumes_list, file, indent=4)  # indent=4 makes it readable
