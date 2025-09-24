
import streamlit as st
import json
import heapq
import pandas as pd

# Load the JSON graph
st.set_page_config(page_title=" Travel Planner", layout="wide")
st.title("🗺️  Travel Planner Using Dijkstra's Algorithm")

@st.cache_data
def load_graph(json_file):
    with open(json_file, "r") as f:
        return json.load(f)

graph = load_graph("cities.json")

# Dijkstra algorithm
def dijkstra(graph, start, end, mode="cheapest"):
    pq = [(0, start, [start], 0)] 
    visited = set()

    while pq:
        cost, city, path, distance = heapq.heappop(pq)
        if city in visited:
            continue
        visited.add(city)

        if city == end:
            return {"path": path, "total_cost": cost, "total_distance": distance}

        for neighbor, data in graph.get(city, {}).items():
            if mode == "cheapest":
                weight = min(v for v in data["price"].values() if v > 0)
            else:
                weight = data["price"].get(mode, float("inf"))

            heapq.heappush(
                pq,
                (cost + weight, neighbor, path + [neighbor], distance + data["distance"])
            )
    return None

# Streamlit UI


# Sidebar 
st.sidebar.header("Plan Your Trip")
source = st.sidebar.selectbox("Select Source City", list(graph.keys()))
destination = st.sidebar.selectbox("Select Destination City", list(graph.keys()))
mode = st.sidebar.radio("Select Transport Mode", ["cheapest", "bus", "train", "plane"])
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #EA1414;
        color: white;
        font-size: 16px;
        border-radius: 8px;
        height: 40px;
        width: 150px;
    }
    </style>
""", unsafe_allow_html=True)    
if st.sidebar.button("Find Path"):
    if source == destination:
        st.warning("Source and Destination cannot be the same!")
    else:
        result = dijkstra(graph, source, destination, mode)
        if result:
            st.success("✅ Route Found!")
            st.subheader("Route: ")
            st.write(" → ".join(result["path"]))
            
            st.subheader("Trip Summary:")
            st.write(f"**Total Distance:**  {result['total_distance']} km")
            st.write(f"**Total Cost ({mode.title()}):**  ₹{result['total_cost']}")

            legs = []
            path = result["path"]
            for i in range(len(path)-1):
                from_city = path[i]
                to_city = path[i+1]
                distance = graph[from_city][to_city]["distance"]
                prices = graph[from_city][to_city]["price"]
                legs.append({
                    "From": from_city,
                    "To": to_city,
                    "Distance (km)": distance,
                    "Bus ₹": prices.get("bus", "-"),
                    "Train ₹": prices.get("train", "-"),
                    "Plane ₹": prices.get("plane", "-")
                })
            df = pd.DataFrame(legs)
            st.table(df)
        else:
            st.error("No path found between the selected cities!")
