import pandas as pd
import json

def clean_data(input_file, output_file):
    print(f"Loading data from {input_file}...")
    try:
        # Read the JSON file
        df = pd.read_json(input_file)
        
        print(f"Initial data shape: {df.shape}")
        
        # 1. Clean titles: remove leading/trailing spaces
        if 'title' in df.columns:
            df['title'] = df['title'].str.strip()
            
        # 2. Clean prices: remove '$' and commas, then convert to float
        if 'price' in df.columns:
            # Replace empty or None prices with '$0' so they can be parsed, or handle NA
            df['price'] = df['price'].fillna('$0.0')
            df['price'] = df['price'].astype(str).str.replace('$', '', regex=False)
            df['price'] = df['price'].str.replace(',', '', regex=False)
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            
        # 3. Handle reviews: remove " reviews", convert to int
        if 'reviews' in df.columns:
            df['reviews'] = df['reviews'].fillna('0 reviews')
            df['reviews'] = df['reviews'].astype(str).str.replace(' reviews', '', regex=False)
            df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0).astype(int)
            
        print("Data cleaned successfully!")
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Cleaned data saved to {output_file}")
        
        # Print a small sample
        print("\nSample of cleaned data:")
        print(df[['title', 'price']].head())
        
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    input_filename = "scraped_products.json"
    output_filename = "cleaned_products.csv"
    
    clean_data(input_filename, output_filename)
