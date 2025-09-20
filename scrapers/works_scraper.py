#!/usr/bin/env python3
"""
Works scraper for Meguru Construction website
"""

import re
from urllib.parse import urljoin
from typing import List, Dict, Any
from .base import BaseScraper


class WorksScraper(BaseScraper):
    """Scraper for construction works/projects"""
    
    def __init__(self, max_pages: int = 4):
        super().__init__()
        self.works_url = f"{self.base_url}/works/"
        self.max_pages = max_pages
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape works data from the works pages"""
        # Get all project links
        project_links = self._get_all_project_links()
        self.logger.info(f"Found {len(project_links)} project pages")
        
        # Scrape each project
        projects_data = []
        for i, link in enumerate(project_links, 1):
            self.logger.info(f"Processing {i}/{len(project_links)}: {link}")
            project_data = self._extract_project_data(link)
            if project_data:
                projects_data.append(project_data)
            self.sleep(1)  # Be respectful to the server
        
        return projects_data
    
    def _get_all_project_links(self) -> List[str]:
        """Get all project links from works pages (limited to max_pages)"""
        all_links = []
        
        for page_num in range(1, self.max_pages + 1):
            if page_num == 1:
                url = self.works_url
            else:
                url = f"{self.works_url}page/{page_num}/"
            
            self.logger.info(f"Fetching page {page_num}: {url}")
            content = self.get_page(url)
            if not content:
                break
                
            links = self._extract_project_links(content)
            if not links:
                break
                
            all_links.extend(links)
            self.sleep(1)
        
        return list(set(all_links))  # Remove duplicates
    
    def _extract_project_links(self, page_content: str) -> List[str]:
        """Extract project links from works listing page"""
        soup = self.parse_html(page_content)
        links = []
        
        # Find all "MORE" links that lead to project pages
        more_links = soup.find_all('a', href=True)
        for link in more_links:
            href = link.get('href')
            if href and '/works/' in href and href != self.works_url:
                # Skip pagination URLs
                if '/page/' in href:
                    continue
                full_url = urljoin(self.base_url, href)
                if full_url not in links:
                    links.append(full_url)
        
        return links
    
    def _extract_project_data(self, url: str) -> Dict[str, Any]:
        """Extract project data from a project page"""
        content = self.get_page(url)
        if not content:
            return None
            
        soup = self.parse_html(content)
        
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
        
        # Extract structured data using regex patterns
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
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate project data"""
        if not data:
            return False
        
        # Check if at least location and project_name are present
        required_fields = ['location', 'project_name']
        for field in required_fields:
            if not data.get(field, '').strip():
                return False
        
        return True
    
    def get_projects_summary(self) -> Dict[str, Any]:
        """Get summary of scraped projects"""
        if not self.data:
            return {}
        
        # Count projects by location (prefecture)
        location_counts = {}
        completion_years = []
        
        for project in self.data:
            location = project.get('location', '')
            if location:
                # Extract prefecture (first part before city)
                prefecture = location.split('区')[0] + '区' if '区' in location else location.split('市')[0] + '市' if '市' in location else location
                location_counts[prefecture] = location_counts.get(prefecture, 0) + 1
            
            completion_date = project.get('completion_date', '')
            if completion_date and '年' in completion_date:
                year_match = re.search(r'(\d{4})年', completion_date)
                if year_match:
                    completion_years.append(int(year_match.group(1)))
        
        summary = {
            'total_projects': len(self.data),
            'locations': location_counts,
            'completion_years': {
                'min': min(completion_years) if completion_years else None,
                'max': max(completion_years) if completion_years else None,
                'count': len(completion_years)
            }
        }
        
        return summary
    
    def run(self, output_filename: str = "output/meguru_projects.json") -> List[Dict[str, Any]]:
        """Run the works scraper"""
        result = super().run(output_filename)
        
        # Print summary
        summary = self.get_projects_summary()
        if summary:
            self.logger.info("Projects Summary:")
            self.logger.info(f"  Total projects: {summary['total_projects']}")
            self.logger.info(f"  Locations: {summary['locations']}")
            if summary['completion_years']['count'] > 0:
                self.logger.info(f"  Completion years: {summary['completion_years']['min']}-{summary['completion_years']['max']}")
        
        return result


def main():
    """Main function for testing works scraper"""
    scraper = WorksScraper(max_pages=2)  # Test with 2 pages
    try:
        data = scraper.run("output/meguru_projects_test.json")
        
        if data:
            print(f"\nSample project data:")
            print(f"Project: {data[0]['project_name']}")
            print(f"Location: {data[0]['location']}")
            print(f"Completion: {data[0]['completion_date']}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
