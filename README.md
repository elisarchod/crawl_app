# Project description

## Author
**Name:** Elisar Chodorov  
**Email:** [elisar.chod@gmail.com](mailto:elisar.chod@gmail.com)

## Short answers in respect to assignment document

* Built a web scraper that collects and stores the web data in a local duck db
* After crawling is **finished** the process starts to classify the text with a queue manager 
* Scraper collects title and content but used only use title to determine the topic, but the application supports using the content as well
* Decoupled the 2 processes, since we will need 2 different types of machines to run the processes, 
  1. first to crawl with a CPU-intensive machine 
  2. GPU-oriented machine to classify 
* Used the provided list of topics for scoring the text, the application supports passing additional topics for comparison, but each additional topic to score increases inference time as the model loops each topic
* The model was quite slow on my laptop, did not try to use async communication for web crawling, but could definitely try
* Should scale horizontally for handling 10,000,000 URLs, which sounds like a lot to cover, and you should use parallel computing (I guess the don't need to be too powerful), with a very good and efficient batching in order to avoid duplicate calculations
* Has recovery from where the process stopped both in the web crawler and in the link processor
* There is an explanation about the docker in this doc, please note the docker build takes several minutes since it downloads the model and initiates the db, 
This allows the application to serve (scrape & classify) the moment you finish building the Docker image,

## TL:DR
Just run the following commands from the project dir after you extract from compressed file (the build takes a while to download the model):
```bash

Build example:
```bash
docker build --build-arg MODEL_NAME="valhalla/distilbart-mnli-12-1" --build-arg DB_NAME="scraping_data.db" -t arpe .
```

Run application:
```bash
docker run arpe scrape-url https://example.com --max-depth 2 --additional-topics "topic1" "topic2"
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

### Main Application Flow (`main.py`)
   - Initiates scraping based on provided URL & depth
   - Can pass additional topics for classification
   - Processes links for classification
   - Handles errors and cleanup

### Database Layer (`database/`)
- `init_db.py`: 
  - Implements database connection using Singleton pattern
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
  - Implements main model manager singleton class
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
- `singleton.py`:
  - Provides singleton pattern implementation
- `log_handler.py`:
  - Centralizes logging configuration
- `query_db.py`:
  - Used outside the application for handling database queries
  - Provides database maintenance utilities
  - Supports data cleanup and inspection
- `cli.py`:
  - Implements command-line interface
  - Exposes core functionality:
    - Model download
    - Database creation
    - Scraping initiation


## Configuration and Deployment

### Poetry Configuration (`pyproject.toml`)
- Manages Python package requirements
- Defines entry points for CLI commands

### Docker Configuration (`Dockerfile`)
- Base image Python 3.11-slim
- Uses Poetry for dependency management
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
  -t arpe .
```

Run container:
```bash
docker run arpe scrape-url https://example.com --max-depth 3 --additional-topics "topic1" "topic2"
```

### Testing

- `tests/` directory contains integration tests for the model

```bash
docker run arpe poetry run python -m unittest discover urlevaluator/tests
```

#### copy project to server
```bash
# Remove existing project directory on server
ssh pie@192.168.1.205 "rm -rf ~/git/arpe" && rsync -avz --include '**/*.py' --include '**/*.toml' --include 'Dockerfile' --include '**/*.md' --exclude '*' . pie@192.168.1.205:~/git/arpe/
```



