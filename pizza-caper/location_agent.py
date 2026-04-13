import os
import boto3
import logging
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

# Amazon Location Service setup
region = os.environ.get('AWS_REGION', 'us-east-1')
location_client = boto3.client('location', region_name=region)
place_index = os.environ.get('PLACE_INDEX_NAME', 'PizzaPlaceIndex')
route_calculator = os.environ.get('ROUTE_CALCULATOR_NAME', 'PizzaRouteCalculator')

@tool
def search_places(query: str) -> str:
    """Search for places using Amazon Location Service"""
    try:
        response = location_client.search_place_index_for_text(
            IndexName=place_index,
            Text=query,
            MaxResults=5
        )
        return f"Places found for {query}: {response['Results']}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def reverse_geocode(latitude: float, longitude: float) -> str:
    """Convert coordinates to address"""
    try:
        response = location_client.search_place_index_for_position(
            IndexName=place_index,
            Position=[longitude, latitude]
        )
        return f"Address for {latitude},{longitude}: {response['Results']}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_places_by_category(category: str) -> str:
    """Get places by category"""
    try:
        response = location_client.search_place_index_for_text(
            IndexName=place_index,
            Text=category,
            MaxResults=10
        )
        return f"Places in category {category}: {response['Results']}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def calculate_route(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float, travel_mode: str = "Car") -> str:
    """Calculate route between two points with turn-by-turn directions"""
    try:
        response = location_client.calculate_route(
            CalculatorName=route_calculator,
            DeparturePosition=[origin_lon, origin_lat],
            DestinationPosition=[dest_lon, dest_lat],
            TravelMode=travel_mode
        )
        
        if response['Legs']:
            route = response['Summary']
            return f"Route calculated: Distance {route['Distance']:.2f}km, Duration {route['DurationSeconds']:.0f}s, Travel mode: {travel_mode}"
        return "No route found"
    except Exception as e:
        return f"Error calculating route: {str(e)}"

# Create location agent
strands_agent = Agent(
    name="Location Agent",
    description="I can search for places (restaurants, Pizza Resaurants, stores), convert coordinates to addresses, find places by category, and calculate routes between locations using Amazon Location Service.",
    tools={TODO}
)

runtime_url = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://127.0.0.1:9000/')

# Create A2A server
a2a_server = A2AServer(
    {TODO}
)

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy", "agent": "location"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
