#!/usr/bin/env python3
"""
Facility Mapping Script - Components and Equipment Facilities

This script creates an interactive map showing two specific types of facilities:
1. FINISHED GOODS - COMPONENTS facilities
2. FINISHED GOODS facilities that handle Equipment

Based on user feedback to distinguish between these two finished goods facility types.
"""

import pandas as pd
import folium
import numpy as np
from geopy.distance import geodesic
import json
import random

# Constants
EXCEL_FILE = 'imap_export.xls'
OUTPUT_MAP = 'facility_locations_map.html'

# Facility type filters based on user requirements
COMPONENTS_TYPE = 'FINISHED GOODS - COMPONENTS'
EQUIPMENT_FILTER = 'Equipment'  # Product Type Type for FINISHED GOODS facilities

# Map styling - distinct colors for each facility type
COMPONENTS_COLOR = '#A23B72'      # Purple for Components
EQUIPMENT_COLOR = '#2E8B57'       # Sea Green for Equipment
MAP_CENTER = [20.0, 0.0]          # Default center

# Comprehensive coordinates database for offline mapping
COORDINATES_DB = {
    # Countries (fallback coordinates)
    'vietnam': {'lat': 14.0583, 'lng': 108.2772},
    'china': {'lat': 35.8617, 'lng': 104.1954},
    'indonesia': {'lat': -0.7893, 'lng': 113.9213},
    'usa': {'lat': 37.0902, 'lng': -95.7129},
    'thailand': {'lat': 15.8700, 'lng': 100.9925},
    'cambodia': {'lat': 12.5657, 'lng': 104.9910},
    'sri lanka': {'lat': 7.8731, 'lng': 80.7718},
    'brazil': {'lat': -14.2350, 'lng': -51.9253},
    'italy': {'lat': 41.8719, 'lng': 12.5674},
    'india': {'lat': 20.5937, 'lng': 78.9629},
    'bangladesh': {'lat': 23.6850, 'lng': 90.3563},
    'mexico': {'lat': 23.6345, 'lng': -102.5528},
    'south korea': {'lat': 35.9078, 'lng': 127.7669},
    'taiwan': {'lat': 23.6978, 'lng': 120.9605},
    'philippines': {'lat': 12.8797, 'lng': 121.7740},
    'pakistan': {'lat': 30.3753, 'lng': 69.3451},
    'turkey': {'lat': 38.9637, 'lng': 35.2433},
    'guatemala': {'lat': 15.7835, 'lng': -90.2308},
    'honduras': {'lat': 15.2000, 'lng': -86.2419},
    'nicaragua': {'lat': 12.2651, 'lng': -85.2072},
    'dominican republic': {'lat': 18.7357, 'lng': -70.1627},
    'el salvador': {'lat': 13.7942, 'lng': -88.8965},
    'morocco': {'lat': 31.7917, 'lng': -7.0926},
    'tunisia': {'lat': 33.8869, 'lng': 9.5375},
    'madagascar': {'lat': -18.7669, 'lng': 46.8691},
    'jordan': {'lat': 30.5852, 'lng': 36.2384},
    'bulgaria': {'lat': 42.7339, 'lng': 25.4858},
    'romania': {'lat': 45.9432, 'lng': 24.9668},
    'moldova': {'lat': 47.4116, 'lng': 28.3699},
    'ukraine': {'lat': 48.3794, 'lng': 31.1656},
    'bosnia and herzegovina': {'lat': 43.9159, 'lng': 17.6791},
    'serbia': {'lat': 44.0165, 'lng': 21.0059},
    'japan': {'lat': 36.2048, 'lng': 138.2529},
    'malaysia': {'lat': 4.2105, 'lng': 101.9758},
    'laos': {'lat': 19.8563, 'lng': 102.4955},
    'myanmar': {'lat': 21.9162, 'lng': 95.9560},
    'spain': {'lat': 40.4168, 'lng': -3.7038},
    
    # Major cities
    'ho chi minh city, vietnam': {'lat': 10.8231, 'lng': 106.6297},
    'hanoi, vietnam': {'lat': 21.0285, 'lng': 105.8542},
    'dong nai, vietnam': {'lat': 10.9467, 'lng': 106.8434},
    'binh duong, vietnam': {'lat': 11.3254, 'lng': 106.4775},
    'nam dinh, vietnam': {'lat': 20.4388, 'lng': 106.1622},
    'vinh phuc, vietnam': {'lat': 21.3608, 'lng': 105.6049},
    'long an, vietnam': {'lat': 10.6956, 'lng': 106.2431},
    'hai duong, vietnam': {'lat': 20.9373, 'lng': 106.3148},
    'thai binh, vietnam': {'lat': 20.4463, 'lng': 106.3365},
    'an giang, vietnam': {'lat': 10.3889, 'lng': 105.4359},
    'can tho, vietnam': {'lat': 10.0452, 'lng': 105.7469},
    'tien giang, vietnam': {'lat': 10.3587, 'lng': 106.3617},
    'quang nam, vietnam': {'lat': 15.5739, 'lng': 108.0199},
    'soc trang, vietnam': {'lat': 9.6003, 'lng': 105.9700},
    
    'beijing, china': {'lat': 39.9042, 'lng': 116.4074},
    'shanghai, china': {'lat': 31.2304, 'lng': 121.4737},
    'guangzhou, china': {'lat': 23.1291, 'lng': 113.2644},
    'shenzhen, china': {'lat': 22.5431, 'lng': 114.0579},
    'dongguan, china': {'lat': 23.0209, 'lng': 113.7518},
    'foshan, china': {'lat': 23.0218, 'lng': 113.1064},
    'qingdao, china': {'lat': 36.0986, 'lng': 120.3719},
    'xiamen, china': {'lat': 24.4798, 'lng': 118.0819},
    'jiangmen, china': {'lat': 22.5751, 'lng': 113.0946},
    'zhongshan, china': {'lat': 22.5167, 'lng': 113.3833},
    
    'jakarta, indonesia': {'lat': -6.2088, 'lng': 106.8456},
    'surabaya, indonesia': {'lat': -7.2575, 'lng': 112.7521},
    'bandung, indonesia': {'lat': -6.9175, 'lng': 107.6191},
    'bekasi, indonesia': {'lat': -6.2383, 'lng': 106.9756},
    'tangerang, indonesia': {'lat': -6.1783, 'lng': 106.6319},
    'grobogan, indonesia': {'lat': -7.0584, 'lng': 110.9158},
    
    'bangkok, thailand': {'lat': 13.7563, 'lng': 100.5018},
    'chonburi, thailand': {'lat': 13.3611, 'lng': 100.9847},
    'nakhon pathom, thailand': {'lat': 13.8199, 'lng': 100.0625},
    'samut sakhon, thailand': {'lat': 13.5475, 'lng': 100.2739},
    
    'phnom penh, cambodia': {'lat': 11.5564, 'lng': 104.9282},
    'kandal, cambodia': {'lat': 11.4564, 'lng': 104.9282},
    'koh kong, cambodia': {'lat': 11.6158, 'lng': 102.9839},
    
    'mumbai, india': {'lat': 19.0760, 'lng': 72.8777},
    'delhi, india': {'lat': 28.7041, 'lng': 77.1025},
    'bangalore, india': {'lat': 12.9716, 'lng': 77.5946},
    'chennai, india': {'lat': 13.0827, 'lng': 80.2707},
    'mysore, india': {'lat': 12.2958, 'lng': 76.6394},
    'tirpur, india': {'lat': 11.1085, 'lng': 77.3411},
    
    'woodburn, usa': {'lat': 45.1437, 'lng': -122.8551},
    'rienzi, usa': {'lat': 34.8248, 'lng': -88.3470},
    'frisco, usa': {'lat': 33.1507, 'lng': -96.8236},
    'spokane, usa': {'lat': 47.6587, 'lng': -117.4260},
    'norfolk, usa': {'lat': 36.8468, 'lng': -76.2852},
    
    'seoul, south korea': {'lat': 37.5665, 'lng': 126.9780},
    'busan, south korea': {'lat': 35.1796, 'lng': 129.0756},
    'gyeonggi-do, south korea': {'lat': 37.4138, 'lng': 127.5183},
    
    'taipei, taiwan': {'lat': 25.0330, 'lng': 121.5654},
    'taipei city, taiwan': {'lat': 25.0330, 'lng': 121.5654},
    
    'taraklia, moldova': {'lat': 46.1667, 'lng': 28.2667},
    
    'chaucina-granada, spain': {'lat': 37.1735, 'lng': -3.7038},
}

