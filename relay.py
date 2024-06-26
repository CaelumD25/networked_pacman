from flask import Flask, request, jsonify
import argparse
import json

app = Flask(__name__)

connection = [{"connect_code": "Imagines3-Payday-Impish"}]

# Global recording state for the movement and game state
movement_instructions = {}
game_state = {}

# Flag to track whether there has been a POST request from the AI process and Godot Process
ai_process_posted = False
godot_process_posted = False
moves = 0

@app.route('/players', methods=['GET', 'POST'])
def movement():
    global movement_instructions, ai_process_posted, move_finished, godot_process_posted, moves

    # Only the game process should be requesting get to players, this should not be called by the AI process(GET)
    if request.method == 'GET':
        if not ai_process_posted or moves <= 0:
            return "AI hasn't posted yet. Access denied.", 403

        moves -= 1
        ai_process_posted = False  # After the return it is no longer true, as an old instruction will be stored
        # Return the latest movement data to Godot game
        return jsonify(movement_instructions)
    # Only the AI process should be updating the instructions of the players(POST)
    elif request.method == 'POST':
        # Receive movement data from Godot game
        if ai_process_posted:
            return "Godot hasn't moved yet, ignoring this could result in missed moves. Access denied.", 403
        moves += 1

        movement_instructions = request.json
        # Records the freshness of the latest AI movement instruction, this should only be true before the game has read
        # it
        ai_process_posted = True
        return 'Movement data received and forwarded to AI'


@app.route('/game_state', methods=['GET', 'POST'])
def state():
    global godot_process_posted, game_state, ai_process_posted, moves
    # Receive game state data from Godot game, only the AI process should ever be requesting the game state
    if request.method == 'GET':
        if not godot_process_posted or moves != 0:
            return "Game hasn't posted yet. Access denied.", 403
        # Return the latest game state data to the AI process
        godot_process_posted = False
        return jsonify(game_state)
    # Update the game state, only the Godot game should ever be updating the game state
    elif request.method == 'POST':

        game_state = request.json
        # Records the freshness of the game state, this should be not true right after it is read or the players have
        # moved

        godot_process_posted = True
        return 'Game state data received and forwarded to AI'


@app.route('/connect', methods=['GET'])
def get_connection():
    return json.dumps(connection)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Start the intermediary relay server")
    parser.add_argument('--port', type=int, default=5000, help="Port number (default is 5000)")
    args = parser.parse_args()
    app.run(debug=True, port=args.port)  # You may want to set debug=False in production
