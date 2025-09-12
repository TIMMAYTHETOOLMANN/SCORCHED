#!/usr/bin/env python3
"""
Nike Keyword Sentinel Scanner

This script performs intelligent keyword analysis and sentiment scanning
on extracted Nike SEC filings data. It searches for predefined keywords,
analyzes context, identifies risks, opportunities, and business intelligence
patterns across the extracted document corpus.

Features:
- Keyword-based scanning across all extracted data
- Risk sentiment analysis  
- Business intelligence pattern recognition
- Competitive intelligence extraction
- Financial sentiment scoring
- Strategic insight identification

Usage:
    python scripts/keyword_sentinel.py --year YYYY
"""

import argparse
import os
import sys
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter

class NikeKeywordSentinel:
    """
    Nike Keyword Sentinel Scanner
    
    Intelligent keyword analysis and sentiment scanning for SEC filings.
    """
    
    def __init__(self, year: str, base_dir: str = None):
        """Initialize the keyword sentinel."""
        self.year = year
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.extracted_data_dir = os.path.join(self.base_dir, 'extracted_data', str(year))
        self.output_dir = os.path.join(self.base_dir, 'analysis_results', str(year))
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.output_dir, 'keyword_sentinel.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize keyword categories
        self.keyword_categories = self.define_keyword_categories()
        
        # Initialize analysis results
        self.analysis_results = {
            'keyword_matches': defaultdict(list),
            'sentiment_analysis': {},
            'risk_indicators': {},
            'opportunity_indicators': {},
            'competitive_intelligence': {},
            'financial_sentiment': {},
            'strategic_insights': {}
        }
        
    def define_keyword_categories(self) -> Dict[str, List[str]]:
        """Define keyword categories for scanning."""
        return {
            'financial_performance': [
                'revenue', 'sales', 'growth', 'profit', 'margin', 'earnings',
                'income', 'cash flow', 'return on investment', 'roi', 'ebitda',
                'gross profit', 'net income', 'operating income', 'revenue growth'
            ],
            'business_segments': [
                'footwear', 'apparel', 'equipment', 'nike brand', 'jordan brand',
                'converse', 'wholesale', 'direct-to-consumer', 'dtc', 'retail',
                'digital', 'e-commerce', 'nike direct'
            ],
            'geographic_markets': [
                'north america', 'emea', 'greater china', 'asia pacific',
                'latin america', 'international', 'domestic', 'global',
                'emerging markets', 'developed markets'
            ],
            'innovation_technology': [
                'innovation', 'research and development', 'r&d', 'technology',
                'digital transformation', 'sustainability', 'consumer insights',
                'product innovation', 'design', 'materials', 'manufacturing'
            ],
            'risk_factors': [
                'risk', 'uncertainty', 'volatility', 'litigation', 'regulatory',
                'competition', 'economic conditions', 'supply chain', 'currency',
                'cybersecurity', 'pandemic', 'tariff', 'trade war', 'inflation'
            ],
            'competitive_landscape': [
                'adidas', 'under armour', 'puma', 'competition', 'competitive',
                'market share', 'brand strength', 'differentiation',
                'competitive advantage', 'market position', 'rivals'
            ],
            'strategic_initiatives': [
                'strategy', 'strategic', 'acquisition', 'partnership',
                'expansion', 'investment', 'transformation', 'digital strategy',
                'consumer direct acceleration', 'sustainability strategy'
            ],
            'operational_metrics': [
                'inventory', 'supply chain', 'manufacturing', 'distribution',
                'logistics', 'working capital', 'operational efficiency',
                'cost management', 'productivity', 'capacity utilization'
            ],
            'consumer_trends': [
                'consumer behavior', 'lifestyle', 'athleisure', 'wellness',
                'fitness', 'sport', 'athletic', 'fashion', 'trends',
                'demographics', 'millennials', 'gen z', 'digitally native'
            ],
            'esg_sustainability': [
                'sustainability', 'environmental', 'social responsibility',
                'governance', 'diversity', 'inclusion', 'corporate citizenship',
                'climate change', 'carbon footprint', 'circular design'
            ]
        }
    
    def load_extracted_data(self) -> Dict:
        """Load all extracted data from previous extraction steps."""
        self.logger.info(f"Loading extracted data from: {self.extracted_data_dir}")
        
        extracted_data = {
            'pdf_data': {},
            'xls_data': {}
        }
        
        if not os.path.exists(self.extracted_data_dir):
            self.logger.warning(f"Extracted data directory not found: {self.extracted_data_dir}")
            return extracted_data
        
        # Load PDF extraction results
        for file in os.listdir(self.extracted_data_dir):
            if file.endswith('_extracted.json'):
                file_path = os.path.join(self.extracted_data_dir, file)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if '.pdf' in file:
                        extracted_data['pdf_data'][file] = data
                    elif '.xls' in file:
                        extracted_data['xls_data'][file] = data
                        
                    self.logger.info(f"Loaded: {file}")
                except Exception as e:
                    self.logger.error(f"Error loading {file}: {e}")
        
        self.logger.info(f"Loaded {len(extracted_data['pdf_data'])} PDF files and {len(extracted_data['xls_data'])} XLS files")
        return extracted_data
    
    def extract_text_for_analysis(self, extracted_data: Dict) -> str:
        """Extract all available text content for keyword analysis."""
        all_text = ""
        
        # Extract text from PDF data
        for file_name, pdf_data in extracted_data['pdf_data'].items():
            if 'sample_text' in pdf_data:
                all_text += f"\n\n=== {file_name} ===\n"
                all_text += pdf_data['sample_text']
            
            # Also include text analysis keywords if available
            if 'text_analysis' in pdf_data:
                text_analysis = pdf_data['text_analysis']
                for category in ['financial_terms', 'business_terms', 'risk_indicators']:
                    if category in text_analysis:
                        for item in text_analysis[category]:
                            if isinstance(item, dict) and 'term' in item:
                                all_text += f" {item['term']}"
        
        # Extract text from XLS data (column names, sheet names)
        for file_name, xls_data in extracted_data['xls_data'].items():
            if 'sheets' in xls_data:
                all_text += f"\n\n=== {file_name} (Excel) ===\n"
                for sheet_name, sheet_data in xls_data['sheets'].items():
                    all_text += f"\nSheet: {sheet_name}\n"
                    if 'columns' in sheet_data:
                        all_text += " ".join(sheet_data['columns'])
                    
                    # Include sample data if available
                    if 'sample_data' in sheet_data:
                        for row in sheet_data['sample_data'][:3]:  # First 3 rows
                            all_text += " " + " ".join(str(v) for v in row.values() if v)
        
        return all_text
    
    def scan_keywords(self, text: str) -> Dict:
        """Scan text for all keyword categories."""
        self.logger.info("Scanning for keywords across all categories...")
        
        text_lower = text.lower()
        keyword_results = {}
        
        for category, keywords in self.keyword_categories.items():
            category_matches = []
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Find all occurrences with context
                pattern = r'(.{0,50})' + re.escape(keyword_lower) + r'(.{0,50})'
                matches = re.finditer(pattern, text_lower)
                
                match_contexts = []
                for match in matches:
                    context = {
                        'keyword': keyword,
                        'before_context': match.group(1).strip(),
                        'after_context': match.group(2).strip(),
                        'full_context': match.group(0).strip()
                    }
                    match_contexts.append(context)
                
                if match_contexts:
                    category_matches.append({
                        'keyword': keyword,
                        'count': len(match_contexts),
                        'contexts': match_contexts[:5]  # Keep first 5 contexts
                    })
            
            keyword_results[category] = category_matches
            
            # Log category summary
            total_matches = sum(item['count'] for item in category_matches)
            self.logger.info(f"  {category}: {len(category_matches)} unique keywords, {total_matches} total matches")
        
        return keyword_results
    
    def analyze_sentiment_patterns(self, keyword_results: Dict) -> Dict:
        """Analyze sentiment patterns in keyword contexts."""
        self.logger.info("Analyzing sentiment patterns...")
        
        sentiment_analysis = {}
        
        # Define sentiment indicators
        positive_indicators = [
            'growth', 'increase', 'strong', 'successful', 'improved', 'positive',
            'opportunity', 'expansion', 'benefit', 'advantage', 'outperformed',
            'exceeded', 'solid', 'robust', 'healthy', 'momentum'
        ]
        
        negative_indicators = [
            'decline', 'decrease', 'weak', 'challenged', 'negative', 'risk',
            'uncertainty', 'volatility', 'pressure', 'headwind', 'impact',
            'concern', 'difficulty', 'obstacle', 'threat', 'disruption'
        ]
        
        for category, matches in keyword_results.items():
            positive_score = 0
            negative_score = 0
            neutral_score = 0
            
            for match_item in matches:
                for context in match_item['contexts']:
                    context_text = context['full_context'].lower()
                    
                    # Count positive indicators
                    for indicator in positive_indicators:
                        positive_score += context_text.count(indicator)
                    
                    # Count negative indicators
                    for indicator in negative_indicators:
                        negative_score += context_text.count(indicator)
                    
                    neutral_score += 1  # Base neutral score
            
            # Calculate sentiment scores
            total_score = positive_score + negative_score + neutral_score
            if total_score > 0:
                sentiment_analysis[category] = {
                    'positive_score': round(positive_score / total_score, 3),
                    'negative_score': round(negative_score / total_score, 3),
                    'neutral_score': round(neutral_score / total_score, 3),
                    'sentiment_ratio': round((positive_score - negative_score) / total_score, 3),
                    'total_contexts_analyzed': total_score
                }
            else:
                sentiment_analysis[category] = {
                    'positive_score': 0,
                    'negative_score': 0,
                    'neutral_score': 0,
                    'sentiment_ratio': 0,
                    'total_contexts_analyzed': 0
                }
        
        return sentiment_analysis
    
    def identify_risk_indicators(self, keyword_results: Dict) -> Dict:
        """Identify and analyze risk indicators."""
        self.logger.info("Identifying risk indicators...")
        
        risk_analysis = {
            'high_frequency_risks': [],
            'emerging_risks': [],
            'risk_categories': {},
            'risk_sentiment': {}
        }
        
        # Focus on risk factors category
        if 'risk_factors' in keyword_results:
            risk_matches = keyword_results['risk_factors']
            
            # Identify high-frequency risks
            for match_item in risk_matches:
                if match_item['count'] >= 3:  # Appears 3 or more times
                    risk_analysis['high_frequency_risks'].append({
                        'risk': match_item['keyword'],
                        'frequency': match_item['count'],
                        'sample_context': match_item['contexts'][0]['full_context']
                    })
            
            # Categorize risks by type
            risk_categories = {
                'operational': ['supply chain', 'manufacturing', 'cybersecurity'],
                'financial': ['currency', 'inflation', 'economic conditions'],
                'regulatory': ['regulatory', 'litigation', 'tariff'],
                'competitive': ['competition', 'competitive'],
                'external': ['pandemic', 'trade war', 'volatility']
            }
            
            for category, risk_keywords in risk_categories.items():
                category_risks = []
                for match_item in risk_matches:
                    if any(risk_keyword in match_item['keyword'].lower() for risk_keyword in risk_keywords):
                        category_risks.append({
                            'risk': match_item['keyword'],
                            'frequency': match_item['count']
                        })
                
                if category_risks:
                    risk_analysis['risk_categories'][category] = category_risks
        
        return risk_analysis
    
    def identify_opportunities(self, keyword_results: Dict) -> Dict:
        """Identify business opportunities and growth drivers."""
        self.logger.info("Identifying opportunities and growth drivers...")
        
        opportunity_analysis = {
            'growth_drivers': [],
            'strategic_opportunities': [],
            'innovation_areas': [],
            'market_opportunities': []
        }
        
        # Analyze different categories for opportunities
        opportunity_categories = {
            'growth_drivers': ['innovation_technology', 'business_segments'],
            'strategic_opportunities': ['strategic_initiatives', 'geographic_markets'],
            'innovation_areas': ['innovation_technology', 'consumer_trends'],
            'market_opportunities': ['geographic_markets', 'consumer_trends']
        }
        
        for opp_type, categories in opportunity_categories.items():
            opportunities = []
            
            for category in categories:
                if category in keyword_results:
                    for match_item in keyword_results[category]:
                        if match_item['count'] >= 2:  # Mentioned multiple times
                            opportunities.append({
                                'opportunity': match_item['keyword'],
                                'category': category,
                                'frequency': match_item['count'],
                                'sample_context': match_item['contexts'][0]['full_context']
                            })
            
            # Sort by frequency
            opportunities.sort(key=lambda x: x['frequency'], reverse=True)
            opportunity_analysis[opp_type] = opportunities[:10]  # Top 10
        
        return opportunity_analysis
    
    def generate_strategic_insights(self, keyword_results: Dict, sentiment_analysis: Dict) -> Dict:
        """Generate strategic insights from keyword analysis."""
        self.logger.info("Generating strategic insights...")
        
        insights = {
            'key_themes': [],
            'business_focus_areas': [],
            'competitive_positioning': [],
            'strategic_priorities': []
        }
        
        # Identify key themes by total keyword frequency
        theme_scores = {}
        for category, matches in keyword_results.items():
            total_frequency = sum(item['count'] for item in matches)
            theme_scores[category] = total_frequency
        
        # Sort themes by frequency
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        insights['key_themes'] = [
            {'theme': theme, 'total_mentions': score}
            for theme, score in sorted_themes[:8]
        ]
        
        # Business focus areas based on sentiment
        for category, sentiment in sentiment_analysis.items():
            if sentiment['sentiment_ratio'] > 0.1 and sentiment['total_contexts_analyzed'] > 5:
                insights['business_focus_areas'].append({
                    'area': category,
                    'sentiment_score': sentiment['sentiment_ratio'],
                    'confidence': sentiment['total_contexts_analyzed']
                })
        
        # Competitive positioning
        if 'competitive_landscape' in keyword_results:
            competitive_mentions = keyword_results['competitive_landscape']
            insights['competitive_positioning'] = [
                {
                    'element': item['keyword'],
                    'frequency': item['count'],
                    'context': item['contexts'][0]['full_context']
                }
                for item in competitive_mentions[:5]
            ]
        
        return insights
    
    def process_keyword_analysis(self) -> bool:
        """Process complete keyword analysis pipeline."""
        self.logger.info(f"=== Starting Keyword Sentinel Analysis for year {self.year} ===")
        
        # Load extracted data
        extracted_data = self.load_extracted_data()
        
        if not extracted_data['pdf_data'] and not extracted_data['xls_data']:
            self.logger.warning("No extracted data found to analyze")
            return False
        
        # Extract text for analysis
        analysis_text = self.extract_text_for_analysis(extracted_data)
        
        if not analysis_text.strip():
            self.logger.warning("No text content found for analysis")
            return False
        
        self.logger.info(f"Analyzing {len(analysis_text)} characters of text content")
        
        # Run keyword scanning
        keyword_results = self.scan_keywords(analysis_text)
        self.analysis_results['keyword_matches'] = keyword_results
        
        # Run sentiment analysis
        sentiment_analysis = self.analyze_sentiment_patterns(keyword_results)
        self.analysis_results['sentiment_analysis'] = sentiment_analysis
        
        # Identify risks and opportunities
        risk_indicators = self.identify_risk_indicators(keyword_results)
        self.analysis_results['risk_indicators'] = risk_indicators
        
        opportunity_indicators = self.identify_opportunities(keyword_results)
        self.analysis_results['opportunity_indicators'] = opportunity_indicators
        
        # Generate strategic insights
        strategic_insights = self.generate_strategic_insights(keyword_results, sentiment_analysis)
        self.analysis_results['strategic_insights'] = strategic_insights
        
        # Save results
        self.save_analysis_results()
        
        self.logger.info(f"=== Keyword Sentinel Analysis complete for year {self.year} ===")
        return True
    
    def save_analysis_results(self) -> str:
        """Save keyword analysis results."""
        results_file = os.path.join(self.output_dir, 'keyword_sentinel_analysis.json')
        
        full_results = {
            'year': self.year,
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'keyword_categories_analyzed': len(self.keyword_categories),
                'total_keywords_defined': sum(len(keywords) for keywords in self.keyword_categories.values()),
                'output_directory': self.output_dir
            },
            'analysis_results': self.analysis_results,
            'summary': self.generate_analysis_summary()
        }
        
        with open(results_file, 'w') as f:
            json.dump(full_results, f, indent=2, default=str)
        
        self.logger.info(f"Analysis results saved to: {results_file}")
        return results_file
    
    def generate_analysis_summary(self) -> Dict:
        """Generate a summary of the analysis results."""
        summary = {
            'total_keyword_categories': len(self.analysis_results['keyword_matches']),
            'categories_with_matches': 0,
            'total_unique_keywords_found': 0,
            'total_keyword_occurrences': 0,
            'highest_sentiment_categories': [],
            'top_risk_indicators': [],
            'top_opportunities': []
        }
        
        # Count categories with matches
        for category, matches in self.analysis_results['keyword_matches'].items():
            if matches:
                summary['categories_with_matches'] += 1
                summary['total_unique_keywords_found'] += len(matches)
                summary['total_keyword_occurrences'] += sum(item['count'] for item in matches)
        
        # Top sentiment categories
        if self.analysis_results['sentiment_analysis']:
            sentiment_scores = [(cat, data['sentiment_ratio']) 
                              for cat, data in self.analysis_results['sentiment_analysis'].items()
                              if data['total_contexts_analyzed'] > 0]
            sentiment_scores.sort(key=lambda x: x[1], reverse=True)
            summary['highest_sentiment_categories'] = sentiment_scores[:5]
        
        # Top risks
        if 'high_frequency_risks' in self.analysis_results['risk_indicators']:
            summary['top_risk_indicators'] = [
                risk['risk'] for risk in self.analysis_results['risk_indicators']['high_frequency_risks'][:5]
            ]
        
        # Top opportunities
        if 'growth_drivers' in self.analysis_results['opportunity_indicators']:
            summary['top_opportunities'] = [
                opp['opportunity'] for opp in self.analysis_results['opportunity_indicators']['growth_drivers'][:5]
            ]
        
        return summary


def main():
    """Main execution function for the keyword sentinel."""
    parser = argparse.ArgumentParser(description='Nike Keyword Sentinel Scanner')
    parser.add_argument('--year', required=True, help='Year to process (e.g., 2019)')
    parser.add_argument('--base-dir', help='Base directory path (optional)')
    
    args = parser.parse_args()
    
    print(f"Nike Keyword Sentinel Scanner - Year {args.year}")
    print("=" * 50)
    
    # Initialize sentinel
    sentinel = NikeKeywordSentinel(args.year, args.base_dir)
    
    # Process keyword analysis
    success = sentinel.process_keyword_analysis()
    
    if success:
        print(f"\n✅ Keyword analysis completed successfully for year {args.year}!")
        print(f"📁 Results saved to: {sentinel.output_dir}")
        
        # Display summary
        summary = sentinel.analysis_results.get('strategic_insights', {})
        if 'key_themes' in summary:
            print(f"\n📊 Key Themes Identified:")
            for theme in summary['key_themes'][:5]:
                print(f"  • {theme['theme']}: {theme['total_mentions']} mentions")
        
        return 0
    else:
        print(f"\n❌ Keyword analysis failed for year {args.year}!")
        return 1


if __name__ == "__main__":
    sys.exit(main())