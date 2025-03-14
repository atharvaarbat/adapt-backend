import heapq
import csv
import ast
# Define connections between POCs (edges in the graph)
# Format: {POC id: [(connected POC id, distance)]}
graph = {}
poc_data = []

with open("poc.csv", "r") as file:  # Replace 'data.csv' with your actual file name
    reader = csv.reader(file)
    next(reader)  # Skip the header row

    for row in reader:
        ID = int(row[0])
        Name = row[1]
        Date = row[2]
        CategoryID = int(row[3])
        Category = row[4]
        Coordinates = ast.literal_eval(row[5])  # Convert string "(x, y)" to tuple (x, y)
        RiskLevel = int(row[6])

        poc_data.append([ID, Name, Date, CategoryID, Category, Coordinates, RiskLevel])
with open("roads.csv", "r") as file:  # Replace 'graph.csv' with your actual file name
    reader = csv.reader(file)
    next(reader)  # Skip the header row

    for source, destination, weight in reader:
        source, destination, weight = int(source), int(destination), int(weight)

        if source not in graph:
            graph[source] = []
        graph[source].append((destination, weight))

# Risk factor constant
RISK_FACTOR = 100

# Remove factor constant (extremely high cost to avoid specific POCs)
REMOVE_FACTOR = 999999

# Terrain factor constant
TERRAIN_FACTOR = 100

# Function to get the risk level of a POC
def get_risk_level(poc_id):
    for poc in poc_data:
        if poc[0] == poc_id:
            return poc[3]
    return 0  # Default to 0 if POC not found

# Function to get the terrain difficulty of a POC
def get_terrain_difficulty(poc_id):
    for poc in poc_data:
        if poc[0] == poc_id:
            return poc[6]
    return 0  # Default to 0 if POC not found

# Function to check if a POC is in the remove_poc list
def is_poc_in_remove_list(poc_id, remove_poc_names):
    for poc in poc_data:
        if poc[0] == poc_id and poc[1] in remove_poc_names:
            return True
    return False

# Modified Dijkstra's algorithm to consider risk levels, terrain difficulty, and remove_poc
def dijkstra(graph, start, end, remove_poc_names, USER_TERRAIN_FACTOR=1.0):
    queue = [(0, start, [])]  # (total cost, current node, path)
    visited = set()
    while queue:
        (total_cost, node, path) = heapq.heappop(queue)
        if node not in visited:
            visited.add(node)
            path = path + [node]
            if node == end:
                return total_cost, path
            for neighbor, distance in graph.get(node, []):
                if neighbor not in visited:
                    # Calculate total cost: distance + risk penalty + terrain penalty + remove penalty
                    risk_level = get_risk_level(neighbor)
                    risk_penalty = risk_level * RISK_FACTOR
                    terrain_difficulty = get_terrain_difficulty(neighbor)
                    terrain_penalty = terrain_difficulty * TERRAIN_FACTOR * USER_TERRAIN_FACTOR
                    remove_penalty = REMOVE_FACTOR if is_poc_in_remove_list(neighbor, remove_poc_names) else 0
                    heapq.heappush(queue, (total_cost + distance + risk_penalty + terrain_penalty + remove_penalty, neighbor, path))
    return float('inf'), []  # If no path is found

# Function to find the best route with remove_poc functionality
def find_best_route(start_id, end_id, remove_poc_names, USER_TERRAIN_FACTOR):
    if start_id not in graph or end_id not in graph:
        return "Invalid start or end POC ID."

    # Check if start or end POC is in the remove_poc list
    if is_poc_in_remove_list(start_id, remove_poc_names) or is_poc_in_remove_list(end_id, remove_poc_names):
        return "Start or end POC is in the remove_poc list."

    total_cost, path = dijkstra(graph, start_id, end_id, remove_poc_names, USER_TERRAIN_FACTOR)
    if total_cost == float('inf'):
        return "No route found."

    # Get POC details for the path
    route_details = []
    for poc_id in path:
        for poc in poc_data:
            if poc[0] == poc_id:
                route_details.append(poc)
                break

    return total_cost, route_details

# Example usage
start_id = 19  # Village S
end_id = 20    # City T
remove_poc_names = []  # POCs to avoid

total_cost, route = find_best_route(start_id, end_id, remove_poc_names, USER_TERRAIN_FACTOR=100.0)
if isinstance(route, str):
    print(route)
else:
    print(f"Best route total cost: {total_cost}")
    print("Route details:")
    for poc in route:
        print(f"POC ID: {poc[0]}, Name: {poc[1]}, Risk Level: {poc[3]}, Terrain Difficulty: {poc[6]}, Type: {poc[4]}, Coordinates: {poc[5]}")