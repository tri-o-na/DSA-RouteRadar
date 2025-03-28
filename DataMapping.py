import json
import numpy as np
import pandas as pd

file_path = 'Data/airline_routes_custom.json' 
with open(file_path) as file:
    data = json.load(file)

def InitAdjacencyMatrix(data):  
    
    
    airport_codes = sorted(data.keys()) # Pull all the airports and sort them
    num_airports = len(airport_codes) # Count the no. of airports
    
    adj_matrix = [[None] * num_airports for _ in range(num_airports)] #initialise adjacency matrix
    for i in range(num_airports):
        adj_matrix[i][i] = [("N/A", "N/A", 0)] # Set the diagonal value to [("N/A", "N/A", 0)]
    # Meaning: No airline, no destination, and a travel duration of 0
    # This represents "self-loops" (i.e., no need to travel from an airport to itself)

   
    airport_index = {code: i for i, code in enumerate(airport_codes)} # create a dictionary to map airport codes to their corresponding index in the adjacency matrix

   
    for airport, details in data.items(): # get the row index of source airport
        src_idx = airport_index[airport]
        for route in details["routes"]:  # iterate thru connections from the source airport
            dest_code = route["airport_code"] # get dest airport code
            dest_idx = airport_index[dest_code] #get column index for destination airport

            route_info = []
            for airline in route["airlines"]:
                airline_code = airline["airline_code"]
                airline_name = airline["airline_name"]
                duration = route["duration"]
                distance = route["distance"]
                base_price = route["base_price"]
                
                route_info.append((airline_code, airline_name, duration, distance, base_price)) #store all details as tuple, add to list
                
            # Store the route information in the matrix
            adj_matrix[src_idx][dest_idx] = route_info

    # Convert to DataFrame for better visualization
    df = pd.DataFrame(adj_matrix, index=airport_codes, columns=airport_codes)
    return df, airport_codes

# Call the function using the `data` variable loaded from the JSON file
df, airport_codes = InitAdjacencyMatrix(data)

# Print result (optional)
print("Adjacency Matrix:\n", df)
