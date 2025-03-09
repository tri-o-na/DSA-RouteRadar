from DataMapping import InitAdjacencyMatrix
import numpy as np
import pandas as pd

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
# Main function

def mainAlgo():
    print()

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

def checkAirportCode(userInput):
    print()

def checkAirlineCode(userInput):
    print()

def checkDate(userInput):
    print()

def checkAirlineRoute(userInput): #check origin and final destination
    print()

# =========================================================================================================

""" ==================  calculation functions  ========================================= """
def getDate():
    print()

def costSpike(): #calls checkDate, current date -- time to booking date --> if < 1 month OR holiday season: price increase
    print()

def getPriceEstimate(): #get price & date
    print()

def layover():
    print()

def getShortestDistance():
    # calls layover function if no direct route
    # call validity function to check origin and final destination
    print()

# =========================================================================================================

""" ====================  printing functions  ================================== """

def printAllAirport():
    print()

def printAllAirlines():
    print()

# =========================================================================================================

def findShortestPath(data):
    """Loads the adjacency matrix, prints airport codes, and allows user to input origin, destination, and airline to get the distance."""
    
    # Step 1: Initialize the adjacency matrix and get airport codes
    adj_matrix_df, airport_codes = InitAdjacencyMatrix(data)
    
    # Step 2: Print all airport codes
    print("Airport Codes:")
    print(", ".join(airport_codes))
    
    # Step 3: Get user input for origin and destination
    origin = input("\nEnter the origin airport code: ").strip().upper()
    destination = input("Enter the destination airport code: ").strip().upper()
    
    # Step 4: Validate the input
    if origin not in airport_codes or destination not in airport_codes:
        print("Invalid airport code. Please check the airport codes and try again.")
        return
    
    # Step 5: Get the route information for the selected origin and destination
    origin_idx = airport_codes.index(origin)
    destination_idx = airport_codes.index(destination)
    
    route_info = adj_matrix_df.iloc[origin_idx, destination_idx]
    
    if route_info is None:
        print(f"No route found from {origin} to {destination}.")
        return
    
    # Step 6: Display available airlines for the selected route
    print(f"\nAvailable airlines from {origin} to {destination}:")
    for i, info in enumerate(route_info):
        airline_code, airline_name, duration = info
        print(f"{i + 1}. {airline_name} ({airline_code}) - {duration} minutes")
    
    # Step 7: Get user input for airline selection
    try:
        airline_choice = int(input("\nEnter the number corresponding to the airline you want to choose: "))
        if airline_choice < 1 or airline_choice > len(route_info):
            print("Invalid choice. Please select a valid number.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Step 8: Display the selected airline and route details
    selected_airline = route_info[airline_choice - 1]
    airline_code, airline_name, duration = selected_airline
    print(f"\nYou have selected {airline_name} ({airline_code}) from {origin} to {destination}.")
    print(f"Duration: {duration} minutes")




