import pandas as pd
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Call the API to add magazines
def call_api(magazines_batch):
    url = "http://localhost:8000/api/magazines"
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=magazines_batch, headers=headers)
        response.raise_for_status()  
        result = response.json() 
        
        if isinstance(result, list): 
            for magazine in result:
                logger.info(f"Magazine {magazine['magazine_id']} added successfully.")
            return True
        else:
            logger.error("Unexpected response format from API.")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return False

# Main processing function
def process_magazines(file_path, batch_size=10, max_records=None):
    try:
        # Read entire CSV file using pandas
        df = pd.read_csv(file_path)

        # Ensure 'publish_date' column is in the correct format
        df['publish_date'] = pd.to_datetime(df['publish_date'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')

        # Concatenate content sentences before processing and update the 'content' column
        df['content'] = df['content'].apply(lambda x: ' '.join(eval(x)) if isinstance(x, str) else x)

        magazines = df.to_dict(orient='records')

        # Limit records to process if max_records is provided
        if max_records:
            magazines = magazines[:max_records]

        # Process in batches of 10 records
        for i in range(0, len(magazines), batch_size):
            batch = magazines[i:i+batch_size]
            success = call_api(batch)
            # print(batch)
            if not success:
                logger.error("Error while processing batch, halting further operations.")
                break  # Exit the loop if the API call fails

    except Exception as e:
        logger.error(f"Error during processing: {e}")


batch_size = 10  # Process 10 records at a time
max_records = 50  # Limit the processing to 50 records, change to None for all records

process_magazines("fake_magazines.csv", batch_size, max_records)
