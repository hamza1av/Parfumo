# Perfume Data Analysis and Rating Prediction

This project is a comprehensive data science project that scrapes, analyzes, and predicts perfume ratings. It uses a variety of data sources and machine learning models to understand the factors that influence perfume ratings and prices.

## Features

- **Data Scraping:** Scripts to scrape perfume data from various websites, including Parfumo, Idealo, and Douglas.
- **Data Analysis:** In-depth analysis of perfume data, including ratings, prices, and scent profiles.
- **Prediction Models:** Machine learning models to predict perfume ratings based on various features.
- **Data Visualization:** A variety of plots and visualizations to understand the data and the model results.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The project is organized into several directories and notebooks:

- **`Scraping/`**: Contains scripts for scraping perfume data.
- **`idealo_prices/`**: Contains scripts for scraping prices from Idealo.
- **`duckduckgo_prices/`**: Contains scripts for scraping prices from DuckDuckGo.
- **`nb_*.ipynb`**: Jupyter notebooks for data analysis, prediction, and visualization.

To run the scrapers or the analysis, navigate to the respective directories and run the Python scripts or notebooks.

## Data

The project uses a variety of data sources, including:

- **`perfumes.xlsx`**: The main dataset with perfume information.
- **`idealo_prices.csv`**: Price data from Idealo.
- **`data/`**: Contains various data files, including brand information and scraped data.

## Models

The project uses the following machine learning models:

- **XGBoost:** For predicting perfume ratings.
- **PyTorch:** For building and training neural networks.
- **Optuna:** For hyperparameter tuning.

The trained models are saved in the `models/` directory.
