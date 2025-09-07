import pandas as pd
from collections import Counter

def log_duplicates(df):
    # Convert ABN to string if it's not already
    df['abn'] = df['abn'].astype(str)
    
    # Count occurrences of each ABN value
    abn_counts = Counter(df['abn'])
    
    # Log duplicates
    duplicates = [f"{abn}: {count}" for abn, count in abn_counts.items() if count > 1]
    print(f"Found {len(duplicates)} duplicate abn values:")
    print(", ".join(duplicates))

def clean_and_log_duplicates():
    # Read CSV
    df = pd.read_csv('data/raw/abn_register_results_20250802_1336.csv')
    
    # Define column name mapping to snake_case
    column_mapping = {
        'isCurrent': 'is_current',
        'replacedFrom': 'replaced_from',
        'entityStatus': 'entity_status',
        'effectiveFrom': 'effective_from',
        'effectiveTo': 'effective_to',
        'entityTypeCode': 'entity_type_code',
        'entityDescription': 'entity_description',
        'acnc_status': 'acnc_status',
        'acnc_status_from': 'acnc_status_from',
        'acnc_status_to': 'acnc_status_to',
        'record_last_updated': 'record_last_updated',
        'gst': 'gst',
        'dgr': 'dgr',
        'main_trading_names': 'main_trading_names',
        'other_trading_names': 'other_trading_names',
        'main_business_physical_address': 'main_business_physical_address',
        'tax_concession_endorsements': 'tax_concession_endorsements'
    }
    
    # Verify all expected columns are present
    missing_columns = [col for col in column_mapping.keys() if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in CSV: {missing_columns}")
    
    # Replace empty strings with None for JSON columns
    json_columns = ['gst', 'dgr', 'main_trading_names', 'other_trading_names', 
                    'main_business_physical_address', 'tax_concession_endorsements']
    for col in json_columns:
        if col in df.columns:
            df[col] = df[col].replace('', None)
    
    # Replace placeholder dates with None for date columns
    date_columns = ['replacedFrom', 'effectiveFrom', 'effectiveTo', 
                    'acnc_status_from', 'acnc_status_to', 'record_last_updated']
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].replace('0001-01-01', None)
    
    # Rename columns to snake_case
    df = df.rename(columns=column_mapping)
    
    # Check if 'abn' column exists and convert to string
    if 'abn' not in df.columns:
        raise ValueError("Column 'abn' not found in the DataFrame")
    else:
        df['abn'] = df['abn'].astype(str)
    
    # Log duplicates before writing to CSV
    log_duplicates(df)
    
    # Save cleaned CSV with snake_case column names
    df.to_csv('data/processed/cleaned_register_results_20250802_1336.csv', index=False)

if __name__ == "__main__":
    clean_and_log_duplicates()