import requests
from faker import Faker
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Initialize Faker
fake = Faker()

# API Configuration
API_URL = 'http://localhost:8000/api/magazine'

categories = ['Entertainment', 'Survival', 'Movies', 'Technology', 'Farming', 'Healthcare', 'Income Tax']

titles = {
    'Entertainment': [
        'The rise of streaming platforms: Changing the entertainment industry',
        'How virtual reality is transforming entertainment experiences',
        'The influence of social media on modern entertainment',
        'Top entertainment trends to watch in the coming years',
        'The future of live events: Concerts, sports, and theatre in the digital age'
    ],
    'Survival': [
        'Essential survival skills everyone should know',
        'How to prepare for natural disasters: A survival guide',
        'The psychology of survival: Mindset during crisis situations',
        'Urban survival: Tips for living in a disaster-prone city',
        'Wilderness survival: Building shelters and sourcing food'
    ],
    'Movies': [
        'The impact of CGI and VFX in modern filmmaking',
        'How streaming services are reshaping the movie industry',
        'The rise of indie films and their influence on mainstream cinema',
        'Exploring the world of film festivals and their importance to filmmakers',
        'The evolution of storytelling in cinema: From classics to contemporary'
    ],
    'Technology': [
        'The role of artificial intelligence in shaping the future of technology',
        'Blockchain technology and its potential to revolutionize industries',
        'The rise of smart cities: How technology is shaping urban life',
        'Quantum computing: The next frontier in tech innovation',
        '5G technology: What it means for the future of connectivity'
    ],
    'Farming': [
        'The future of sustainable farming: Innovative methods and practices',
        'How AI is transforming modern farming techniques',
        'The rise of organic farming: Health benefits and environmental impact',
        'The role of drones in agriculture: Precision farming at its best',
        'How urban farming is becoming a solution to food insecurity'
    ],
    'Healthcare': [
        'The role of telemedicine in the future of healthcare delivery',
        'AI in healthcare: Revolutionizing diagnostics and treatment options',
        'Mental health awareness and the importance of early intervention',
        'The challenges of global healthcare systems in the 21st century',
        'How wearable technology is changing healthcare monitoring and management'
    ],
    'Income Tax': [
        'Understanding the basics of income tax: A beginner’s guide',
        'Tax planning strategies for individuals and businesses',
        'The impact of tax reforms on the global economy',
        'How to file income tax returns online: A step-by-step guide',
        'Income tax deductions: What you can claim and how to maximize savings'
    ]
}
def generate_magazine_batch(batch_size: int):
    
    batch = []
    for _ in range(batch_size):
        category = random.choice(categories)
        title = random.choice(titles[category])
        publish_date = fake.date_this_century()
        
        magazine = {
            'title': title,
            'author': fake.name(),
            'category': category,
            'content': ' '.join(fake.sentences(2)),
            'publish_date': publish_date.strftime('%Y-%m-%d')
        }
        batch.append(magazine)
    return batch

def add_magazine_batch(batch):
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_URL, json=batch, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully added batch of {len(batch)} magazines")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding magazine batch: {str(e)}")
        return False

def add_data_to_database(total_count: int = 50, batch_size: int = 10):
    
    logger.info(f"Will post {total_count} magazines to DB in batches of {batch_size}")
    
    # Calculate number of full batches and remaining items
    num_batches = total_count // batch_size
    remaining_items = total_count % batch_size
    
    # Process full batches
    for batch_num in range(num_batches):
        logger.info(f"Processing batch {batch_num + 1}/{num_batches}")
        batch = generate_magazine_batch(batch_size)
        if add_magazine_batch(batch):
            logger.info(f"Batch {batch_num + 1} processed successfully")
        else:
            logger.error(f"Failed to process batch {batch_num + 1}")
    
    # Process remaining items if any
    if remaining_items > 0:
        logger.info(f"Processing remaining {remaining_items} items")
        final_batch = generate_magazine_batch(remaining_items)
        if add_magazine_batch(final_batch):
            logger.info("Remaining items processed successfully")
        else:
            logger.error("Failed to process remaining items")

    logger.info("Data generation completed")
    
    
# Generate 50 magazines in batches of 10
add_data_to_database(50, 10)