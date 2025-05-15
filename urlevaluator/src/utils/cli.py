from typing import List
import argparse
from urlevaluator.src.classifier.download_model import model_manager
from urlevaluator.src.database.init_db import db_manager
from urlevaluator.src.main import scrape_and_process_links

def create_db_command():
    db_manager.create_database()

def download_model_command():
    model_manager.download_model()

def scrape_url_command():
    parser = argparse.ArgumentParser(description='Scrape URLs')
    parser.add_argument('initial_url', help='Initial URL to start scraping from')
    parser.add_argument('--max-depth', type=int, default=2, help='Maximum depth of the crawl')
    parser.add_argument('--additional-topics', nargs='*', help='Additional topics to classify')
    args = parser.parse_args()
    
    scrape_and_process_links(args.initial_url, args.max_depth, args.additional_topics)

if __name__ == '__main__':
    scrape_url_command()