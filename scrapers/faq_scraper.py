#!/usr/bin/env python3
"""
FAQ scraper for Meguru Construction website
"""

import re
from typing import List, Dict, Any
from .base import BaseScraper


class FAQScraper(BaseScraper):
    """Scraper for FAQ page"""
    
    def __init__(self):
        super().__init__()
        self.faq_url = f"{self.base_url}/faq/"
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape FAQ data from the FAQ page"""
        content = self.get_page(self.faq_url)
        if not content:
            return []
        
        soup = self.parse_html(content)
        faq_data = []
        
        # Find all category sections
        categories = self._extract_categories(soup)
        
        for category in categories:
            category_name = category['name']
            category_section = category['section']
            
            self.logger.info(f"Processing category: {category_name}")
            
            # Extract Q&A pairs for this category
            qa_pairs = self._extract_qa_pairs(category_section, category_name)
            faq_data.extend(qa_pairs)
        
        return faq_data
    
    def _extract_categories(self, soup) -> List[Dict[str, Any]]:
        """Extract category information from the page"""
        categories = []
        
        # Find category headers (h2 with em tags)
        category_headers = soup.find_all('h2')
        
        for header in category_headers:
            em_tag = header.find('em')
            if em_tag:
                category_name = em_tag.get_text().strip()
                
                # Find the parent div that contains this category's content
                category_section = header.find_parent('div')
                if category_section:
                    categories.append({
                        'name': category_name,
                        'section': category_section
                    })
        
        return categories
    
    def _extract_qa_pairs(self, category_section, category_name: str) -> List[Dict[str, Any]]:
        """Extract Q&A pairs from a category section"""
        qa_pairs = []
        
        # Find all divs that might contain Q&A content
        # Based on the structure, Q and A are in separate divs
        divs = category_section.find_all('div', recursive=True)
        
        current_question = None
        question_index = 1
        
        for div in divs:
            text = div.get_text().strip()
            
            # Skip empty divs or divs with only whitespace
            if not text or len(text) < 2:
                continue
            
            # Check if this div contains a question (starts with 'Q')
            if text.startswith('Q') and len(text) > 2:
                # Extract question text (remove 'Q' prefix)
                question_text = text[1:].strip()
                if question_text:
                    current_question = {
                        'category': category_name,
                        'question_number': question_index,
                        'question': question_text,
                        'answer': ''
                    }
                    question_index += 1
            
            # Check if this div contains an answer (starts with 'A')
            elif text.startswith('A') and len(text) > 2 and current_question:
                # Extract answer text (remove 'A' prefix)
                answer_text = text[1:].strip()
                if answer_text:
                    current_question['answer'] = answer_text
                    qa_pairs.append(current_question)
                    current_question = None
        
        return qa_pairs
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate FAQ data"""
        required_fields = ['category', 'question', 'answer']
        
        for field in required_fields:
            if not data.get(field, '').strip():
                return False
        
        # Ensure question and answer have meaningful content
        if len(data['question']) < 5 or len(data['answer']) < 10:
            return False
        
        return True
    
    def get_categories_summary(self) -> Dict[str, int]:
        """Get summary of questions per category"""
        summary = {}
        for item in self.data:
            category = item.get('category', 'Unknown')
            summary[category] = summary.get(category, 0) + 1
        return summary
    
    def run(self, output_filename: str = "output/meguru_faq.json") -> List[Dict[str, Any]]:
        """Run the FAQ scraper"""
        result = super().run(output_filename)
        
        # Print category summary
        summary = self.get_categories_summary()
        self.logger.info("FAQ Categories Summary:")
        for category, count in summary.items():
            self.logger.info(f"  {category}: {count} questions")
        
        return result


def main():
    """Main function for testing FAQ scraper"""
    scraper = FAQScraper()
    try:
        data = scraper.run()
        
        if data:
            print(f"\nSample FAQ data:")
            print(f"Category: {data[0]['category']}")
            print(f"Question: {data[0]['question']}")
            print(f"Answer: {data[0]['answer'][:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
