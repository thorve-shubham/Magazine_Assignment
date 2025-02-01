import pandas as pd
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Call the API to add magazines
def call_api(magazines_batch):
    url = "http://localhost:8000/api/magazine"
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        # Send POST request to the API
        response = requests.post(url, json=magazines_batch, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        result = response.json()
        # print(result)
        # print(type(result))
        # Check if the response contains the expected structure
        if isinstance(result, list):
            for magazine in result:
                logger.info(f"Magazine {magazine['id']} added successfully.")
            return True
        else:
            logger.error("Unexpected response format from API.")
            return False
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return False
    except ValueError as e:
        logger.error(f"Failed to decode JSON response: {e}")
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
            
            if not success:
                logger.error("Error while processing batch, halting further operations.")
                break

    except Exception as e:
        logger.error(f"Error during processing: {e}")


batch_size = 10
max_records = 100

process_magazines("app/fake_magazines.csv", batch_size, max_records)
