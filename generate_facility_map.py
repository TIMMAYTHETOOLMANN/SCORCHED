#!/usr/bin/env python3
"""
Geographical Bubble Map Generator for Facility Locations

This script reads facility data from the Excel file and creates an interactive
geographical bubble map showing two facility types:
1. FINISHED GOODS facilities
2. FINISHED GOODS - COMPONENTS facilities

The map visualizes their locations and distances between facilities.
"""

import pandas as pd
import folium
from folium import plugins
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
import json
import os

# Constants
EXCEL_FILE = 'imap_export.xls'
OUTPUT_MAP = 'facility_locations_map.html'
CACHE_FILE = 'geocoding_cache.json'

# Facility type filters
FINISHED_GOODS_TYPE = 'FINISHED GOODS'
COMPONENTS_TYPE = 'FINISHED GOODS - COMPONENTS'

# Map styling
FINISHED_GOODS_COLOR = '#2E86AB'  # Blue
COMPONENTS_COLOR = '#A23B72'      # Purple
MAP_CENTER = [20.0, 0.0]          # Default center

class FacilityMapper:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="facility_mapper")
        self.geocoding_cache = self.load_cache()
        
    def load_cache(self):
        """Load geocoding cache to avoid repeated API calls"""
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_cache(self):
        """Save geocoding cache"""
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.geocoding_cache, f, indent=2)
    
    def geocode_location(self, city, country):
        """Geocode a city, country combination to lat/lng"""
        # Create cache key
        location_key = f"{city}, {country}".strip().lower()
        
        if location_key in self.geocoding_cache:
            return self.geocoding_cache[location_key]
        
        try:
            # Try full address first
            location = self.geocoder.geocode(f"{city}, {country}", timeout=10)
            
            if not location:
                # Try just country if city fails
                location = self.geocoder.geocode(country, timeout=10)
            
            if location:
                result = {'lat': location.latitude, 'lng': location.longitude}
                self.geocoding_cache[location_key] = result
                print(f"Geocoded: {city}, {country} -> {result}")
                # Add delay to respect rate limits
                time.sleep(1)
                return result
            else:
                print(f"Failed to geocode: {city}, {country}")
                return None
                
        except Exception as e:
            print(f"Error geocoding {city}, {country}: {e}")
            return None
    
    def load_and_process_data(self):
        """Load Excel data and process facility information"""
        print("Loading Excel data...")
        df = pd.read_excel(EXCEL_FILE, engine='xlrd', header=1)
        
        # Filter for the two facility types
        finished_goods = df[df['Factory Type'] == FINISHED_GOODS_TYPE].copy()
        components = df[df['Factory Type'] == COMPONENTS_TYPE].copy()
        
        print(f"Found {len(finished_goods)} FINISHED GOODS facilities")
        print(f"Found {len(components)} FINISHED GOODS - COMPONENTS facilities")
        
        return finished_goods, components
    
    def add_coordinates(self, df):
        """Add lat/lng coordinates to dataframe"""
        coordinates = []
        
        for idx, row in df.iterrows():
            city = str(row['City']).strip()
            country = str(row['Country / Region']).strip()
            
            # Skip if city or country is NaN or empty
            if pd.isna(row['City']) or pd.isna(row['Country / Region']):
                coordinates.append({'lat': None, 'lng': None})
                continue
            
            coords = self.geocode_location(city, country)
            if coords:
                coordinates.append(coords)
            else:
                coordinates.append({'lat': None, 'lng': None})
        
        df['latitude'] = [c['lat'] for c in coordinates]
        df['longitude'] = [c['lng'] for c in coordinates]
        
        # Remove rows without coordinates
        df_with_coords = df.dropna(subset=['latitude', 'longitude'])
        print(f"Successfully geocoded {len(df_with_coords)} out of {len(df)} facilities")
        
        return df_with_coords
    
    def calculate_distances(self, df1, df2):
        """Calculate distances between facilities in two groups"""
        distances = []
        
        for idx1, row1 in df1.iterrows():
            for idx2, row2 in df2.iterrows():
                coord1 = (row1['latitude'], row1['longitude'])
                coord2 = (row2['latitude'], row2['longitude'])
                
                distance = geodesic(coord1, coord2).kilometers
                distances.append({
                    'facility1': row1['Factory Name'],
                    'facility2': row2['Factory Name'],
                    'lat1': row1['latitude'],
                    'lng1': row1['longitude'],
                    'lat2': row2['latitude'],
                    'lng2': row2['longitude'],
                    'distance_km': distance,
                    'type1': FINISHED_GOODS_TYPE,
                    'type2': COMPONENTS_TYPE
                })
        
        return sorted(distances, key=lambda x: x['distance_km'])
    
    def create_map(self, finished_goods_df, components_df):
        """Create the interactive bubble map"""
        print("Creating interactive map...")
        
        # Calculate map center based on all facilities
        all_lats = list(finished_goods_df['latitude']) + list(components_df['latitude'])
        all_lngs = list(finished_goods_df['longitude']) + list(components_df['longitude'])
        
        center_lat = np.mean(all_lats)
        center_lng = np.mean(all_lngs)
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=3,
            tiles='OpenStreetMap'
        )
        
        # Add finished goods facilities
        for idx, row in finished_goods_df.iterrows():
            popup_text = f"""
            <b>{row['Factory Name']}</b><br>
            Type: {row['Factory Type']}<br>
            Location: {row['City']}, {row['Country / Region']}<br>
            Total Workers: {row['Total Workers']}<br>
            Female Workers: {row['% Female Workers']}%
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=folium.Popup(popup_text, max_width=300),
                color='white',
                weight=2,
                fillColor=FINISHED_GOODS_COLOR,
                fillOpacity=0.7,
                tooltip=f"{row['Factory Name']} (Finished Goods)"
            ).add_to(m)
        
        # Add components facilities
        for idx, row in components_df.iterrows():
            popup_text = f"""
            <b>{row['Factory Name']}</b><br>
            Type: {row['Factory Type']}<br>
            Location: {row['City']}, {row['Country / Region']}<br>
            Total Workers: {row['Total Workers']}<br>
            Female Workers: {row['% Female Workers']}%
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=folium.Popup(popup_text, max_width=300),
                color='white',
                weight=2,
                fillColor=COMPONENTS_COLOR,
                fillOpacity=0.7,
                tooltip=f"{row['Factory Name']} (Components)"
            ).add_to(m)
        
        # Calculate and display shortest distances between facility types
        print("Calculating distances between facility types...")
        distances = self.calculate_distances(finished_goods_df, components_df)
        
        # Show top 20 shortest distances as lines
        for dist_info in distances[:20]:
            folium.PolyLine(
                locations=[[dist_info['lat1'], dist_info['lng1']], 
                          [dist_info['lat2'], dist_info['lng2']]],
                color='red',
                weight=1,
                opacity=0.3,
                popup=f"Distance: {dist_info['distance_km']:.1f} km<br>"
                      f"From: {dist_info['facility1']}<br>"
                      f"To: {dist_info['facility2']}"
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Facility Types</b></p>
        <p><i class="fa fa-circle" style="color:{finished_color}"></i> Finished Goods ({finished_count})</p>
        <p><i class="fa fa-circle" style="color:{components_color}"></i> Components ({components_count})</p>
        <p style="font-size:12px;">Red lines show 20 shortest distances</p>
        </div>
        '''.format(
            finished_color=FINISHED_GOODS_COLOR,
            components_color=COMPONENTS_COLOR,
            finished_count=len(finished_goods_df),
            components_count=len(components_df)
        )
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def generate_report(self, finished_goods_df, components_df):
        """Generate a summary report"""
        print("\n" + "="*50)
        print("FACILITY MAPPING REPORT")
        print("="*50)
        
        print(f"\nFINISHED GOODS facilities: {len(finished_goods_df)}")
        print("Top countries:")
        for country, count in finished_goods_df['Country / Region'].value_counts().head(5).items():
            print(f"  {country}: {count}")
        
        print(f"\nFINISHED GOODS - COMPONENTS facilities: {len(components_df)}")
        print("Top countries:")
        for country, count in components_df['Country / Region'].value_counts().head(5).items():
            print(f"  {country}: {count}")
        
        # Calculate some distance statistics
        distances = self.calculate_distances(finished_goods_df, components_df)
        if distances:
            distances_km = [d['distance_km'] for d in distances]
            print(f"\nDistance Statistics (km):")
            print(f"  Shortest distance: {min(distances_km):.1f}")
            print(f"  Longest distance: {max(distances_km):.1f}")
            print(f"  Average distance: {np.mean(distances_km):.1f}")
        
        print(f"\nMap saved as: {OUTPUT_MAP}")
        print("="*50)
    
    def run(self):
        """Main execution function"""
        print("Starting Facility Mapping Process...")
        
        # Load and process data
        finished_goods, components = self.load_and_process_data()
        
        # Add coordinates
        print("\nGeocoding FINISHED GOODS facilities...")
        finished_goods_with_coords = self.add_coordinates(finished_goods)
        
        print("\nGeocoding FINISHED GOODS - COMPONENTS facilities...")
        components_with_coords = self.add_coordinates(components)
        
        # Save cache
        self.save_cache()
        
        if len(finished_goods_with_coords) == 0 or len(components_with_coords) == 0:
            print("Error: No facilities with valid coordinates found!")
            return
        
        # Create map
        map_obj = self.create_map(finished_goods_with_coords, components_with_coords)
        
        # Save map
        map_obj.save(OUTPUT_MAP)
        
        # Generate report
        self.generate_report(finished_goods_with_coords, components_with_coords)

if __name__ == "__main__":
    mapper = FacilityMapper()
    mapper.run()