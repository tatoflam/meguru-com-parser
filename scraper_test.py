#!/usr/bin/env python3
"""
Meguru Construction Works Scraper - Test Version
Limited to first few pages for testing
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse
import sys


class MeguruScraper:
    def __init__(self, max_pages=3):
        self.base_url = "https://meguru-construction.com"
        self.works_url = "https://meguru-construction.com/works/"
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.projects = []

    def get_page(self, url):
        """Fetch a page with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_project_links(self, page_content):
        """Extract project links from works listing page"""
        soup = BeautifulSoup(page_content, 'html.parser')
        links = []
        
        # Find all "MORE" links that lead to project pages
        more_links = soup.find_all('a', href=True)
        for link in more_links:
            href = link.get('href')
            if href and '/works/' in href and href != self.works_url:
                full_url = urljoin(self.base_url, href)
                if full_url not in links:
                    links.append(full_url)
        
        return links

    def get_all_project_links(self):
        """Get all project links from limited pages"""
        all_links = []
        page_num = 1
        
        while page_num <= self.max_pages:
            if page_num == 1:
                url = self.works_url
            else:
                url = f"{self.works_url}page/{page_num}/"
            
            print(f"Fetching page {page_num}: {url}")
            content = self.get_page(url)
            if not content:
                break
                
            links = self.extract_project_links(content)
            if not links:
                break
                
            all_links.extend(links)
            page_num += 1
            time.sleep(1)  # Be respectful to the server
        
        return list(set(all_links))  # Remove duplicates

    def extract_project_data(self, url):
        """Extract project data from a project page"""
        print(f"Scraping: {url}")
        content = self.get_page(url)
        if not content:
            return None
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract project name
        title_elem = soup.find('h3')
        project_name = ""
        if title_elem:
            project_name = title_elem.get_text().strip()
        
        # Initialize data structure
        project_data = {
            "url": url,
            "project_name": project_name,
            "location": "",
            "completion_date": "",
            "site_area": "",
            "floor_area": "",
            "volume_consumption": "",
            "structure": "",
            "floors": "",
            "units": "",
            "comment": ""
        }
        
        # Extract structured data
        # The data appears to be in a specific format after the images
        text_content = soup.get_text()
        
        # Define patterns to extract each field
        patterns = {
            "location": r"所在地\s*([^\n]+)",
            "completion_date": r"竣工年月\s*([^\n]+)",
            "site_area": r"敷地面積\s*([^\n]+)",
            "floor_area": r"延床面積\s*([^\n]+)",
            "volume_consumption": r"容積消化\s*([^\n]+)",
            "structure": r"構造\s*([^\n]+)",
            "floors": r"階数\s*([^\n]+)",
            "units": r"戸数\s*([^\n]+)",
            "comment": r"コメント\s*([^\n]+)"
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text_content)
            if match:
                project_data[field] = match.group(1).strip()
        
        return project_data

    def scrape_all_projects(self):
        """Main scraping function"""
        print(f"Starting to scrape Meguru Construction projects (max {self.max_pages} pages)...")
        
        # Get all project links
        project_links = self.get_all_project_links()
        print(f"Found {len(project_links)} project pages")
        
        # Scrape each project
        for i, link in enumerate(project_links, 1):
            print(f"Processing {i}/{len(project_links)}: {link}")
            project_data = self.extract_project_data(link)
            if project_data:
                self.projects.append(project_data)
            time.sleep(1)  # Be respectful to the server
        
        print(f"Successfully scraped {len(self.projects)} projects")
        return self.projects

    def save_to_json(self, filename="output/meguru_projects_test.json"):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filename}")


def main():
    scraper = MeguruScraper(max_pages=2)  # Test with just 2 pages
    
    try:
        # Scrape all projects
        projects = scraper.scrape_all_projects()
        
        # Save to JSON
        scraper.save_to_json()
        
        # Print summary
        print(f"\nScraping completed successfully!")
        print(f"Total projects scraped: {len(projects)}")
        
        if projects:
            print("\nSample project data:")
            print(json.dumps(projects[0], ensure_ascii=False, indent=2))
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
