from DataMapping import InitAdjacencyMatrix
#import numpy as np
import pandas as pd
import json
import sys
from datetime import datetime, timedelta

"""
Main Algo
Functions:
 - validity (airport code, airline route, user input)
 - getDate (user input --> 1 year or less, String to DATE input)
 - costSpike (check current date -- time to booking date --> if < 1 month OR holiday season: price increase)
 - getPriceEstimate (get price & date)
 - layover (call this function (in main) when there is no direct route)
 - printAllAirlines
 - printAllAirport
"""
file_path = 'Data/airline_routes_custom.json'  # Check if the path is correct
with open(file_path) as file:
    data = json.load(file)

# Main function
def mainAlgo(data, origin, destination, flight_date):
    df, airport_codes = InitAdjacencyMatrix(data)
    printAllAirport(airport_codes)

    valid_booking_date, isHoliday, is_within_one_month = checkDate(flight_date)
    print(f"Validated booking date: {valid_booking_date.strftime('%d/%m/%Y')}")
    print(f"Date a holiday or festive season? {'Yes' if isHoliday else 'No'}")
    print(f"Is this date within one month? {'Yes' if is_within_one_month else 'No'}")

    origin = checkAirportCode(origin, airport_codes)
    destination = checkAirportCode(destination, airport_codes)
    selected_route = getShortestDistance(origin, destination, airport_codes, df, isHoliday, is_within_one_month)

    if selected_route:
        if selected_route['type'] == "layover":  # Layover route
            print(f"\nYou have selected {selected_route['airline_name']} ({selected_route['airline_code']}) for the route: {' -> '.join(selected_route['route'])}")
            print(f"Total Distance: {selected_route['total_distance']} km")
            print(f"Total Duration: {selected_route['total_duration']} minutes")
            print(f"Total Price: ${selected_route['total_price']:.2f}")
        else:  # Direct route
            print(f"\nYou have selected {selected_route['airline_name']} ({selected_route['airline_code']}) for the route: {' -> '.join(selected_route['route'])}")
            print(f"Total Distance: {selected_route['distance']} km")
            print(f"Total Duration: {selected_route['duration']} minutes")
            print(f"Total Price: ${selected_route['price']:.2f}")
    else:
        print(f"No route found from {origin} to {destination}.")

# Main algo (distance)
def floydWarshall(graph):
    """Runs the Floyd-Warshall algorithm on the given adjacency matrix."""
    V = len(graph)  # Number of airports

    # Run Floyd-Warshall algorithm
    for k in range(V):  # Intermediate vertex
        for i in range(V):  # origin location
            for j in range(V):  # destination location
                if graph[i][k] != float('inf') and graph[k][j] != float('inf'):
                    graph[i][j] = min(graph[i][j], graph[i][k] + graph[k][j])

# =========================================================================================================

""" ===================  validity functions  ===================================================== """

def checkAirportCode(airport_code, airport_codes):
    if airport_code not in airport_codes:
        raise ValueError("Invalid airport code.")
    return airport_code

holiday_months = {1, 3, 6, 12}  # jan, march, june, dec
specific_holidays = {
    "25/12", "31/10", "14/02",  # Christmas, Halloween, Valentine's
    "01/01", "19/02",  # New Year's Day, CNY
    "04/07", "01/05", "04/05", "25/10",  # US Independence Day, Labour day, Buddha's Bday, China's republic day
}

def checkDate(user_input):  # (user input --> 1 year or less, String to DATE input, return date)
    try:
        input_date = datetime.strptime(user_input, "%d/%m/%Y")
        today = datetime.now().date()
        one_year_ahead = today + timedelta(days=365)
        one_month_ahead = today + timedelta(days=30)

        # Check date range validity
        if not (today <= input_date.date() <= one_year_ahead): 
            raise ValueError("Date must be within 1 year ahead from today.")
        
        # Check if the date falls within the next 1 month
        is_within_one_month = input_date.date() <= one_month_ahead

        # Check if the date falls in a holiday month
        is_festive_month = input_date.month in holiday_months

        # Check if the date is a public holiday
        is_public_holiday = input_date.strftime("%d/%m") in specific_holidays

        # Determine if the date is considered a holiday
        isHoliday = is_festive_month or is_public_holiday

        return input_date, isHoliday, is_within_one_month  # Returning the date and booleans

    except ValueError as e:
        raise ValueError(f"Invalid date format or value: {e}")

