# Project description

## Author
**Name:** Elisar Chodorov  
**Email:** elisar.chod@gmail.com

## Short answers in respect to assignment

* build a web scrapper that collects and stores the web data in a local duck db
* after we **finish** crawling we classify the text with a queue manager 
* collect title and content but used only title for the model, could have used first n of the web page content
* Decoupled the 2 process, since we will need 2 different types of machines to run the processes, 
  1. first to crawl with CPU intense machine 
  2. GPU oriented machine to classify 
* used the provided list of topics for scoring the text, the application supports passing additional topics for comparison, but each additional topic to score increases inference time as the model loops each topic
* the model worked very slow on my laptop, i did not try to use async communication for web crawling, we could defentaly try it
* Should scale horizontally for handling 10,000,000 it sounds like a lot of url to cover, and you should use parallel computing (I guess the don't need to be too powerful), with a very good and efficient batching in order to avoid duplicate calculations
* I have a recovery from where we left both in the web crawler and in the link process based
* there is an explanation about the docker, please note the build takes several minutes as it downloads the model and initates the db, but it will be ready to scrap and find topic the moment the container finished

#### TL:DR
just run the following commands from the project dir:

Build example:
```bash
docker build \
  --build-arg MODEL_NAME="valhalla/distilbart-mnli-12-1" \
  --build-arg DB_NAME="scraping_data.db" \
  -t arpe .
```

Run container:
```bash
docker run arpe scrape-url https://example.com --max-depth 2 --additional-topics "topic1" "topic2"
```

# Architecture and Components

## Data Flow

```
WebScraper
   ↓
CrawlerDataManager (stores in DB)
   ↓
QueueManager (fetches unclassified links)
   ↓
LinkProcessor (processes in batches)
   ↓
TopicClassifier (classifies using ML model)
   ↓
QueueManager (updates classifications)
   ↓
Analytics (aggregates topic scores)
```

### Main Application Flow (`main.py`)

   - Checks if URL exists in database
   - Initiates scraping if needed
   - Processes links for classification
   - Handles errors and cleanup

### Database Layer (`database/`)
- `init_db.py`: 
  - Implements database connection using Singleton pattern
  - Initializes database schema with two tables:
    - `pages`: Stores page metadata (URL, source URL, depth, title, content)
    - `links`: Stores discovered links with their text and classification scores
- `url_db_manager.py`:
  - Handles data persistence for scraped pages
  - Performs URL existence checks
  - Stores page data and associated links
- `queue.py`:
  - Implements processing queue for unclassified links
  - Provides batch fetching with pagination
  - Updates classification results

### Scraping Component (`scraper/`)
- `crawler.py`:
  - Implements depth-first web crawling
  - Validates URLs before processing
  - Extracts links and page content
  - Enforces rate limiting (1 second between requests)
  - Tracks visited URLs to prevent duplicates
  - Supports resuming from last visited URL
  - Has number of URLs collect limit 

### Classification System (`classifier/`)
- `download_model.py`:
  - Implements ModelManager singleton class
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
  - Classifies text into predefined topics
  - Handles model inference
  
### Utility Components (`utils/`)
- `singleton.py`:
  - Provides database and model management
- `log_handler.py`:
  - Centralizes logging configuration
- `query_db.py`:
  - Provides database maintenance utilities
  - Supports data cleanup and inspection
- `cli.py`:
  - Implements command-line interface
  - Exposes core functionality:
    - Model download
    - Database creation
    - Scraping initiation


## Configuration and Deployment

### TOML Configuration (`pyproject.toml`)
- Manages Python package requirements
- Defines entry points for CLI commands

### Docker Configuration (`Dockerfile`)
- Base image: Python 3.11-slim
- Uses Poetry for dependency management
- Build-time configuration:
  - Creates database and downloads ML model from HF during build
  - Ready to be deployed for inferance
  - Supports build arguments:
    - `MODEL_NAME`: HuggingFace model identifier
    - `DB_NAME`: DuckDB database filename
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
- `tests/` directory contains integration tests
```bash
pytest tests/
```

#### copy project to server
```bash
# Remove existing project directory on server
ssh pie@192.168.1.205 "rm -rf ~/git/arpe" && rsync -avz --include '**/*.py' --include '**/*.toml' --include 'Dockerfile' --include '**/*.md' --exclude '*' . pie@192.168.1.205:~/git/arpe/
```



