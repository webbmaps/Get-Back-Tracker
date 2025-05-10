import streamlit as st
from streamlit_folium import st_folium
import folium
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
import math
import json

# Set page config (must be first Streamlit command)
st.set_page_config(layout="wide")

# Title and instructions
st.title("The Get-Back_inator")
st.write("""
1. Allow location access to see your position
2. Click anywhere to set destination
3. Route will appear in red
""")

@st.cache_data
def load_data():
    trails_url = 'https://raw.githubusercontent.com/webbmaps/Get-Back-Tracker/main/trails.geojson'
    lusk_url = 'https://raw.githubusercontent.com/webbmaps/Get-Back-Tracker/main/lusk.geojson'
    
    trail_gdf = gpd.read_file(trails_url)
    wilderness_gdf = gpd.read_file(lusk_url)
    
    # Build graph from trail lines
    G = nx.Graph()
    for _, row in trail_gdf.iterrows():
        coords = list(row.geometry.coords)
        for i in range(len(coords) - 1):
            a, b = coords[i], coords[i+1]
            dist = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
            G.add_edge(a, b, weight=dist)
    
    return G, trail_gdf, wilderness_gdf

G, trails, wilderness = load_data()

# Initialize map
m = folium.Map(
    location=[37.5, -88.7],
    zoom_start=13,
    tiles="Esri.WorldImagery"
)

# Add GeoJSON layers
folium.GeoJson(
    wilderness,
    name="Wilderness Area",
    style_function=lambda x: {
        'color': 'gray',
        'weight': 2,
        'fillOpacity': 0
    }
).add_to(m)

folium.GeoJson(
    trails,
    name="Trails",
    style_function=lambda x: {
        'color': 'brown',
        'weight': 3
    }
).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Add locate control
folium.plugins.LocateControl(
    auto_start=False,
    strings={"title": "Show my location"}
).add_to(m)

# Display map and capture interactions
map_data = st_folium(
    m,
    height=700,
    width=None,
    returned_objects=["last_clicked", "last_position"]
)

# Process interactions
if map_data and map_data.get("last_clicked"):
    dest_point = Point(map_data["last_clicked"]["lng"], map_data["last_clicked"]["lat"])
    
    # Get user location
    user_lat = map_data.get("last_position", {}).get("lat", 37.49)
    user_lon = map_data.get("last_position", {}).get("lng", -88.72)
    user_point = Point(user_lon, user_lat)
    
    # Find nearest nodes
    start_node = min(G.nodes, key=lambda n: Point(n).distance(user_point))
    end_node = min(G.nodes, key=lambda n: Point(n).distance(dest_point))
    
    try:
        # Calculate shortest path
        path = nx.shortest_path(G, source=start_node, target=end_node, weight="weight")
        
        # Create new map with route
        m2 = folium.Map(
            location=[user_lat, user_lon],
            zoom_start=14,
            tiles="Esri.WorldImagery"
        )
        
        # Add layers again
        folium.GeoJson(wilderness, name="Wilderness", style_function=lambda x: {
            'color': 'gray', 'weight': 2, 'fillOpacity': 0
        }).add_to(m2)
        
        folium.GeoJson(trails, name="Trails", style_function=lambda x: {
            'color': 'brown', 'weight': 3
        }).add_to(m2)
        
        # Add route
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in path],
            color="red",
            weight=5
        ).add_to(m2)
        
        # Add markers
        folium.Marker(
            location=[user_lat, user_lon],
            tooltip="You",
            icon=folium.Icon(color="green")
        ).add_to(m2)
        
        folium.Marker(
            location=[dest_point.y, dest_point.x],
            tooltip="Destination",
            icon=folium.Icon(color="red")
        ).add_to(m2)
        
        # Add controls
        folium.LayerControl().add_to(m2)
        folium.plugins.LocateControl().add_to(m2)
        
        # Calculate distance
        distance = sum(math.sqrt((path[i][0]-path[i+1][0])**2 + (path[i][1]-path[i+1][1])**2) 
                  for i in range(len(path)-1))
        st.success(f"Route distance: {distance * 69:.2f} miles")
        
        # Display new map
        st_folium(m2, height=700)
        
    except nx.NetworkXNoPath:
        st.error("No trail route found between these points")
