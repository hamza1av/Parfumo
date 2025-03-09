# Example usage of the enhanced perfume price scraper
import pandas as pd
from idealo_scraper import PerfumePriceScraper

# Sample dataset
data = {
    'perfume_name': ['XerJoff', 'Sauvage', 'Black Opium', 'Coco Mademoiselle', 'Aventus'],
    'brand': ['40 Knots', 'Dior', 'Yves Saint Laurent', 'Chanel', 'Creed'],
    'id': [1001, 1002, 1003, 1004, 1005]  # Optional unique identifiers
}

perfume_df = pd.DataFrame(data)

# Create the scraper instance with checkpointing every 2 perfumes (for demo purposes)
scraper = PerfumePriceScraper(checkpoint_dir="perfume_checkpoints", checkpoint_interval=2, max_results=5)

# Option 1: Process the entire dataset at once
result_df = scraper.process_perfume_dataset(
    perfume_df, 
    name_col='perfume_name', 
    brand_col='brand', 
    id_col='id'
)

# Save final results
result_df.to_csv('perfume_sizes_prices.csv', index=False)

print(result_df)