# =========================================================================================================

""" ==================  calculation functions  ========================================= """

def costSpike(isHoliday, is_within_one_month):  # if < 1 month OR holiday season: price increase
    spike = 0
    if isHoliday:
        spike += 0.1
    if is_within_one_month:
        spike += 0.05
    return spike

def getPriceEstimate(basePrice, costSpike):  # get price & costSpike()
    return basePrice * (1 + costSpike)

# Get coordinates for airports
def get_airport_coords(code):
    airport_data = data.get(code, {})
    return (float(airport_data.get('latitude', 0)), float(airport_data.get('longitude', 0))) 

def layover(origin, destination, airport_codes, df, max_layovers=3):  # replace max_layovers with user input
    """
    Finds layover routes with the same airline and calculates total distance, duration, and price.
    Returns a list of possible layover routes.
    """
    layover_routes = []
    visited = set()  # Track visited airports to prevent cycles
    
    print(f"Searching for layover routes from {origin} to {destination} with up to {max_layovers} layovers")
    
    def find_routes(current_route, current_airport, layover_count, current_airline):
        """
        Recursive helper function to find routes with layovers.
        """
        # Avoid cycles by not revisiting airports in the same path
        if current_airport in visited:
            return
            
        visited.add(current_airport)
        
        if current_airport == destination:
            if layover_count <= max_layovers:  
                total_distance = sum(segment[3] for segment in current_route)
                total_duration = sum(segment[2] for segment in current_route)
                total_price = sum(segment[4] for segment in current_route) * (0.9 ** (len(current_route) - 1))
                route_airports = [origin] + [segment[5] for segment in current_route]
                route_coordinates = [get_airport_coords(code) for code in route_airports]
                
                # Add to layover routes
                layover_routes.append({
                    "type": "layover",
                    "airline_code": current_airline,
                    "airline_name": current_route[0][1],
                    "route": route_airports,
                    "total_distance": total_distance,
                    "total_duration": total_duration,
                    "total_price": total_price,
                    "coordinates": route_coordinates,
                    "layovers": layover_count
                })
                print(f"Found route with {layover_count} layovers: {' -> '.join(route_airports)}")
            visited.remove(current_airport)
            return
        if layover_count >= max_layovers:
            visited.remove(current_airport)
            return
        
        for next_airport in airport_codes:
            if next_airport == current_airport or next_airport in visited:
                continue
                
            # Check if there's a route to the next airport
            current_idx = airport_codes.index(current_airport)
            next_idx = airport_codes.index(next_airport)
            route_info = df.iloc[current_idx, next_idx]
            
            if route_info is None:
                continue
                
            # Find routes with the same airline
            for info in route_info:
                if current_airline is None or info[0] == current_airline:
                    # Add the segment and continue search
                    next_segment = info + (next_airport,)
                    find_routes(
                        current_route + [next_segment],
                        next_airport,
                        layover_count + 1,
                        info[0]
                    )
        
        # Remove from visited when backtracking
        visited.remove(current_airport)
    
    find_routes([], origin, 0, None)
    
    # debugging for CGK to JHB
    if origin == "CGK" and destination == "JHB":
        print(f"Found {len(layover_routes)} routes from CGK to JHB")
        for i, route in enumerate(layover_routes):
            print(f"Route {i+1}: {' -> '.join(route['route'])} with {route['layovers']} layovers ({route['airline_name']})")

    # Sort layover routes by total distance (shortest first)
    layover_routes.sort(key=lambda x: x["total_distance"])
    
    return layover_routes  # Return all layover routes

