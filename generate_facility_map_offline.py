#!/usr/bin/env python3
"""
Geographical Bubble Map Generator for Facility Locations (Offline Version)

This script reads facility data from the Excel file and creates an interactive
geographical bubble map showing two facility types using predefined coordinates.
"""

import pandas as pd
import folium
import numpy as np
from geopy.distance import geodesic
import json

# Constants
EXCEL_FILE = 'imap_export.xls'
OUTPUT_MAP = 'facility_locations_map.html'

# Facility type filters
FINISHED_GOODS_TYPE = 'FINISHED GOODS'
COMPONENTS_TYPE = 'FINISHED GOODS - COMPONENTS'

# Map styling
FINISHED_GOODS_COLOR = '#2E86AB'  # Blue
COMPONENTS_COLOR = '#A23B72'      # Purple

# Predefined coordinates for countries and major cities
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
    'my tho, vietnam': {'lat': 10.3600, 'lng': 106.3597},
    'tan uyen, vietnam': {'lat': 11.1520, 'lng': 106.6226},
    'nhon trach, vietnam': {'lat': 10.8120, 'lng': 106.8434},
    'duy xuyen district, vietnam': {'lat': 15.8021, 'lng': 108.2208},
    'taipei city, vietnam': {'lat': 25.0330, 'lng': 121.5654},  # Note: This might be an error in data
    
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
    'meizhou, china': {'lat': 24.2899, 'lng': 116.1177},
    'yongzhou, china': {'lat': 26.4204, 'lng': 111.6134},
    'shaoyang city, china': {'lat': 27.2418, 'lng': 111.4689},
    'zhan jiang city, china': {'lat': 21.2707, 'lng': 110.3594},
    'zhongshan guangdong, china': {'lat': 22.5167, 'lng': 113.3833},
    
    'jakarta, indonesia': {'lat': -6.2088, 'lng': 106.8456},
    'surabaya, indonesia': {'lat': -7.2575, 'lng': 112.7521},
    'bandung, indonesia': {'lat': -6.9175, 'lng': 107.6191},
    'bekasi, indonesia': {'lat': -6.2383, 'lng': 106.9756},
    'tangerang, indonesia': {'lat': -6.1783, 'lng': 106.6319},
    'grobogan, indonesia': {'lat': -7.0584, 'lng': 110.9158},
    'majalengka, indonesia': {'lat': -6.8364, 'lng': 108.2277},
    'sukabumi, indonesia': {'lat': -6.9175, 'lng': 106.9276},
    'cirebon, indonesia': {'lat': -6.7063, 'lng': 108.5571},
    
    'bangkok, thailand': {'lat': 13.7563, 'lng': 100.5018},
    'chonburi, thailand': {'lat': 13.3611, 'lng': 100.9847},
    'nakhon pathom, thailand': {'lat': 13.8199, 'lng': 100.0625},
    'samut sakhon, thailand': {'lat': 13.5475, 'lng': 100.2739},
    'samut prakan, thailand': {'lat': 13.5990, 'lng': 100.5998},
    'pathum thani, thailand': {'lat': 14.0208, 'lng': 100.5250},
    
    'phnom penh, cambodia': {'lat': 11.5564, 'lng': 104.9282},
    'kandal, cambodia': {'lat': 11.4564, 'lng': 104.9282},
    'koh kong, cambodia': {'lat': 11.6158, 'lng': 102.9839},
    
    'colombo, sri lanka': {'lat': 6.9271, 'lng': 79.8612},
    'katunayake, sri lanka': {'lat': 7.1697, 'lng': 79.8841},
    'seeduwa, sri lanka': {'lat': 7.1097, 'lng': 79.8841},
    'biyagama, sri lanka': {'lat': 6.9544, 'lng': 79.9772},
    'koggala, sri lanka': {'lat': 5.9900, 'lng': 80.3233},
    'mirigama, sri lanka': {'lat': 7.2433, 'lng': 80.1219},
    
    'mumbai, india': {'lat': 19.0760, 'lng': 72.8777},
    'delhi, india': {'lat': 28.7041, 'lng': 77.1025},
    'bangalore, india': {'lat': 12.9716, 'lng': 77.5946},
    'chennai, india': {'lat': 13.0827, 'lng': 80.2707},
    'mysore, india': {'lat': 12.2958, 'lng': 76.6394},
    'tirpur, india': {'lat': 11.1085, 'lng': 77.3411},
    'madurai, india': {'lat': 9.9252, 'lng': 78.1198},
    'coimbatore, india': {'lat': 11.0168, 'lng': 76.9558},
    'gudur, india': {'lat': 14.1489, 'lng': 79.8492},
    
    'sao paulo, brazil': {'lat': -23.5505, 'lng': -46.6333},
    'rio de janeiro, brazil': {'lat': -22.9068, 'lng': -43.1729},
    'novo hamburgo, brazil': {'lat': -29.6783, 'lng': -51.1306},
    'sapiranga, brazil': {'lat': -29.6364, 'lng': -51.0069},
    'dois irmaos, brazil': {'lat': -29.5800, 'lng': -51.0856},
    'campo bom, brazil': {'lat': -29.6789, 'lng': -51.0533},
    'franca, brazil': {'lat': -20.5386, 'lng': -47.4006},
    'igrejinha, brazil': {'lat': -29.5733, 'lng': -50.7958},
    'tupa, brazil': {'lat': -21.9344, 'lng': -50.5136},
    
    'milan, italy': {'lat': 45.4642, 'lng': 9.1900},
    'rome, italy': {'lat': 41.9028, 'lng': 12.4964},
    'florence, italy': {'lat': 43.7696, 'lng': 11.2558},
    'montebelluna, italy': {'lat': 45.7753, 'lng': 12.0478},
    'ancarano, italy': {'lat': 42.7575, 'lng': 13.8019},
    'kilkis, italy': {'lat': 41.0833, 'lng': 22.8833},  # Note: Kilkis is actually in Greece
    
    'new york, usa': {'lat': 40.7128, 'lng': -74.0060},
    'los angeles, usa': {'lat': 34.0522, 'lng': -118.2437},
    'chicago, usa': {'lat': 41.8781, 'lng': -87.6298},
    'woodburn, usa': {'lat': 45.1437, 'lng': -122.8551},
    'rienzi, usa': {'lat': 34.8248, 'lng': -88.3470},
    'frisco, usa': {'lat': 33.1507, 'lng': -96.8236},
    'spokane, usa': {'lat': 47.6587, 'lng': -117.4260},
    
    'seoul, south korea': {'lat': 37.5665, 'lng': 126.9780},
    'busan, south korea': {'lat': 35.1796, 'lng': 129.0756},
    'gyeonggi-do, south korea': {'lat': 37.4138, 'lng': 127.5183},
    
    'taipei, taiwan': {'lat': 25.0330, 'lng': 121.5654},
    'yun-lin hsien, taiwan': {'lat': 23.7081, 'lng': 120.4315},
    
    'taraklia, moldova': {'lat': 46.1667, 'lng': 28.2667},
    
    'villanueva, honduras': {'lat': 15.3167, 'lng': -88.0167},
}

