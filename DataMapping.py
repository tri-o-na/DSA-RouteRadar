# Initalize Function to get the data to the class
import json
import numpy as np
import pandas as pd

def InitAdjancyMatrix():
    # Step 0: Get the data file
    file_path = 'Data/airline_routes_custom.json' # This is the json file path used for reference. Check if the path is correct
    file = open(file_path)
    data = json.load(file)

    # Step 1: Get all unique airport codes
    airport_codes = sorted(data.keys())  # Sort for consistent ordering
    num_airports = len(airport_codes)

    # Step 2: Create an adjacency matrix initialized with infinity
    INF = float('inf')
    adj_matrix = np.full((num_airports, num_airports), INF)

    # Step 3: Fill diagonal with 0 (self-to-self distance)
    np.fill_diagonal(adj_matrix, 0)

    # Step 4: Use a set to track stored edges
    stored_routes = set()
    airline_codes = set()  # ✅ Store unique airline codes
    airline_names = {}  # ✅ Store airline names (code → name)
    airport_index = {code: i for i, code in enumerate(airport_codes)}

    # Step 5: Populate the adjacency matrix, storing only one direction
    for airport, details in data.items():
        src_idx = airport_index[airport]
        for route in details["routes"]:
            dest_code = route["airport_code"]
            dest_idx = airport_index[dest_code]

            # Extract airline data from the route
            for airline in route["airlines"]:
                airline_code = airline["airline_code"]
                airline_name = airline["airline_name"]

                airline_codes.add(airline_code)  # Store airline code
                airline_names[airline_code] = airline_name  # Store airline name

            # Ensure we store only one direction: (min, max) ordering
            edge = tuple(sorted([airport, dest_code]))
            if edge not in stored_routes:
                adj_matrix[src_idx][dest_idx] = route["distance"]
                stored_routes.add(edge)

    # Step 6: Return adjancy matrix
    df = pd.DataFrame(adj_matrix, index=airport_codes, columns=airport_codes)
    return df, airport_codes, airline_names

df = InitAdjancyMatrix()
# Dont need to print the adjancy matrix (user should not see this)
print("Adjacency Matrix (Labeled):\n", df)