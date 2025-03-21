from DataMapping import InitAdjacencyMatrix
import numpy as np
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

def layover(origin, destination, airport_codes, df, max_layovers=2):  # replace max_layovers with user input
    """
    Finds layover routes with the same airline and calculates total distance, duration, and price.
    Returns a list of possible layover routes.
    """
    layover_routes = []
    
    def find_routes(current_route, current_airport, remaining_layovers, current_airline):
        """
        Recursive helper function to find routes with layovers.
        """
        if remaining_layovers < 0:
            return
        
        # Check if the current airport is the destination
        if current_airport == destination:
            # Calculate total distance, duration, and price
            total_distance = sum(segment[3] for segment in current_route)
            total_duration = sum(segment[2] for segment in current_route)
            total_price = sum(segment[4] for segment in current_route) * (0.9 ** (len(current_route) - 1))  # 10% discount per transfer
            
            # Add to layover routes
            layover_routes.append({
                "type": "layover",
                "airline_code": current_airline,
                "airline_name": current_route[0][1],  # Airline name from the first segment
                "route": [origin] + [segment[5] for segment in current_route],  # Include all airports in the route
                "total_distance": total_distance,
                "total_duration": total_duration,
                "total_price": total_price
            })
            return
        
        # Iterate through all possible next airports
        for next_airport in airport_codes:
            # Check if there is a route from current_airport to next_airport
            current_idx = airport_codes.index(current_airport)
            next_idx = airport_codes.index(next_airport)
            route_info = df.iloc[current_idx, next_idx]
            
            if route_info is None:
                continue  # No route from current_airport to next_airport
            
            # Find routes with the same airline
            for info in route_info:
                if current_airline is None or info[0] == current_airline:  # Same airline or first segment
                    # Add the segment to the current route
                    find_routes(
                        current_route + [info + (next_airport,)],  # Add segment info and next airport
                        next_airport,
                        remaining_layovers - 1,
                        info[0]  # Current airline
                    )
    
    # Start the recursive search
    find_routes([], origin, max_layovers, None)

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
    
    # Combine direct routes from both directions
    direct_routes = []
    if route_info is not None:
        for info in route_info:
            direct_routes.append({
                "type": "direct",
                "airline_code": info[0],
                "airline_name": info[1],
                "duration": info[2],
                "distance": info[3],
                "price": info[4],
                "route": [origin, destination]  # Direct route
            })
    if route_info is None and reverse_route_info is not None:
        route_info = reverse_route_info
        for info in route_info:
            if info[0] in route_info:
                continue
            else: 
                direct_routes.append({
                    "type": "direct",
                    "airline_code": info[0],
                    "airline_name": info[1],
                    "duration": info[2],
                    "distance": info[3],
                    "price": info[4],
                    "route": [destination, origin] 
                })
    
    # Search for layover routes if no direct routes are found
    layover_routes = []
    if not direct_routes:
        print(f"No direct route found from {origin} to {destination}. Searching for layover routes...")
        layover_routes = layover(origin, destination, airport_codes, df)
        if not layover_routes:
            layover_routes = layover(destination, origin, airport_codes, df)
    
    # Combine direct and layover routes
    all_routes = direct_routes + layover_routes
    
    if not all_routes:
        print("No routes found.")
        return None
    
    # Sort all routes by total distance (shortest first)
    all_routes.sort(key=lambda x: x.get("distance", x.get("total_distance", float('inf'))))
    for route in all_routes:
        if route['type'] == "direct":
            route['price'] = getPriceEstimate(route['price'], costSpike(isHoliday, is_within_one_month))
        else:
            route['total_price'] = getPriceEstimate(route['total_price'], costSpike(isHoliday, is_within_one_month))

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