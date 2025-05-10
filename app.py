{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "44d0a33d-d244-449a-a76e-0e4073346b89",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2025-05-10 16:16:56.499 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n"
     ]
    }
   ],
   "source": [
    "import leafmap.foliumap as leafmap\n",
    "import geopandas as gpd\n",
    "from shapely.geometry import Point, LineString\n",
    "import networkx as nx\n",
    "import streamlit as st\n",
    "from streamlit_folium import st_folium"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "8cf39ceb-ea77-4876-be05-6f1b1df7e032",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2025-05-10 16:21:45.202 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-05-10 16:21:45.203 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-05-10 16:21:45.204 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n",
      "2025-05-10 16:21:45.205 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.\n"
     ]
    }
   ],
   "source": [
    "Map=leafmap.Map(draw_control= False,\n",
    "    scale_control=False,\n",
    "    layer_control= False,\n",
    "    attribution_control=False,\n",
    "    toolbar_control=False,\n",
    "    measure_control= False,\n",
    "    basemap= None)\n",
    "\n",
    "trails= r\"C:\\Users\\User\\Desktop\\Python\\trails.geojson\"\n",
    "lusk= r\"C:\\Users\\User\\Desktop\\Python\\lusk.geojson\"\n",
    "vis={\n",
    "    'color': 'brown',\n",
    "    'weight': 1\n",
    "}\n",
    "vis2={'color': 'grey', 'weight': 2, 'fillColor': 'transparent', 'fillopacity': 0}\n",
    "Map.add_geojson(lusk,style=vis2,layer_name= 'Lusk Creek Wilderness',zoom_to_layer= True)\n",
    "Map.add_geojson(trails, style=vis,layer_name= \"Trail Map\")\n",
    "leafmap.plugins.LocateControl(auto_start=False).add_to(Map)\n",
    "Map.add_basemap('Esri.WorldImagery')\n",
    "\n",
    "click= st_folium(Map, height= 600, returned_objects=['last_clicked'])\n",
    "\n",
    "trail_gdf= gpd.read_file(trails)\n",
    "\n",
    "G= nx.Graph()\n",
    "for _,row in trail_gdf.iterrows():\n",
    "    coords= list(row.geometry.coords)\n",
    "    for i in range(len(coords) -1):\n",
    "        a,b =coords[i], coords[i+1]\n",
    "        dist= Point(a).distance(Point(b))\n",
    "        G.add_edge(a,b,weight=dist)\n",
    "\n",
    "if click and click.get(\"last_clicked\"):\n",
    "    dest_lat = click[\"last_clicked\"][\"lat\"]\n",
    "    dest_lon = click[\"last_clicked\"][\"lng\"]\n",
    "    dest_point = Point(dest_lon, dest_lat)\n",
    "\n",
    "    # Display button to activate LocateControl\n",
    "    if st.button(\"Locate Me\"):\n",
    "        # Show map with LocateControl enabled\n",
    "        Map.add_control(leafmap.plugins.LocateControl(auto_start=True))\n",
    "        st.session_state.locate_triggered = True\n",
    "\n",
    "    # Process the user's location if LocateControl is triggered\n",
    "    if \"locate_triggered\" in st.session_state and st.session_state.locate_triggered:\n",
    "        # User location will be available from the LocateControl plugin once they click the \"Locate Me\" button\n",
    "        user_lat, user_lon = Map.user_location['lat'], Map.user_location['lng']\n",
    "        user_point = Point(user_lon, user_lat)\n",
    "\n",
    "        # Calculate best trail when button is clicked\n",
    "        if st.button(\"Calculate Best Trail\"):\n",
    "            # Find closest nodes\n",
    "            start_node = min(G.nodes, key=lambda n: Point(n).distance(user_point))\n",
    "            end_node = min(G.nodes, key=lambda n: Point(n).distance(dest_point))\n",
    "\n",
    "            try:\n",
    "                # Find the shortest path\n",
    "                path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')\n",
    "                route = [Point(x, y) for x, y in path]\n",
    "\n",
    "                # Display the route\n",
    "                route_map = Map\n",
    "                folium.PolyLine([(point.y, point.x) for point in route], color=\"red\", weight=3).add_to(route_map)\n",
    "                st_folium(route_map, height=600)\n",
    "            except nx.NetworkXNoPath:\n",
    "                st.error(\"No path found.\")\n",
    "    else:\n",
    "        st.warning(\"Click the 'Locate Me' button to get your location.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "id": "8db4811a-10ee-4c6c-8f37-35f33a9fa8f1",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
