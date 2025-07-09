# Project description

* Main requirements
  * Built a web scraper that collects and stores the web data in a local duck db
  * After crawling is **finished** the process starts to classify the text with a queue manager 
  * I Decoupled the 2 processes, since in production we will need 2 different types of machines to run the processes, 
    1. first to crawl with a CPU-intensive machine 
    2. GPU-oriented machine to classify
  * Scraper collects title and content from the web page but only uses title to determine the topic, in order to save resources
  * Used the provided list of topics for scoring the text, the application supports passing additional topics for comparison, each additional topic to score increases inference time since the model needs to compare the text to each topic
* Bonus
  * Scrapes web with async
  * Could be scale horizontally in order to handle large trafic, we should use parallel computing (with small machines), and pay attention to efficient batching in order to avoid duplicate calculations
  * Application has recovery from where the process stopped both in the web crawler and in the link processor
  * please note the docker build takes several minutes since it downloads the model and initiates the db, 
  This allows the application to serve (scrape & classify) the moment you finish building the Docker image,

## TL:DR
Just run the following commands from the project dir after you extract from compressed file (the build takes a while to download the model):

### Using Poe the Poet (Recommended)
```bash
# Set up the project (init database and download model)
poe setup

# Run scraping
poe scrape https://example.com --depth 2 --topics "topic1" "topic2"

# Or run individual tasks
poe init-db
poe download-model
poe test
```

### Using Docker
Build example:
```bash
docker build --build-arg MODEL_NAME="valhalla/distilbart-mnli-12-1" --build-arg DB_NAME="scraping_data.db" -t crawl_app .
```

Run container (interactive shell):
```bash
docker run -it crawl_app
```

Inside the container, use Poe tasks:
```bash
poe scrape https://example.com --depth 2 --topics "topic1" "topic2"
```

# Architecture and Components

## Data Flow

```
WebScraper (recursively scrapes pages)
   ↓
CrawlerDataManager (stores in DB)
   ↓
QueueManager (fetches unclassified links)
   ↓
LinkProcessor (processes in batches)
   ↓
TopicClassifier (classifies using HF model)
   ↓
QueueManager (updates classifications batch in db)
   ↓
Analytics (aggregates topic scores)
```

### Main Application Flow (`urlevaluator/src/main.py`)
   - Primary entry point with command-line argument parsing
   - Initiates scraping based on provided URL & depth
   - Can pass additional topics for classification
   - Processes links for classification
   - Handles errors and cleanup
   - Loads environment variables only when executed as main

### Database Layer (`database/`)
- `init_db.py`: 
  - Implements database connection and initialization
  - Runs at docker build time or before start scraping (if not using docker, run `init_db.py` manually)
  - Initializes database schema with two tables:
    - `pages`: Stores page metadata (URL, source URL, depth, title, content, visit timestamp)
    - `links`: Stores discovered links with classification scores
- `url_db_manager.py`:
  - Handles data persistence for scraped pages
  - Stores page data and associated links
  - Tracks visited URLs to prevent duplicates
- `queue.py`:
  - Implements processing queue for unclassified links
  - Provides batch fetching with pagination
  - Updates classification results

### Scraping Component (`scraper/`)
- `crawler.py`:
  - Implements depth-first web crawling
  - Validates URLs before processing
  - Extracts links and page content
  - Supports resuming from last visited URL
  - Has limit for max URLs to collect
  - Enforces rate limiting (1 second between requests)

### Classification System (`classifier/`)
- `download_model.py`:
  - Implements main model manager class
  - Handles model and tokenizer download from HuggingFace
  - Caches models locally in resources directory
  - Supports model name configuration via environment variables
  - Provides model path management
- `link_processor.py`:
  - Processes links in batches
  - Coordinates classification workflow
  - Handles errors during classification
  - Tracks processing progress
- `topic_classifier.py`:
  - Interfaces with HuggingFace model
  - Classifies text into provided topics (has default topics and supports additional topics passed by user)
  - Handles model inference
  
### Utility Components (`utils/`)
- `log_handler.py`:
  - Centralizes logging configuration
- `query_db.py`:
  - Used outside the application for handling database queries
  - Provides database maintenance utilities
  - Supports data cleanup and inspection



## Configuration and Deployment

### Poetry Configuration (`pyproject.toml`)
- Manages Python package requirements
- Uses Poe the Poet for task management and CLI commands

### Available Poe Tasks
- `poe setup`: Initialize database and download ML model
- `poe init-db`: Create database with required tables
- `poe download-model`: Download the ML model for topic classification
- `poe scrape`: Crawl website and classify links
- `poe test`: Run the test suite

### Docker Configuration (`Dockerfile`)
- Base image Python 3.11-slim
- Uses Poetry for dependency management & entry points  
- Build-time configuration:
  - Creates database and downloads ML model from HF during build
  - Ready to serve immediately after build
  - Supports build arguments:
    - `MODEL_NAME`: HuggingFace model identifier
    - `DB_NAME`: DuckDB database filename
- Can mount the `resources` directory to avoid re-downloading
- Entry point: Interactive bash shell

Build example:
```bash
docker build \
  --build-arg MODEL_NAME="valhalla/distilbart-mnli-12-1" \
  --build-arg DB_NAME="scraping_data.db" \
  -t crawl_app .
```

Run container (interactive shell):
```bash
docker run -it crawl_app
```

Inside the container, use Poe tasks:
```bash
poe scrape https://example.com 2 "topic1" "topic2"
```

### Testing (`urlevaluator/tests/`)

- directory contains integration tests for the model

```bash
docker run crawl_app poetry run pytest urlevaluator/tests/
```

#### copy project to server
```bash
# Remove existing project directory on server
ssh pie@192.168.1.205 "rm -rf ~/git/crawl_app" && rsync -avz --include '**/*.py' --include '**/*.toml' --include 'Dockerfile' --include '**/*.md' --exclude '*' . pie@192.168.1.205:~/git/crawl_app/
```



