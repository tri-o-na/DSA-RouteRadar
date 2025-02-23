from DataMapping import InitAdjancyMatrix
import numpy as np
import pandas as pd

def floydWarshall(graph):
    """Runs the Floyd-Warshall algorithm on the given adjacency matrix."""
    V = len(graph)  # Number of airports

    # Run Floyd-Warshall algorithm
    for k in range(V):  # Intermediate vertex
        for i in range(V):  # origin location
            for j in range(V):  # destination location
                if graph[i][k] != float('inf') and graph[k][j] != float('inf'):
                    graph[i][j] = min(graph[i][j], graph[i][k] + graph[k][j])

def get_valid_airport(prompt, airport_codes):
    """Keep asking the user for an airport code until a valid one is entered."""
    while True:
        airport = input(prompt).strip().upper()
        if airport in airport_codes:
            return airport
        print("Invalid input! Please enter a valid airport code from the list.")

def get_valid_airline(prompt, airline_names):
    """Keep asking the user for an airline code or name until a valid one is entered."""
    airline_map = {code.upper(): name for code, name in airline_names.items()}  # Map code → name
    name_to_code = {name.upper(): code for code, name in airline_names.items()}  # Map name → code

    while True:
        airline_input = input(prompt).strip().upper()

        # If input is a valid airline code, return it
        if airline_input in airline_map:
            return airline_input
        
        # If input is a valid airline name, return its code
        if airline_input in name_to_code:
            return name_to_code[airline_input]

        print("Invalid airline! Please enter a valid airline code or name.")

def getWeatherCondition(route_data, shortest_distance):
    # print(f"Weather Condition: {route_data['weather_condition']}")
    routeDelayMultiplier = 1

    match route_data['weather_condition']:
        case "Fine":
            print("Expect no delay to the flight time")
            routeDelayMultiplier = 1
        case "Heavy Rain" | "Heavy Snow":
            print("Expect delay to the flight time")
            routeDelayMultiplier = 1.5
        case "Thunderstorm" | "Snowstorm":
            print("Expect flight cancellations")
            return "CANCELLED"  # Directly return a cancellation message

    # Calculate adjusted distance
    weather_delay_distance = shortest_distance * routeDelayMultiplier
    return weather_delay_distance

def getPriceEstimate(shortest_distance, airline):
    """Calculate the estimated flight price based on airline and distance."""
    
    # Base price per km for each airline (Example values, adjust as needed)
    base_prices = {
        "SQ": 0.12,  # Singapore Airlines
        "TA": 0.10,  # Test Airlines
        "MH": 0.11,  # Malaysia Airlines
        "GA": 0.09,  # Garuda Indonesia
        "TG": 0.13,  # Thai Airways
        "CX": 0.14,  # Cathay Pacific
        "QZ": 0.08,  # Indonesia AirAsia (Budget)
        "JL": 0.15,  # Japan Airlines
        "QF": 0.13,  # Qantas
        "VA": 0.12,  # Virgin Australia
        "NH": 0.14,  # All Nippon Airways
        "UA": 0.16   # United Airlines
    }

    # ✅ Get the base price per km (default to 0.10 if airline not found)
    base_price = base_prices.get(airline, 0.10)

    # ✅ Calculate the final price
    final_price = shortest_distance * base_price

    # ✅ Return the final price (rounded to 2 decimal places)
    return round(final_price, 2)

def findShortestPath():
    """Loads the adjacency matrix and runs the Floyd-Warshall algorithm."""
    adj_matrix, airport_codes, airline_names = InitAdjancyMatrix()

    # Convert DataFrame to NumPy array if it's a DataFrame
    if isinstance(adj_matrix, pd.DataFrame):
        adj_matrix = adj_matrix.to_numpy()

    # Run Floyd-Warshall on adjacency matrix
    floydWarshall(adj_matrix)

    # Let user input origin and destination
    print("\nAvailable Airports:", ", ".join(airport_codes))
    print("Available Airlines:")
    # Convert dictionary to a list of formatted airline strings
    all_airlines = [f"{code} - {name}" for code, name in airline_names.items()]
    # Print as a comma-separated list
    print(", ".join(all_airlines))

    # Validity check for origin and destination
    origin = get_valid_airport("\nEnter origin airport code: ", airport_codes)
    destination = get_valid_airport("Enter destination airport code: ", airport_codes)
    selected_airline = get_valid_airline("Enter selected airline (Code or Name): ", airline_names)

    # Get indices for the airports
    origin_index = airport_codes.index(origin)
    destination_index = airport_codes.index(destination)

    # Get shortest path distance, checks both ways
    shortest_distance = min(adj_matrix[origin_index][destination_index],
                            adj_matrix[destination_index][origin_index])
    if shortest_distance == 0:
        return print("Origin and destination are the same airport.")
    
    route_data = {"weather_condition": "Heavy Rain"}  # Replace with real API data if available
    
    weather_adjusted_distance = getWeatherCondition(route_data, shortest_distance)
    #  Check if the flight is cancelled
    if weather_adjusted_distance == "CANCELLED":
        print(f"Flight from {origin} to {destination} has been **CANCELLED** due to {route_data['weather_condition']}.")
        return  # Stop further processing

    # Proceed with price estimation if not cancelled
    # Get the price estimate
    price_estimate = getPriceEstimate(weather_adjusted_distance, selected_airline)

    # Print the result
    print(f"\nShortest distance from {origin} to {destination}: {weather_adjusted_distance} km" 
          if shortest_distance != float('inf') else 
          f"\nNo available route from {origin} to {destination}.")
    print(f"Price Estimate: ${price_estimate}")

findShortestPath() 
