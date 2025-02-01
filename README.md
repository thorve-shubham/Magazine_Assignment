# Magazine Vector Search API

This project implements a hybrid search API that combines traditional keyword-based search with vector-based search to efficiently query a database of magazine information and content. The API is built using Python 3.9, FastAPI, and PostgreSQL with the pgvector, pg_trgm extension for vector search and trigram comparison capabilities.

## Features

- **Hybrid Search**: Combines keyword-based search and vector-based search for improved relevance.
- **Efficient Querying**: Optimized to handle up to 1 million records.
- **Pagination**: Supports pagination for large result sets.
- **Performance Optimization**: Utilizes indexing and database optimizations for fast query responses.

## Technology Stack

- **Backend**: Python 3.9, FastAPI
- **Database**: PostgreSQL with pgvector and pg_trgm extension
- **Vector Embeddings**: Sentence Transformers (multi-qa-MiniLM-L6-cos-v1)
- **ORM**: SQLAlchemy
- **Logging**: Python logging module
- **Data Generation**: Used a Python Notebook with Faker on Google Colab (Personal System Performance Limitations)
- **Python libraries**: FastAPI, uvicorn, sqlalchemy, pandas, sentence_transformers, pgvector
- **Testing Tools**: Postamn Client

## Getting Started Instructions

Follow below steps:

#### **1. Install PostgreSQL -**

- We will be making use of an image on docker repository which comes with pgvector extension preinstalled in it.
- Install Docker Desktop from - https://www.docker.com/products/docker-desktop/
- once docker is running, open command line tool and execute below command

```bash
docker run -e POSTGRES_USER=username -e POSTGRES_PASSWORD=password -e POSTGRES_DB=magazine_databse -p 5432:5432 -d ankane/pgvector --name container_name
```

- With this command you should have your PostgreSQL Server running in docker container
- Next, you need to connect to the database using psql (CLI) or any Database Client using above credentials and execute

```bash
create extension vector;
create extension pg_trgm;
```

#### **2. Installing Python -**

- Download Python 3.9 from - https://www.python.org/downloads/
- make sure you have version 3.9 installed by executing

```bash
python --version
```

- Next, install required libraries and dependencies

```bash
pip install fastapi uvicorn sqlalchemy pandas sentence-transformers pgvector faker
```

#### **3. Setting up Code Repository -**

