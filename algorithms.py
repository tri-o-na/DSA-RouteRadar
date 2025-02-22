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

def findShortestPath():
    """Loads the adjacency matrix and runs the Floyd-Warshall algorithm."""
    adj_matrix, airport_codes = InitAdjancyMatrix()

    # Convert DataFrame to NumPy array if it's a DataFrame
    if isinstance(adj_matrix, pd.DataFrame):
        adj_matrix = adj_matrix.to_numpy()

    # Run Floyd-Warshall on adjacency matrix
    floydWarshall(adj_matrix)

    # Let user input origin and destination
    print("\nAvailable Airports:", ", ".join(airport_codes))

    # Validity check for origin and destination
    origin = get_valid_airport("Enter origin airport code: ", airport_codes)
    destination = get_valid_airport("Enter destination airport code: ", airport_codes)

    # Get indices for the airports
    origin_index = airport_codes.index(origin)
    destination_index = airport_codes.index(destination)

    # Get shortest path distance, checks both ways
    shortest_distance = min(adj_matrix[origin_index][destination_index],
                            adj_matrix[destination_index][origin_index])
    
    if shortest_distance == 0:
        return print("Origin and destination are the same airport.")

    # Print the result
    print(f"\nShortest distance from {origin} to {destination}: {shortest_distance} km" 
          if shortest_distance != float('inf') else 
          f"\nNo available route from {origin} to {destination}.")

# Example usage:
findShortestPath() 
