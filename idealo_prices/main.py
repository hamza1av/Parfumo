from queries import douglas_query, idealo_query
import pandas as pd
from tqdm import tqdm
import time
import os

def process_perfume(row: pd.DataFrame) -> dict:
    query: str = row['name'] + ' ' + row['brand'] + ' '
    price_dict = {}

    d_url_prefix = 'https://www.douglas.de/de/p'
    d_query = query + 'Douglas'
    d_url = douglas_query.get_first_relevant_link(query, d_url_prefix)
    d_html = douglas_query.fetch_douglas_page(d_url)
    
    price_dict['douglas'] = douglas_query.extract_douglas_prices(d_html)

    for key, item in price_dict['douglas'].items():
        
        i_query = query + ' ' + key
        price_dict['idealo'][key] = idealo_query.make_request(query=i_query)

    return price_dict

if __name__ == "__main__":

    # file_path = os.path.join(os.getcwd(), "perfumes_price.csv")  # Get absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "perfumes_price.csv")
    df = pd.read_csv(file_path)
    sorted_df = df.sort_values(by='Duft.number_of_ratings', ascending=False) 

    # df["Price"] = df["Price"].apply(lambda x: process_perfume(df.loc[df["Price"] == x].iloc[0]) if x is None else x)
    if "price" not in sorted_df.columns:
        sorted_df["price"] = None

    results = []
    # Iterate with progress bar (tqdm)
    for i, row in tqdm(sorted_df.iterrows(), total=len(df), desc="Fetching Data"):
        if pd.isna(row["price"]):  # Skip already processed entries
            result = process_perfume(row)
            time.sleep(1)  # Optional: Prevent API rate limit issues
        else:
            result = row["price"]  # Keep existing data

        results.append(result)

    sorted_df["price"] = results

    sorted_df.to_csv('perfumes_price.csv')