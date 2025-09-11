#!/usr/bin/env python3
"""
Nike Data Triangulator Auto Executor

This script triangulates multiple Nike data sources to provide comprehensive
business intelligence analysis. It combines facility data, geographic information,
and operational metrics to identify patterns, relationships, and strategic insights.

Features:
- Cross-references facility locations with operational capacity
- Analyzes geographic distribution and supply chain patterns  
- Identifies facility clusters and regional concentrations
- Calculates operational efficiency metrics
- Generates consolidated analysis reports

Usage:
    python scripts/triangulator_auto_executor.py [options]
"""

import json
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Add parent directory to path to import from facility_map_generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class NikeDataTriangulator:
    """
    Nike Data Triangulation Engine
    
    Integrates multiple data sources to provide comprehensive business analysis.
    """
    
    def __init__(self, base_dir: str = None):
        """Initialize the triangulator with base directory."""
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.facility_data_file = os.path.join(self.base_dir, 'imap_export.xls')
        self.json_data_file = os.path.join(self.base_dir, 'facility_data.json')
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.base_dir, 'triangulator.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize data containers
        self.facility_df = None
        self.geographic_data = None
        self.analysis_results = {}
        
    def load_data_sources(self) -> bool:
        """Load all available Nike data sources."""
        self.logger.info("Loading Nike data sources...")
        
        try:
            # Load facility Excel data
            if os.path.exists(self.facility_data_file):
                self.facility_df = pd.read_excel(self.facility_data_file, header=1)
                self.logger.info(f"Loaded {len(self.facility_df)} facility records from Excel")
            else:
                self.logger.warning(f"Facility Excel file not found: {self.facility_data_file}")
                return False
                
            # Load JSON geographic data if available
            if os.path.exists(self.json_data_file):
                with open(self.json_data_file, 'r') as f:
                    self.geographic_data = json.load(f)
                self.logger.info("Loaded geographic coordinate data from JSON")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data sources: {e}")
            return False
    
    def triangulate_facility_clusters(self) -> Dict:
        """Identify and analyze facility clusters by geographic region."""
        self.logger.info("Triangulating facility clusters...")
        
        if self.facility_df is None:
            return {}
            
        try:
            # Group facilities by country and region
            country_analysis = self.facility_df.groupby('Country / Region').agg({
                'Factory Name': 'count',
                'Total Workers': 'sum',
                '% Female Workers': 'mean',
                '% Migrant Workers': 'mean'
            }).round(2)
            
            # Rename columns for clarity
            country_analysis.columns = [
                'Facility_Count', 'Total_Workers', 'Avg_Female_Percent', 'Avg_Migrant_Percent'
            ]
            
            # Sort by facility count
            country_analysis = country_analysis.sort_values('Facility_Count', ascending=False)
            
            self.analysis_results['facility_clusters'] = country_analysis.to_dict('index')
            
            self.logger.info(f"Analyzed {len(country_analysis)} countries with facilities")
            return self.analysis_results['facility_clusters']
            
        except Exception as e:
            self.logger.error(f"Error in facility cluster analysis: {e}")
            return {}
    
    def triangulate_operational_patterns(self) -> Dict:
        """Analyze operational patterns across different facility types."""
        self.logger.info("Triangulating operational patterns...")
        
        if self.facility_df is None:
            return {}
            
        try:
            # Analyze by facility type
            type_analysis = self.facility_df.groupby('Factory Type').agg({
                'Factory Name': 'count',
                'Total Workers': ['sum', 'mean', 'median'],
                '% Female Workers': 'mean',
                '% Migrant Workers': 'mean'
            }).round(2)
            
            # Flatten multi-level columns
            type_analysis.columns = ['_'.join(col).strip() for col in type_analysis.columns.values]
            
            # Analyze by product type
            if 'Product Type Type' in self.facility_df.columns:
                product_analysis = self.facility_df.groupby('Product Type Type').agg({
                    'Factory Name': 'count',
                    'Total Workers': 'sum',
                    '% Female Workers': 'mean'
                }).round(2)
                
                self.analysis_results['product_patterns'] = product_analysis.to_dict('index')
            
            self.analysis_results['operational_patterns'] = type_analysis.to_dict('index')
            
            return self.analysis_results['operational_patterns']
            
        except Exception as e:
            self.logger.error(f"Error in operational pattern analysis: {e}")
            return {}
    
    def triangulate_workforce_metrics(self) -> Dict:
        """Calculate comprehensive workforce metrics and patterns."""
        self.logger.info("Triangulating workforce metrics...")
        
        if self.facility_df is None:
            return {}
            
        try:
            # Calculate summary workforce metrics
            workforce_metrics = {
                'total_facilities': len(self.facility_df),
                'total_workers': self.facility_df['Total Workers'].sum(),
                'average_facility_size': round(self.facility_df['Total Workers'].mean(), 1),
                'median_facility_size': self.facility_df['Total Workers'].median(),
                'largest_facility': self.facility_df['Total Workers'].max(),
                'smallest_facility': self.facility_df['Total Workers'].min(),
                'avg_female_percentage': round(self.facility_df['% Female Workers'].mean(), 2),
                'avg_migrant_percentage': round(self.facility_df['% Migrant Workers'].mean(), 2),
                'facilities_high_female_workforce': len(
                    self.facility_df[self.facility_df['% Female Workers'] > 70]
                ),
                'facilities_high_migrant_workforce': len(
                    self.facility_df[self.facility_df['% Migrant Workers'] > 30]
                )
            }
            
            # Identify workforce composition patterns
            workforce_metrics['workforce_composition'] = {
                'primarily_female': len(self.facility_df[self.facility_df['% Female Workers'] > 60]),
                'balanced_gender': len(self.facility_df[
                    (self.facility_df['% Female Workers'] >= 40) & 
                    (self.facility_df['% Female Workers'] <= 60)
                ]),
                'primarily_male': len(self.facility_df[self.facility_df['% Female Workers'] < 40]),
                'high_migrant': len(self.facility_df[self.facility_df['% Migrant Workers'] > 50]),
                'low_migrant': len(self.facility_df[self.facility_df['% Migrant Workers'] < 10])
            }
            
            self.analysis_results['workforce_metrics'] = workforce_metrics
            return workforce_metrics
            
        except Exception as e:
            self.logger.error(f"Error in workforce metrics calculation: {e}")
            return {}
    
    def triangulate_strategic_insights(self) -> Dict:
        """Generate strategic business insights from triangulated data."""
        self.logger.info("Generating strategic insights...")
        
        if self.facility_df is None:
            return {}
            
        try:
            insights = {
                'supply_chain_distribution': {},
                'operational_efficiency': {},
                'risk_assessment': {},
                'growth_opportunities': {}
            }
            
            # Supply chain distribution insights
            top_countries = self.facility_df['Country / Region'].value_counts().head(5)
            insights['supply_chain_distribution'] = {
                'top_manufacturing_countries': top_countries.to_dict(),
                'geographic_concentration': f"{top_countries.head(3).sum()}/{len(self.facility_df)} facilities in top 3 countries",
                'diversification_score': len(self.facility_df['Country / Region'].unique())
            }
            
            # Operational efficiency patterns
            efficiency_metrics = self.facility_df.groupby('Country / Region')['Total Workers'].agg(['count', 'sum', 'mean']).round(1)
            insights['operational_efficiency'] = {
                'most_efficient_regions': efficiency_metrics.sort_values('mean', ascending=False).head(3).to_dict('index'),
                'largest_workforce_concentrations': efficiency_metrics.sort_values('sum', ascending=False).head(3).to_dict('index')
            }
            
            # Risk assessment
            migrant_risk = self.facility_df.groupby('Country / Region')['% Migrant Workers'].mean().sort_values(ascending=False)
            insights['risk_assessment'] = {
                'high_migrant_dependency': migrant_risk.head(3).to_dict(),
                'workforce_concentration_risk': f"Top country represents {(top_countries.iloc[0]/len(self.facility_df)*100):.1f}% of facilities"
            }
            
            self.analysis_results['strategic_insights'] = insights
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating strategic insights: {e}")
            return {}
    
    def generate_triangulation_report(self, output_file: str = None) -> str:
        """Generate comprehensive triangulation report."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.base_dir, f'nike_triangulation_report_{timestamp}.json')
        
        self.logger.info(f"Generating triangulation report: {output_file}")
        
        try:
            report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'data_sources': [
                        self.facility_data_file,
                        self.json_data_file if self.geographic_data else None
                    ],
                    'total_facilities_analyzed': len(self.facility_df) if self.facility_df is not None else 0
                },
                'analysis_results': self.analysis_results,
                'summary': {
                    'countries_with_facilities': len(self.facility_df['Country / Region'].unique()) if self.facility_df is not None else 0,
                    'facility_types': list(self.facility_df['Factory Type'].unique()) if self.facility_df is not None else [],
                    'total_workforce': self.facility_df['Total Workers'].sum() if self.facility_df is not None else 0
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Triangulation report saved to: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return ""
    
    def execute_full_triangulation(self) -> bool:
        """Execute complete triangulation analysis pipeline."""
        self.logger.info("=== Starting Nike Data Triangulation Analysis ===")
        
        # Step 1: Load data
        if not self.load_data_sources():
            self.logger.error("Failed to load data sources")
            return False
        
        # Step 2: Execute triangulation analyses
        self.triangulate_facility_clusters()
        self.triangulate_operational_patterns() 
        self.triangulate_workforce_metrics()
        self.triangulate_strategic_insights()
        
        # Step 3: Generate report
        report_file = self.generate_triangulation_report()
        
        if report_file:
            self.logger.info("=== Triangulation Analysis Complete ===")
            self.logger.info(f"Results saved to: {report_file}")
            return True
        else:
            self.logger.error("Failed to generate triangulation report")
            return False


def main():
    """Main execution function for the triangulator auto executor."""
    print("Nike Data Triangulator Auto Executor")
    print("=" * 50)
    
    # Initialize triangulator
    triangulator = NikeDataTriangulator()
    
    # Execute full triangulation
    success = triangulator.execute_full_triangulation()
    
    if success:
        print("\n✅ Triangulation analysis completed successfully!")
        print("\nKey Results:")
        
        # Display summary results
        if 'workforce_metrics' in triangulator.analysis_results:
            metrics = triangulator.analysis_results['workforce_metrics']
            print(f"  • Total Facilities: {metrics.get('total_facilities', 'N/A')}")
            print(f"  • Total Workers: {metrics.get('total_workers', 'N/A'):,}")
            print(f"  • Average Facility Size: {metrics.get('average_facility_size', 'N/A')} workers")
            print(f"  • Countries with Facilities: {len(triangulator.facility_df['Country / Region'].unique()) if triangulator.facility_df is not None else 'N/A'}")
        
        if 'facility_clusters' in triangulator.analysis_results:
            clusters = triangulator.analysis_results['facility_clusters']
            print(f"\nTop Manufacturing Countries:")
            for country, data in list(clusters.items())[:5]:
                print(f"  • {country}: {data['Facility_Count']} facilities, {data['Total_Workers']:,} workers")
        
        return 0
    else:
        print("\n❌ Triangulation analysis failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())