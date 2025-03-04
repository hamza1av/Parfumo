import os
import json
import queries.douglas_query as dq
import time

SOURCE_DIR = "queries/brands_urls"
OUTPUT_DIR = "queries/brands_prices"


# Assume this function is already implemented and available
def fetch_and_extract(url: str) -> dict:
    """Fetches the HTML content from a URL and extracts relevant data."""
    time.sleep(1)
    html = dq.fetch_douglas_page(url)
    result = dq.extract_douglas_prices(html)
    return result

def process_json_files(source_dir: str, output_dir: str):
    """Reads JSON files from source_dir, processes the URLs, and writes output to output_dir."""
    os.makedirs(output_dir, exist_ok=True)

    input_files = os.listdir(source_dir)
    done_files = os.listdir(output_dir)
    files = list(set(input_files) - set(done_files))
    total_files = len(files)

    for file_idx, filename in enumerate(files, start=1):
        if filename.endswith(".json"):
            source_path = os.path.join(source_dir, filename)
            output_path = os.path.join(output_dir, filename)

            with open(source_path, "r", encoding="utf-8") as f:
                try:
                    urls = list(set(json.load(f)))
                    total_urls = len(urls)
                    print(f'processing {filename}')
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {filename}")
                    continue

            results = []
            for url_idx, url in enumerate(urls, start=1):
                try:
                    extracted_data = fetch_and_extract(url)
                    results.append(extracted_data)
                    print(f'[{file_idx}|{total_files}] [{url_idx}|{total_urls}] processing: {url}')
                except Exception as e:
                    print(f"Error processing {url}: {e}")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

            print(f"Processed {filename} -> {output_path}")
if __name__ == "__main__":
    process_json_files(SOURCE_DIR, OUTPUT_DIR)
