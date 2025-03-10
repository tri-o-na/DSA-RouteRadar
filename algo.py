from DataMapping import InitAdjacencyMatrix
import numpy as np
import pandas as pd
import json
import sys

"""
Main Algo
Funtions:
 - validity (airport code, airline route, user input)
 - getDate (user input --> 1 year or less, String to DATE input)
 - costSpike (check current date -- time to booking date --> if < 1 month OR holiday season: price increase)
 - getPriceEstimate (get price & date)
 - layover (call this function (in main) when there is no direct route)
 - printAllAirlines
 - printAllAirport
"""
file_path = 'Data/airline_routes_custom.json'  #Check if the path is correct
with open(file_path) as file:
    data = json.load(file)

# Main function
def mainAlgo(data):
    df, airport_codes = InitAdjacencyMatrix(data)
    printAllAirport(airport_codes)

    # Get user input for origin and destination
    origin = input("\nEnter the origin airport code: ").strip().upper()
    checkAirportCode(origin, airport_codes)
    destination = input("Enter the destination airport code: ").strip().upper()
    checkAirportCode(destination, airport_codes)
    selected_route = getShortestDistance(origin, destination, airport_codes, df)

    if selected_route:
        if "route" in selected_route:  # Layover route
            print(f"\nYou have selected {selected_route['airline_name']} ({selected_route['airline_code']}) for the route: {' -> '.join(selected_route['route'])}")
            print(f"Total Distance: {selected_route['total_distance']} km")
            print(f"Total Duration: {selected_route['total_duration']} minutes")
            print(f"Total Price: ${selected_route['total_price']:.2f}")
        else:  # Direct route
            airline_code, airline_name, duration, distance, base_price = selected_route
            print(f"\nYou have selected {airline_name} ({airline_code}) from {origin} to {destination}.")
            print(f"Duration: {duration} minutes")
            print(f"Distance: {distance} km")
            print(f"Base Price: ${base_price}")
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
        print("Invalid airport code. Please check the airport codes and try again.")
        sys.exit()

def checkDate(userInput): # (user input --> 1 year or less, String to DATE input, return date)
    print()

# =========================================================================================================

""" ==================  calculation functions  ========================================= """

def costSpike(): #calls checkDate, current date -- time to booking date --> if < 1 month OR holiday season: price increase
    print()

def getPriceEstimate(): # get price & costSpike()
    print()

def layover(origin, destination, airport_codes, df, max_layovers=4):
    """
    Finds layover routes with the same airline and calculates total distance, duration, and price.
    Supports up to 3 layovers (4 segments in total).
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
            if next_airport == current_airport:
                continue  # Skip the current airport
            
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
    
    # Print all possible layover routes
    if layover_routes:
        print("\nAvailable layover routes:")
        for i, route in enumerate(layover_routes):
            print(f"{i + 1}. {route['airline_name']} ({route['airline_code']}) - Route: {' -> '.join(route['route'])}")
            print(f"   Total Distance: {route['total_distance']} km")
            print(f"   Total Duration: {route['total_duration']} minutes")
            print(f"   Total Price: ${route['total_price']:.2f}")
        
        if len(layover_routes) == 1:
            return layover_routes[0]
        
        try:
            airline_choice = int(input("\nEnter the number corresponding to the airline you want to choose: "))
            if airline_choice < 1 or airline_choice > len(layover_routes):
                print("Invalid choice. Please select a valid number.")
                return 
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        
        selected_layover_route = layover_routes[airline_choice - 1]
        # Return the best layover route (shortest distance)
        return selected_layover_route
    else:
        return None

def selectAirline(route_info): #Get user input for airline selection
    try:
        airline_choice = int(input("\nEnter the number corresponding to the airline you want to choose: "))
        if airline_choice < 1 or airline_choice > len(route_info):
            print("Invalid choice. Please select a valid number.")
            return 
        return airline_choice
    
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

def getShortestDistance(origin, destination, airport_codes, df):
    # calls layover function if no direct route
    # call validity function to check origin and final destination
    # Get the route information for the selected origin and destination
    origin_idx = airport_codes.index(origin)
    destination_idx = airport_codes.index(destination)
    
    route_info = df.iloc[origin_idx, destination_idx]
    reverse_route_info = df.iloc[destination_idx, origin_idx]
    
    if route_info is None:
        route_info = reverse_route_info
    
    if route_info is None:
        print(f"No direct route found from {origin} to {destination}. Searching for layover routes...")
        layover_routes = layover(origin, destination, airport_codes, df)
        if layover_routes:
            return layover_routes
        elif layover_routes is None:
            layover_routes = layover(destination, origin, airport_codes, df)
            if layover_routes:
                return layover_routes
        else:
            print("No layover routes found.")
            return None
    
    if layover_routes is None:
        return None
    
    else:
        # Display available airlines for the selected route
        print(f"\nAvailable airlines from {origin} to {destination}:")
        for i, info in enumerate(route_info):
            airline_code, airline_name, _, distance, _ = info
            print(f"{i + 1}. {airline_name} ({airline_code}) - Distance: {distance} km")

        if len(route_info) == 1:
            return route_info[0]

        try:
            airline_choice = int(input("\nEnter the number corresponding to the airline you want to choose: "))
            if airline_choice < 1 or airline_choice > len(route_info):
                print("Invalid choice. Please select a valid number.")
                return 
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        
        selected_airline = route_info[airline_choice - 1]

        return selected_airline

# =========================================================================================================

""" ====================  printing functions  ================================== """

def printAllAirport(airport_codes):
    print("Airport Codes:")
    print(", ".join(airport_codes))

# =========================================================================================================

mainAlgo(data)