class FacilityMapper:
    def __init__(self):
        pass
    
    def get_coordinates(self, city, country):
        """Get coordinates for a city/country combination"""
        # Clean and normalize
        city = str(city).strip().lower() if pd.notna(city) else ""
        country = str(country).strip().lower() if pd.notna(country) else ""
        
        # Try city, country combination first
        location_key = f"{city}, {country}"
        if location_key in COORDINATES_DB:
            return COORDINATES_DB[location_key]
        
        # Try just city
        if city in COORDINATES_DB:
            return COORDINATES_DB[city]
        
        # Try just country
        if country in COORDINATES_DB:
            coords = COORDINATES_DB[country].copy()
            # Add some random offset for different cities in same country
            coords['lat'] += random.uniform(-1.5, 1.5)
            coords['lng'] += random.uniform(-1.5, 1.5)
            return coords
        
        return None
    
    def load_and_process_data(self):
        """Load Excel data and process facility information"""
        print("Loading Excel data...")
        df = pd.read_excel(EXCEL_FILE, engine='xlrd', header=1)
        
        # Filter for the two specific facility types the user wants
        # 1. FINISHED GOODS - COMPONENTS facilities
        components_df = df[df['Factory Type'] == COMPONENTS_TYPE].copy()
        
        # 2. FINISHED GOODS facilities that handle Equipment
        equipment_df = df[
            (df['Factory Type'] == 'FINISHED GOODS') & 
            (df['Product Type Type'] == EQUIPMENT_FILTER)
        ].copy()
        
        print(f"Found {len(components_df)} FINISHED GOODS - COMPONENTS facilities")
        print(f"Found {len(equipment_df)} FINISHED GOODS - Equipment facilities")
        
        return components_df, equipment_df
    
    def add_coordinates(self, df, facility_type_name):
        """Add lat/lng coordinates to dataframe"""
        coordinates = []
        successful = 0
        
        print(f"\nMapping coordinates for {facility_type_name} facilities...")
        
        for idx, row in df.iterrows():
            city = row['City']
            country = row['Country / Region']
            
            coords = self.get_coordinates(city, country)
            if coords:
                coordinates.append(coords)
                successful += 1
            else:
                coordinates.append({'lat': None, 'lng': None})
                print(f"  No coordinates found for: {city}, {country}")
        
        df['latitude'] = [c['lat'] for c in coordinates]
        df['longitude'] = [c['lng'] for c in coordinates]
        
        # Remove rows without coordinates
        df_with_coords = df.dropna(subset=['latitude', 'longitude'])
        print(f"Successfully located {len(df_with_coords)} out of {len(df)} {facility_type_name} facilities")
        
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
                    'type1': 'Components',
                    'type2': 'Equipment'
                })
        
        return sorted(distances, key=lambda x: x['distance_km'])
    
    def create_map(self, components_df, equipment_df):
        """Create the interactive bubble map"""
        print("\nCreating interactive map...")
        
        # Calculate map center based on all facilities
        all_lats = list(components_df['latitude']) + list(equipment_df['latitude'])
        all_lngs = list(components_df['longitude']) + list(equipment_df['longitude'])
        
        if len(all_lats) == 0:
            print("Error: No facilities with coordinates found!")
            return None
        
        center_lat = np.mean(all_lats)
        center_lng = np.mean(all_lngs)
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=3,
            tiles='OpenStreetMap'
        )
        
        # Add Components facilities
        components_group = folium.FeatureGroup(name='Components Facilities')
        for idx, row in components_df.iterrows():
            popup_text = f"""
            <div style="width: 280px;">
            <b>{row['Factory Name']}</b><br>
            <b>Type:</b> Components (Finished Goods - Components)<br>
            <b>Product:</b> {row['Product Type Type']}<br>
            <b>Location:</b> {row['City']}, {row['Country / Region']}<br>
            <b>Total Workers:</b> {row['Total Workers']}<br>
            <b>Female Workers:</b> {row['% Female Workers']}%<br>
            <b>Migrant Workers:</b> {row['% Migrant Workers']}%
            </div>
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=12,
                popup=folium.Popup(popup_text, max_width=320),
                color='white',
                weight=2,
                fillColor=COMPONENTS_COLOR,
                fillOpacity=0.8,
                tooltip=f"{row['Factory Name']} (Components)"
            ).add_to(components_group)
        
        components_group.add_to(m)
        
        # Add Equipment facilities
        equipment_group = folium.FeatureGroup(name='Equipment Facilities')
        for idx, row in equipment_df.iterrows():
            popup_text = f"""
            <div style="width: 280px;">
            <b>{row['Factory Name']}</b><br>
            <b>Type:</b> Equipment (Finished Goods - Equipment)<br>
            <b>Product:</b> {row['Product Type Type']}<br>
            <b>Location:</b> {row['City']}, {row['Country / Region']}<br>
            <b>Total Workers:</b> {row['Total Workers']}<br>
            <b>Female Workers:</b> {row['% Female Workers']}%<br>
            <b>Migrant Workers:</b> {row['% Migrant Workers']}%
            </div>
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=12,
                popup=folium.Popup(popup_text, max_width=320),
                color='white',
                weight=2,
                fillColor=EQUIPMENT_COLOR,
                fillOpacity=0.8,
                tooltip=f"{row['Factory Name']} (Equipment)"
            ).add_to(equipment_group)
        
        equipment_group.add_to(m)
        
        # Calculate and display shortest distances between facility types
        print("Calculating distances between Components and Equipment facilities...")
        distances = self.calculate_distances(components_df, equipment_df)
        
        # Show top 25 shortest distances as lines
        distance_group = folium.FeatureGroup(name='Shortest Distances (Top 25)')
        for i, dist_info in enumerate(distances[:25]):
            color_intensity = 1.0 - (i / 25)  # Fade color for longer distances
            opacity = 0.3 + (color_intensity * 0.4)
            
            folium.PolyLine(
                locations=[[dist_info['lat1'], dist_info['lng1']], 
                          [dist_info['lat2'], dist_info['lng2']]],
                color='red',
                weight=2,
                opacity=opacity,
                popup=f"<b>Distance:</b> {dist_info['distance_km']:.1f} km<br>"
                      f"<b>Components Facility:</b> {dist_info['facility1']}<br>"
                      f"<b>Equipment Facility:</b> {dist_info['facility2']}"
            ).add_to(distance_group)
        
        distance_group.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add comprehensive legend
        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 320px; height: 160px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 15px; border-radius: 8px; 
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 16px;">Facility Types</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:{COMPONENTS_COLOR}"></i> 
           <b>Components Facilities</b> ({len(components_df)} facilities)</p>
        <p style="margin: 0 0 5px 20px; font-size: 12px; color: #666;">
           Finished Goods - Components facilities</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:{EQUIPMENT_COLOR}"></i> 
           <b>Equipment Facilities</b> ({len(equipment_df)} facilities)</p>
        <p style="margin: 0 0 5px 20px; font-size: 12px; color: #666;">
           Finished Goods facilities that handle Equipment</p>
        <p style="margin: 8px 0 5px 0; font-size:12px; color: red;">
           — Red lines show 25 shortest distances between facility types</p>
        <p style="margin: 5px 0 0 0; font-size:11px; color: #888;">
           Use layer control (top right) to toggle visibility</p>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def generate_report(self, components_df, equipment_df):
        """Generate a summary report"""
        print("\n" + "="*70)
        print("FACILITY MAPPING REPORT - COMPONENTS & EQUIPMENT")
        print("="*70)
        
        print(f"\nCOMPONENTS facilities (FINISHED GOODS - COMPONENTS): {len(components_df)}")
        if len(components_df) > 0:
            print("Top countries:")
            for country, count in components_df['Country / Region'].value_counts().head(5).items():
                print(f"  {country}: {count}")
        
        print(f"\nEQUIPMENT facilities (FINISHED GOODS - Equipment): {len(equipment_df)}")
        if len(equipment_df) > 0:
            print("Top countries:")
            for country, count in equipment_df['Country / Region'].value_counts().head(5).items():
                print(f"  {country}: {count}")
        
        # Calculate some distance statistics if both types exist
        if len(components_df) > 0 and len(equipment_df) > 0:
            distances = self.calculate_distances(components_df, equipment_df)
            if distances:
                distances_km = [d['distance_km'] for d in distances]
                print(f"\nDistance Statistics between Components and Equipment (km):")
                print(f"  Shortest distance: {min(distances_km):.1f}")
                print(f"  Longest distance: {max(distances_km):.1f}")
                print(f"  Average distance: {np.mean(distances_km):.1f}")
                print(f"  Median distance: {np.median(distances_km):.1f}")
                
                # Show top 5 closest facility pairs
                print(f"\nTop 5 Closest Components-Equipment Facility Pairs:")
                for i, dist in enumerate(distances[:5], 1):
                    print(f"  {i}. {dist['distance_km']:.1f} km")
                    print(f"     Components: {dist['facility1'][:40]}...")
                    print(f"     Equipment:  {dist['facility2'][:40]}...")
        
        print(f"\n✓ Interactive map saved as: {OUTPUT_MAP}")
        print("✓ Open the HTML file in a web browser to view the map")
        print("✓ Click on markers for detailed facility information")
        print("✓ Use layer controls to toggle different facility types")
        print("="*70)
    
    def run(self):
        """Main execution function"""
        print("="*70)
        print("FACILITY MAPPING: COMPONENTS & EQUIPMENT FACILITIES")
        print("="*70)
        print("Creating map for two specific finished goods facility types:")
        print("1. Finished Goods - Components facilities")
        print("2. Finished Goods facilities that handle Equipment")
        
        # Load and process data
        components_df, equipment_df = self.load_and_process_data()
        
        if len(components_df) == 0 and len(equipment_df) == 0:
            print("\nError: No facilities of the specified types found!")
            return
        
        # Add coordinates
        components_with_coords = self.add_coordinates(components_df, "Components") if len(components_df) > 0 else pd.DataFrame()
        equipment_with_coords = self.add_coordinates(equipment_df, "Equipment") if len(equipment_df) > 0 else pd.DataFrame()
        
        if len(components_with_coords) == 0 and len(equipment_with_coords) == 0:
            print("\nError: No facilities with valid coordinates found!")
            return
        
        # Create map
        map_obj = self.create_map(components_with_coords, equipment_with_coords)
        
        if map_obj is None:
            print("\nError: Failed to create map!")
            return
        
        # Save map
        map_obj.save(OUTPUT_MAP)
        
        # Generate report
        self.generate_report(components_with_coords, equipment_with_coords)

if __name__ == "__main__":
    mapper = FacilityMapper()
    mapper.run()