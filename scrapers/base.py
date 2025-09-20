#!/usr/bin/env python3
"""
Base scraper class for Meguru Construction website
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging


class BaseScraper(ABC):
    """Base class for all Meguru Construction scrapers"""
    
    def __init__(self, base_url: str = "https://meguru-construction.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data = []
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the scraper"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch a page with error handling"""
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def sleep(self, seconds: float = 1.0):
        """Sleep to be respectful to the server"""
        time.sleep(seconds)
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate scraped data - must be implemented by subclasses"""
        pass
    
    def save_to_json(self, filename: str, data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save scraped data to JSON file"""
        if data is None:
            data = self.data
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Data saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving data to {filename}: {e}")
    
    def get_data_count(self) -> int:
        """Get the count of scraped data items"""
        return len(self.data)
    
    def clear_data(self) -> None:
        """Clear scraped data"""
        self.data = []
    
    def run(self, output_filename: str) -> List[Dict[str, Any]]:
        """Run the scraper and save results"""
        self.logger.info(f"Starting {self.__class__.__name__}...")
        
        try:
            # Scrape data
            scraped_data = self.scrape()
            
            # Validate and filter data
            valid_data = []
            for item in scraped_data:
                if self.validate_data(item):
                    valid_data.append(item)
                else:
                    self.logger.warning(f"Skipping invalid data: {item.get('url', 'Unknown URL')}")
            
            self.data = valid_data
            
            # Save to file
            self.save_to_json(output_filename)
            
            # Log summary
            self.logger.info(f"Scraping completed successfully!")
            self.logger.info(f"Total items scraped: {len(scraped_data)}")
            self.logger.info(f"Valid items saved: {len(valid_data)}")
            
            return valid_data
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            raise