def getShortestDistance(origin, destination, airport_codes, df, isHoliday, is_within_one_month):
    """
    Finds the shortest distance route between two airports and returns the selected route information.
    Combines direct and layover routes into a single list, sorted by total distance.
    """
    # Get the route information for the selected origin and destination
    origin_idx = airport_codes.index(origin)
    destination_idx = airport_codes.index(destination)
    
    route_info = df.iloc[origin_idx, destination_idx]
    reverse_route_info = df.iloc[destination_idx, origin_idx]

    # Track unique airlines to avoid duplicates
    seen_airlines = set()
    
    # Combine direct routes from both directions
    direct_routes = []
    if route_info is not None:
        for info in route_info:
            if info[0] in seen_airlines:
                continue
            seen_airlines.add(info[0])
            direct_routes.append({
                "type": "direct",
                "airline_code": info[0],
                "airline_name": info[1],
                "duration": info[2],
                "distance": info[3],
                "price": info[4],
                "route": [origin, destination],  
                "coordinates": [get_airport_coords(origin), get_airport_coords(destination)],
                "layovers": 0  
            })
    if route_info is None and reverse_route_info is not None:
        for info in reverse_route_info:
            if info[0] in seen_airlines:  
                continue
            seen_airlines.add(info[0])
            direct_routes.append({
                "type": "direct",
                "airline_code": info[0],
                "airline_name": info[1],
                "duration": info[2],
                "distance": info[3],
                "price": info[4],
                "route": [origin, destination],  
                "coordinates": [get_airport_coords(origin), get_airport_coords(destination)],
                "layovers": 0 
            })
    
    # Debug output for direct routes
    print(f"Direct routes from {origin} to {destination}: {len(direct_routes)}")
    for idx, route in enumerate(direct_routes):
        print(f"Direct route {idx+1}: {route['airline_name']} from {origin} to {destination}")
    
    # ALWAYS search for layover routes, regardless of direct routes
    print(f"Searching for layover routes from {origin} to {destination}...")
    layover_routes = layover(origin, destination, airport_codes, df)
    
    # Debug output for layover routes
    print(f"Layover routes from {origin} to {destination}: {len(layover_routes)}")
    for idx, route in enumerate(layover_routes):
        print(f"Layover route {idx+1}: {route['airline_name']} via {' -> '.join(route['route'])}")
    
    # Add layover count to layover routes
    for route in layover_routes:
        route["layovers"] = len(route["route"]) - 2  # Number of intermediate stops
    
    # Combine direct and layover routes
    all_routes = direct_routes + layover_routes
    
    if not all_routes:
        print("No routes found.")
        return []
    
    # Sort all routes by total distance (shortest first)
    all_routes.sort(key=lambda x: x.get("distance", x.get("total_distance", float('inf'))))
    for route in all_routes:
        if route['type'] == "direct":
            route['price'] = getPriceEstimate(route['price'], costSpike(isHoliday, is_within_one_month))
        else:
            route['total_price'] = getPriceEstimate(route['total_price'], costSpike(isHoliday, is_within_one_month))
    print(f"All routes found: {len(all_routes)}")
    for idx, route in enumerate(all_routes):
        print(f"Route {idx+1}: {route['airline_name']} from {' to '.join(route['route'])}")

    return all_routes  # Return all available routes

# =========================================================================================================

""" ====================  printing functions  ================================== """

def printAllAirport(airport_codes):
    print("Airport Codes:")
    print(", ".join(airport_codes))

# =========================================================================================================

# Example usage (for testing purposes, can be removed in production)
if __name__ == "__main__":
    # Example inputs for testing
    origin = "JFK"  # Example origin airport code
    destination = "LAX"  # Example destination airport code
    flight_date = "15/12/2023"  # Example flight date

    try:
        mainAlgo(data, origin, destination, flight_date)
    except Exception as e:
        print(f"Error: {e}")