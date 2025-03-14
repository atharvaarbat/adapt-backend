from flask import Flask, request, jsonify
from route_gen import find_best_route  # Import the routing logic script

app = Flask(__name__)

@app.route('/find_route', methods=['POST'])
def find_route():
    # Get JSON payload from the request
    data = request.get_json()

    # Validate required fields
    if not data or 'start' not in data or 'end' not in data:
        return jsonify({"error": "Missing 'start' or 'end' in request body"}), 400

    # Extract parameters
    start = data.get('start')
    end = data.get('end')
    remove_array = data.get('remove_array', [])  # Default to empty list if not provided
    terrain_difficulty = data.get('terrain_difficulty', 0)  # Default to 0 if not provided

    # Call the find_best_route function from routing_logic
    try:
        total_cost, route = find_best_route(start, end, remove_array, terrain_difficulty)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Prepare the response
    if isinstance(route, str):
        return jsonify({"message": route}), 404
    else:
        return jsonify({
            "total_cost": total_cost,
            "route": route
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)