- Clone repository from - https://github.com/thorve-shubham/Magazine_Assignment.git
- Navigate to app directory and create a .env file as shown below, update username, password accordingly

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/magazine_database
```

- To run the API Server in command line tool from root of git repository execute below command to run main module

```bash
python -m app.main
```

- Executing of this command will take 2-3 minutes as database tables and their indexes will be created.
- Once you see a message stating that FASTAPI Server has started you're good to acess APIs

#### **4. Loading 50 Magazine Records to Database -**

- Make sure the app is running, and then execute below command from root of git repository

```bash
python .\app\data_loader_relevant.py
```

- This script will add 50 records

#### **5. Loading 1 Million Dummy Magazine Data - (Optional)**

- To create dummy data, we have a data_loader.py python script which loades data in batches from fake_magazines.csv file
- How to get this csv ?
  - Execute this Google Colab which will generate the CSV with 1 million records - https://colab.research.google.com/drive/1Exu17nNt0wojT5j464-dY2qBmxaVqRCE?usp=sharing
  - You can then download this CSV and paste it into app folder of Magazine_Assignment repository.
- To load the data into PostgreSQL database execute data_loader.py from command line terminal using below command, make sure to execute this command from root directory of code repository.
- Both batch size and records to store fields are programmable in this script, feel free to tweak

```bash
python .\app\data_loader.py
```

- With this now we have database with some records to to query

## API Endpoints

#### **1. Add Magazines (POST) -**

```
POST /api/magazine
```

#### Request Format

Send a JSON array containing magazine objects with the following properties:

| Field        | Type   | Description                           |
| ------------ | ------ | ------------------------------------- |
| title        | string | Title of the magazine article         |
| author       | string | Name of the article's author          |
| category     | string | Category/topic of the article         |
| content      | string | Main content/body of the article      |
| publish_date | string | Publication date in YYYY-MM-DD format |

#### Example Request

```json
[
  {
    "title": "The Future of Quantum Computing",
    "author": "Dr. Alice Zhang",
    "category": "Technology",
    "content": "Quantum computing promises to revolutionize industries by solving complex problems faster than classical computers. Researchers are now focusing on overcoming quantum decoherence to make these machines more reliable.",
    "publish_date": "2023-09-15"
  }
]
```

#### Response Format

Returns the created magazine entries with assigned IDs. The response maintains the same structure as the request with an additional `id` field for each entry.

#### Example Response

```json
[
  {
    "id": "1",
    "title": "The Future of Quantum Computing",
    "author": "Dr. Alice Zhang",
    "category": "Technology",
    "content": "Quantum computing promises to revolutionize industries by solving complex problems faster than classical computers. Researchers are now focusing on overcoming quantum decoherence to make these machines more reliable.",
    "publish_date": "2023-09-15"
  }
]
```

#### Status Codes

| Code | Description                                       |
| ---- | ------------------------------------------------- |
| 201  | Successfully created magazine entries             |
| 400  | Invalid request format or missing required fields |
| 500  | Server error                                      |

#### **2. Query Magazine - (GET)**

**Approach #1**

```
POST /api/magazine?search=<search_query>
```

Eaxmple Endpoint - http://localhost:8000/api/magazine?search=healthcare&page=1&page_size=10

**Approach #2**

```
POST /api/magazine/best?search=<search_query>
```

Eaxmple Endpoint - http://localhost:8000/api/magazine/best?search=healthcare&page=1&page_size=10

| Query Param | Type   | Description             |
| ----------- | ------ | ----------------------- |
| search      | string | Search Query            |
| page        | number | Page Number (Optional)  |
| page_size   | number | Size of Page (Optional) |

#### Response Format

Returns a list of magazines with page, page*size, total*

#### Example Response

```json
{
  "magazines": [
    {
      "id": "1",
      "title": "The Future of Quantum Computing",
      "author": "Dr. Alice Zhang",
      "category": "Technology",
      "content": "Quantum computing promises to revolutionize industries by solving complex problems faster than classical computers. Researchers are now focusing on overcoming quantum decoherence to make these machines more reliable.",
      "publish_date": "2023-09-15"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_results": 1,
  "total_pages": 1
}
```

### Find the Postman Collection in repository - Magazine Search.postman_collection.json

## Database Schema

### Table 1 : Magazine Information

```sql
CREATE TABLE magazine_information (
    id SERIAL PRIMARY KEY,
    title VARCHAR INDEX,
    author VARCHAR,
    category VARCHAR,
    publish_date DATE
);
```

### Table 2 : Magazine Content

```sql
CREATE TABLE magazine_content (
    id SERIAL PRIMARY KEY,
    magazine_id INTEGER REFERENCES magazine_information(id),
    content VARCHAR,
    content_tsvector TSVECTOR,
    content_embedding VECTOR(384)
);
```

## Search Implementation Details

The API implements hybrid search using two different approaches:

### Approach 1: Separate Queries with Memory-Based Deduplication

**Method**: `query_magazine()`

This approach combines keyword and vector search results in application memory:

1. **Keyword Search**

   - Uses PostgreSQL's full-text search capabilities with `tsvector` and `tsquery`
   - Performs case-insensitive matching on title and author using ILIKE
   - Ranks results using `ts_rank_cd`

2. **Vector Search**

   - Uses pgvector for semantic similarity search
   - Calculates cosine similarity between query embedding and stored content embeddings
   - Filters results based on minimum similarity threshold (0.15) - can be increased for more precise similarity

3. **Result Combination Process**
   - Fetches double the requested page size from both searches
   - Merges results in memory
   - Deduplicates based on magazine_id while keeping highest scoring version
   - Applies pagination after deduplication

**Limitations**:

- Less efficient due to fetching more data than needed
- Memory-intensive for large result sets
- Pagination might be inconsistent due to post-query deduplication

### Approach 2: Database-Level Hybrid Search

**Method**: `hybrid_search()`

This approach combines searches at the database level using a single SQL query:

1. **Query Structure**

   - Uses Common Table Expressions (CTEs) for both search types
   - `keyword_search` CTE:

     ```sql
     SELECT ... FROM magazine_information mi
     JOIN magazine_content mc ON mi.id = mc.magazine_id
     WHERE (mc.content_tsvector @@ to_tsquery('english', :query))
     OR mi.title % :query
     OR mi.author % :query
     OR mi.title ILIKE '%' || :query || '%'
     OR mi.author ILIKE '%' || :query || '%'
     ```

   - `vector_search` CTE:
     ```sql
     SELECT ... FROM magazine_information mi
     JOIN magazine_content mc ON mi.id = mc.magazine_id
     WHERE (1 - (mc.content_embedding <=> :query_embedding)) >= :threshold
     ```

2. **Result Combination**
   - Uses `UNION ALL` to combine both search results
   - Applies `DISTINCT ON` for efficient deduplication
   - Sorts by score and applies pagination in a single query

**Advantages**:

- More efficient as deduplication and pagination happen at database level
- Reduced memory usage
- Consistent pagination
- Better performance for large datasets

## Search Features

- **Full-text Search**: Uses PostgreSQL's `tsvector` and `tsquery` for text matching
- **Semantic Search**: Uses pgvector for embedding-based similarity search
- **Hybrid Ranking**: Combines text relevance and semantic similarity scores
- **Pagination**: Supports page-based result fetching
- **Deduplication**: Ensures unique results while maintaining highest relevance
- **Minimum Score Threshold**: Filters out low-relevance results (0.15 threshold)

## Performance Considerations

### 1. **Indexing Strategy**

### Magazine Content Table Indexes

- **content_embedding**: HNSW index optimized for vector cosine similarity which significantly improves performance for vector-based queries

- **content_tsvector**: GIN index which optimizes full-text search operations and enables fast text pattern matching

- **magazine_id**: B-tree index that improves join performance with magazine_information table and optimizes foreign key relationships

### MagazineInformation Table Indexes

- **title and author**: Regular B-tree index for exact matches and GIN with trigram operators for fuzzy matching enabling efficient partial and full title searches

### Performance Benefits

1. **Vector Similarity Search**

   - HNSW index reduces time complexity for nearest neighbor search
   - Provides approximate results with high accuracy
   - Scales well with large datasets

2. **Text Search Performance**

   - GIN indexes enable fast full-text search capabilities
   - Trigram indexes support efficient fuzzy matching
   - Combined indexes allow flexible text search without performance penalties

### 2. **Query Optimization**

- Uses joins instead of subqueries where possible
- Implements efficient pagination
- Leverages database-level operations for better performance

### 3. **Memory Management**

- Second approach (hybrid_search) is more memory-efficient
- Handles deduplication at database level
- Reduces data transfer between database and application

### 4. **Choice of Sentence Transformer Model - multi-qa-MiniLM-L6-cos-v1**

reference - https://sbert.net/docs/sentence_transformer/pretrained_models.html

- A descent choice considering the semantic search performance of 51.83 on 6 datasets, speed of 14200 and performance in sentence embedding of 64.33 on 14 datasets.
- This is one of the fastest pretrained models that sbert provides with maximum performance is semantic search.
- Its a lightweight model of 80 MB.

## API Stress Test Result

### System Configuration:

- Processor: Intel Core i7 8th Gen
- RAM: 8 GB
- Database: Running in a Docker container with 4 GB RAM allocated

### Test Configuration

- **Test Type**: Stress Test
- **Strategy**: Peak Strategy
- **Duration**: 5 minutes
- **Virtual Users**: 20 VUs

### Results Comparison

#### Strategy 1: Combined Search with Separate Queries

| Metric                | Value |
| --------------------- | ----- |
| Average Response Time | 135ms |
| Requests per Second   | 9.67  |
| Total Requests Sent   | 2,984 |

![Performance Result of Approach 1](StressTest_Method_1.png "Approach 1 - Stress Test")

#### Strategy 2: Hybrid Search with Combined Query

| Metric                | Value |
| --------------------- | ----- |
| Average Response Time | 110ms |
| Requests per Second   | 10.03 |
| Total Requests Sent   | 3,087 |

![Performance Result of Approach 2](StressTest_Method_2.png "Approach 2 - Stress Test")

### Key Findings

- Strategy 2 shows ~18.5% improvement in response time
- Strategy 2 handles ~3.5% more requests per second
- Strategy 2 processed ~3.5% more total requests during the test period

## Example Search Queries and Expected Results

**_IMPORTANT NOTE_** : It is recommended to add magazines using POST API to get the best results as Faker Library generated sentences randomly and thus content may not be related to title or category of magazine.

Use AI tools to generate relevant magazine data is recommended as its easy and POST API supports batch magazine save.

### Example 1 - Search Query - "health"

Expected Output - Magazines related to healthcare

### Example 2 - Search Query - "europe"

Expected Output - Magazines related to french food

### Example 3 - Search Query - "outespace"

Expected Output - Magazines related to space travel

### Example 4 - Search Query - "graphic card"

Expected Output - Magazines related to Competative Gaming

#### Example Data in Database:

```json
[
  {
    "id": 51,
    "title": "The Future of Quantum Computing",
    "author": "Dr. Alice Zhang",
    "category": "Technology",
    "publish_date": "2023-09-15",
    "content": "Quantum computing promises to revolutionize industries by solving complex problems faster than classical computers. Researchers are now focusing on overcoming quantum decoherence to make these machines more reliable."
  },
  {
    "id": 52,
    "title": "Exploring the Depths of the Mariana Trench",
    "author": "Marine Biologist John Doe",
    "category": "Science",
    "publish_date": "2023-08-22",
    "content": "Recent expeditions to the Mariana Trench have uncovered new species that thrive in extreme pressure. These discoveries could provide insights into the origins of life on Earth."
  },
  {
    "id": 53,
    "title": "The Renaissance of Classical Music",
    "author": "Emily Carter",
    "category": "Music",
    "publish_date": "2023-07-30",
    "content": "Classical music is experiencing a resurgence as young composers blend traditional techniques with modern sounds. This fusion is attracting a new generation of listeners to concert halls."
  },
  {
    "id": 54,
    "title": "Advancements in CRISPR Technology",
    "author": "Dr. Sarah Lin",
    "category": "Biotechnology",
    "publish_date": "2023-06-18",
    "content": "CRISPR technology is being refined to increase its precision in gene editing. This could lead to breakthroughs in treating genetic disorders and improving crop resilience."
  },
  {
    "id": 55,
    "title": "The Art of French Pastry",
    "author": "Chef Pierre Lambert",
    "category": "Culinary",
    "publish_date": "2023-05-25",
    "content": "French pastry chefs are innovating with traditional recipes to create lighter, more flavorful desserts. Techniques like sous-vide are being adapted for baking to enhance texture and taste."
  },
  {
    "id": 56,
    "title": "Virtual Reality in Education",
    "author": "Tech Educator Rachel Gomez",
    "category": "Education",
    "publish_date": "2023-04-12",
    "content": "Virtual reality is transforming classrooms by providing immersive learning experiences. Students can now explore historical sites or conduct virtual science experiments from their desks."
  },
  {
    "id": 57,
    "title": "The Rise of Sustainable Fashion",
    "author": "Fashion Critic Mia Johnson",
    "category": "Fashion",
    "publish_date": "2023-03-09",
    "content": "Sustainable fashion is gaining momentum as designers focus on eco-friendly materials and ethical production methods. Consumers are increasingly supporting brands that prioritize environmental responsibility."
  },
  {
    "id": 58,
    "title": "Understanding Black Holes",
    "author": "Astrophysicist Dr. Neil Carter",
    "category": "Astronomy",
    "publish_date": "2023-02-17",
    "content": "Recent studies have provided new insights into the behavior of black holes and their impact on surrounding galaxies. These findings help scientists understand the fundamental laws of the universe."
  },
  {
    "id": 59,
    "title": "The Evolution of Digital Art",
    "author": "Digital Artist Sofia Martinez",
    "category": "Art",
    "publish_date": "2023-01-24",
    "content": "Digital art is evolving with advancements in software that allow for more realistic textures and lighting. Artists are pushing boundaries by integrating AI to create dynamic, interactive pieces."
  },
  {
    "id": 60,
    "title": "Breakthroughs in Renewable Energy",
    "author": "Environmental Scientist Dr. Omar Yusuf",
    "category": "Environment",
    "publish_date": "2022-12-15",
    "content": "Innovations in solar panel technology are making renewable energy more efficient and affordable. These advancements are crucial for reducing global dependence on fossil fuels."
  },
  {
    "id": 61,
    "title": "The Psychology of Social Media",
    "author": "Psychologist Dr. Hannah Lee",
    "category": "Psychology",
    "publish_date": "2022-11-08",
    "content": "Social media usage is being studied for its effects on mental health and social behavior. Researchers are finding that moderation and mindful engagement can mitigate negative impacts."
  },
  {
    "id": 62,
    "title": "Modern Architecture Trends",
    "author": "Architect Daniel Kim",
    "category": "Architecture",
    "publish_date": "2022-10-03",
    "content": "Contemporary architecture is focusing on sustainability and smart technology integration. Buildings are not only becoming more energy-efficient but also more adaptable to the needs of their occupants."
  },
  {
    "id": 63,
    "title": "The World of Competitive Gaming",
    "author": "Gaming Analyst Chris Thompson",
    "category": "Gaming",
    "publish_date": "2022-09-19",
    "content": "Esports continues to grow, with tournaments offering multi-million dollar prizes and attracting global audiences. This surge is reshaping perceptions of gaming as a legitimate career path."
  },
  {
    "id": 64,
    "title": "Innovations in Automotive Design",
    "author": "Automotive Engineer Lisa Chang",
    "category": "Automotive",
    "publish_date": "2022-08-14",
    "content": "Electric vehicles are at the forefront of automotive innovation, with improvements in battery life and charging infrastructure. Designers are also focusing on enhancing user experience with advanced interfaces."
  },
  {
    "id": 65,
    "title": "The Impact of AI on Healthcare",
    "author": "Health Tech Expert Dr. Raj Patel",
    "category": "Healthcare",
    "publish_date": "2022-07-22",
    "content": "Artificial intelligence is revolutionizing healthcare by improving diagnostic accuracy and personalizing treatment plans. AI-driven tools are enabling doctors to predict patient outcomes more effectively."
  },
  {
    "id": 66,
    "title": "Exploring Ancient Civilizations",
    "author": "Historian Dr. Emily Tran",
    "category": "History",
    "publish_date": "2022-06-30",
    "content": "Archaeological discoveries are shedding light on the daily lives of ancient civilizations. These findings help historians piece together the complex social structures of the past."
  },
  {
    "id": 67,
    "title": "The Science of Happiness",
    "author": "Positive Psychologist Dr. Mark Benson",
    "category": "Wellness",
    "publish_date": "2022-05-18",
    "content": "Research in positive psychology is uncovering the practices that contribute to long-term happiness. Techniques like gratitude journaling and mindfulness are proving effective in enhancing well-being."
  },
  {
    "id": 68,
    "title": "The Future of Space Travel",
    "author": "Aerospace Engineer Dr. Susan Choi",
    "category": "Aerospace",
    "publish_date": "2022-04-11",
    "content": "Space agencies are developing technologies for longer manned missions, including to Mars. Innovations in life support and propulsion systems are critical for the success of these endeavors."
  },
  {
    "id": 69,
    "title": "The Revival of Handwritten Letters",
    "author": "Cultural Historian Dr. Angela Moreno",
    "category": "Culture",
    "publish_date": "2022-03-07",
    "content": "In a digital age, handwritten letters are making a comeback as a personal and meaningful way to communicate. This revival is part of a broader trend towards valuing authenticity and craftsmanship."
  },
  {
    "id": 70,
    "title": "Advancements in Robotics",
    "author": "Robotics Engineer Dr. Ethan Bradley",
    "category": "Robotics",
    "publish_date": "2022-02-01",
    "content": "Robotics technology is advancing rapidly, with robots becoming more autonomous and capable of complex tasks. These developments are opening up new possibilities in manufacturing, service, and exploration."
  }
]
```
