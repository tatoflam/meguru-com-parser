#!/usr/bin/env python3
"""
Unified CLI interface for Meguru Construction scrapers
"""

import argparse
import sys
import os
from typing import Dict, Any

# Add scrapers directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.works_scraper import WorksScraper
from scrapers.faq_scraper import FAQScraper


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Meguru Construction Website Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py works                    # Scrape works/projects (4 pages)
  python main.py works --pages 2          # Scrape works (2 pages only)
  python main.py faq                      # Scrape FAQ
  python main.py all                      # Scrape both works and FAQ
  python main.py works --output custom.json  # Custom output filename
        """
    )
    
    parser.add_argument(
        'target',
        choices=['works', 'faq', 'all'],
        help='What to scrape: works (construction projects), faq (Q&A), or all'
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=4,
        help='Number of pages to scrape for works (default: 4)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output filename (default: auto-generated based on target)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory (default: output)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


def ensure_output_dir(output_dir: str) -> None:
    """Ensure output directory exists"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")


def scrape_works(args) -> Dict[str, Any]:
    """Scrape construction works/projects"""
    print(f"Scraping construction works (max {args.pages} pages)...")
    
    scraper = WorksScraper(max_pages=args.pages)
    
    if args.output:
        output_file = os.path.join(args.output_dir, args.output)
    else:
        output_file = os.path.join(args.output_dir, "meguru_projects.json")
    
    data = scraper.run(output_file)
    
    return {
        'type': 'works',
        'count': len(data),
        'file': output_file,
        'data': data
    }


def scrape_faq(args) -> Dict[str, Any]:
    """Scrape FAQ"""
    print("Scraping FAQ...")
    
    scraper = FAQScraper()
    
    if args.output:
        output_file = os.path.join(args.output_dir, args.output)
    else:
        output_file = os.path.join(args.output_dir, "meguru_faq.json")
    
    data = scraper.run(output_file)
    
    return {
        'type': 'faq',
        'count': len(data),
        'file': output_file,
        'data': data
    }


def scrape_all(args) -> Dict[str, Any]:
    """Scrape both works and FAQ"""
    print("Scraping all content (works + FAQ)...")
    
    results = {}
    
    # Scrape works
    works_args = argparse.Namespace(**vars(args))
    works_args.output = None  # Use default filenames
    works_result = scrape_works(works_args)
    results['works'] = works_result
    
    # Scrape FAQ
    faq_args = argparse.Namespace(**vars(args))
    faq_args.output = None  # Use default filenames
    faq_result = scrape_faq(faq_args)
    results['faq'] = faq_result
    
    return results


def print_summary(results) -> None:
    """Print summary of scraping results"""
    print("\n" + "="*50)
    print("SCRAPING SUMMARY")
    print("="*50)
    
    if isinstance(results, dict) and 'type' in results:
        # Single scraper result
        print(f"Target: {results['type'].upper()}")
        print(f"Items scraped: {results['count']}")
        print(f"Output file: {results['file']}")
        
        if results['data']:
            print(f"\nSample data:")
            sample = results['data'][0]
            if results['type'] == 'works':
                print(f"  Project: {sample.get('project_name', 'N/A')}")
                print(f"  Location: {sample.get('location', 'N/A')}")
                print(f"  Completion: {sample.get('completion_date', 'N/A')}")
            elif results['type'] == 'faq':
                print(f"  Category: {sample.get('category', 'N/A')}")
                print(f"  Question: {sample.get('question', 'N/A')[:50]}...")
                print(f"  Answer: {sample.get('answer', 'N/A')[:50]}...")
    
    else:
        # Multiple scraper results
        total_items = 0
        for scraper_type, result in results.items():
            print(f"{scraper_type.upper()}:")
            print(f"  Items scraped: {result['count']}")
            print(f"  Output file: {result['file']}")
            total_items += result['count']
        
        print(f"\nTotal items scraped: {total_items}")


def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Ensure output directory exists
    ensure_output_dir(args.output_dir)
    
    try:
        # Route to appropriate scraper
        if args.target == 'works':
            results = scrape_works(args)
        elif args.target == 'faq':
            results = scrape_faq(args)
        elif args.target == 'all':
            results = scrape_all(args)
        else:
            print(f"Unknown target: {args.target}")
            sys.exit(1)
        
        # Print summary
        print_summary(results)
        
        print(f"\nScraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during scraping: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