class OfflineFacilityMapper:
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
            coords['lat'] += np.random.uniform(-2, 2)
            coords['lng'] += np.random.uniform(-2, 2)
            return coords
        
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
        successful = 0
        
        for idx, row in df.iterrows():
            city = row['City']
            country = row['Country / Region']
            
            coords = self.get_coordinates(city, country)
            if coords:
                coordinates.append(coords)
                successful += 1
            else:
                coordinates.append({'lat': None, 'lng': None})
                print(f"No coordinates found for: {city}, {country}")
        
        df['latitude'] = [c['lat'] for c in coordinates]
        df['longitude'] = [c['lng'] for c in coordinates]
        
        # Remove rows without coordinates
        df_with_coords = df.dropna(subset=['latitude', 'longitude'])
        print(f"Successfully located {len(df_with_coords)} out of {len(df)} facilities")
        
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
        finished_goods_group = folium.FeatureGroup(name='Finished Goods Facilities')
        for idx, row in finished_goods_df.iterrows():
            popup_text = f"""
            <div style="width: 250px;">
            <b>{row['Factory Name']}</b><br>
            <b>Type:</b> {row['Factory Type']}<br>
            <b>Location:</b> {row['City']}, {row['Country / Region']}<br>
            <b>Total Workers:</b> {row['Total Workers']}<br>
            <b>Female Workers:</b> {row['% Female Workers']}%<br>
            <b>Migrant Workers:</b> {row['% Migrant Workers']}%
            </div>
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=10,
                popup=folium.Popup(popup_text, max_width=300),
                color='white',
                weight=2,
                fillColor=FINISHED_GOODS_COLOR,
                fillOpacity=0.8,
                tooltip=f"{row['Factory Name']} (Finished Goods)"
            ).add_to(finished_goods_group)
        
        finished_goods_group.add_to(m)
        
        # Add components facilities
        components_group = folium.FeatureGroup(name='Components Facilities')
        for idx, row in components_df.iterrows():
            popup_text = f"""
            <div style="width: 250px;">
            <b>{row['Factory Name']}</b><br>
            <b>Type:</b> {row['Factory Type']}<br>
            <b>Location:</b> {row['City']}, {row['Country / Region']}<br>
            <b>Total Workers:</b> {row['Total Workers']}<br>
            <b>Female Workers:</b> {row['% Female Workers']}%<br>
            <b>Migrant Workers:</b> {row['% Migrant Workers']}%
            </div>
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=10,
                popup=folium.Popup(popup_text, max_width=300),
                color='white',
                weight=2,
                fillColor=COMPONENTS_COLOR,
                fillOpacity=0.8,
                tooltip=f"{row['Factory Name']} (Components)"
            ).add_to(components_group)
        
        components_group.add_to(m)
        
        # Calculate and display shortest distances between facility types
        print("Calculating distances between facility types...")
        distances = self.calculate_distances(finished_goods_df, components_df)
        
        # Show top 30 shortest distances as lines
        distance_group = folium.FeatureGroup(name='Shortest Distances (Top 30)')
        for i, dist_info in enumerate(distances[:30]):
            color_intensity = 1.0 - (i / 30)  # Fade color for longer distances
            opacity = 0.3 + (color_intensity * 0.4)
            
            folium.PolyLine(
                locations=[[dist_info['lat1'], dist_info['lng1']], 
                          [dist_info['lat2'], dist_info['lng2']]],
                color='red',
                weight=2,
                opacity=opacity,
                popup=f"<b>Distance:</b> {dist_info['distance_km']:.1f} km<br>"
                      f"<b>From:</b> {dist_info['facility1']}<br>"
                      f"<b>To:</b> {dist_info['facility2']}"
            ).add_to(distance_group)
        
        distance_group.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 250px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 5px;">
        <p style="margin: 0; font-weight: bold;">Facility Types</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:{finished_color}"></i> Finished Goods ({finished_count} facilities)</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:{components_color}"></i> Components ({components_count} facilities)</p>
        <p style="margin: 5px 0; font-size:12px; color: red;">— Red lines show 30 shortest distances</p>
        <p style="margin: 5px 0; font-size:11px;">Use layer control to toggle visibility</p>
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
        print("\n" + "="*60)
        print("FACILITY MAPPING REPORT")
        print("="*60)
        
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
            print(f"  Median distance: {np.median(distances_km):.1f}")
            
            # Show top 10 closest facility pairs
            print(f"\nTop 10 Closest Facility Pairs:")
            for i, dist in enumerate(distances[:10], 1):
                print(f"  {i}. {dist['distance_km']:.1f} km")
                print(f"     {dist['facility1'][:50]}...")
                print(f"     {dist['facility2'][:50]}...")
                print()
        
        print(f"\nMap saved as: {OUTPUT_MAP}")
        print("Open the HTML file in a web browser to view the interactive map.")
        print("="*60)
    
    def run(self):
        """Main execution function"""
        print("Starting Offline Facility Mapping Process...")
        
        # Load and process data
        finished_goods, components = self.load_and_process_data()
        
        # Add coordinates
        print("\nAdding coordinates to FINISHED GOODS facilities...")
        finished_goods_with_coords = self.add_coordinates(finished_goods)
        
        print("\nAdding coordinates to FINISHED GOODS - COMPONENTS facilities...")
        components_with_coords = self.add_coordinates(components)
        
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
    mapper = OfflineFacilityMapper()
    mapper.run()