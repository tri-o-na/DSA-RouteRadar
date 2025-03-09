from DataMapping import InitAdjacencyMatrix
import numpy as np
import pandas as pd
import json

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
    destination = input("Enter the destination airport code: ").strip().upper()
    checkAirportCode(origin, destination, airport_codes)
    selected_airline = getShortestDistance(origin, destination, airport_codes, df)
    airline_code, airline_name, duration, distance, base_price = selected_airline
    print(f"\nYou have selected {airline_name} ({airline_code}) from {origin} to {destination}.")
    print(f"Duration: {duration} minutes")
    print(f"Distance: {distance} km")        
    print(f"Base Price: ${base_price}")


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

def checkAirportCode(origin, destination, airport_codes):
    if origin not in airport_codes or destination not in airport_codes:
        print("Invalid airport code. Please check the airport codes and try again.")
        return

def checkDate(userInput): # (user input --> 1 year or less, String to DATE input, return date)
    print()

# =========================================================================================================

""" ==================  calculation functions  ========================================= """

def costSpike(): #calls checkDate, current date -- time to booking date --> if < 1 month OR holiday season: price increase
    print()

def getPriceEstimate(): # get price & costSpike()
    print()

def layover():
    print()

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
    
    if route_info is None:
        print(f"No route found from {origin} to {destination}.")
        # call layover()
        return
    
    # Display available airlines for the selected route
    print(f"\nAvailable airlines from {origin} to {destination}:")
    for i, info in enumerate(route_info):
        airline_code, airline_name, _, distance, _ = info
        print(f"{i + 1}. {airline_name} ({airline_code}) - Distance: {distance} km")

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

