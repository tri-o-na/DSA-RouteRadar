import numpy as np
import pandas as pd

def InitAdjacencyMatrix(data):  # Accepts `data` as an argument
    # Step 1: Get all unique airport codes
    airport_codes = sorted(data.keys())  # Sort for consistent ordering
    num_airports = len(airport_codes)

    # Step 2: Create an adjacency matrix initialized with None
    adj_matrix = [[None] * num_airports for _ in range(num_airports)]

    # Step 3: Fill diagonal with 0 (self-to-self distance)
    for i in range(num_airports):
        adj_matrix[i][i] = [("N/A", "N/A", 0)]  # No airline, no duration

    # Step 4: Create airport index mapping
    airport_index = {code: i for i, code in enumerate(airport_codes)}

    # Step 5: Populate adjacency matrix with (airline_code, airline_name, duration)
    for airport, details in data.items():
        src_idx = airport_index[airport]
        for route in details["routes"]:
            dest_code = route["airport_code"]
            dest_idx = airport_index[dest_code]

            route_info = []
            for airline in route["airlines"]:
                airline_code = airline["airline_code"]
                airline_name = airline["airline_name"]
                duration = route["duration"]

                route_info.append((airline_code, airline_name, duration))

            # Store the route information in the matrix
            adj_matrix[src_idx][dest_idx] = route_info

    # Convert to DataFrame for better visualization
    df = pd.DataFrame(adj_matrix, index=airport_codes, columns=airport_codes)
    return df, airport_codes

# Call the function using the `data` variable from Colab
df, airport_codes = InitAdjacencyMatrix(data)

# Print result (optional)
print("Adjacency Matrix:\n", df)
