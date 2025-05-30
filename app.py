#Flask Application Setup basics:

# import os

# from flask import Flask


# def create_app(test_config=None):
#     # create and configure the app
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_mapping(
#         SECRET_KEY='dev',
#         DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
#     )

#     if test_config is None:
#         # load the instance config, if it exists, when not testing
#         app.config.from_pyfile('config.py', silent=True)
#     else:
#         # load the test config if passed in
#         app.config.from_mapping(test_config)

#     # ensure the instance folder exists
#     try:
#         os.makedirs(app.instance_path)
#     except OSError:
#         pass

#     # a simple page that says hello
#     @app.route('/hello')
#     def hello():
#         return 'Hello, World!'

#     return app


# ////// End of Flask Application Setup basics //////



# # Python Backend (Flask)
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Helper function to initialize game state
def initialize_game_state():
    return {
        "player1": {"clicked": None, "ready": False},
        "player2": {"clicked": None, "ready": False},
        "results": {}
    }

# In-memory game state
game_state = initialize_game_state()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    if not data or 'player_id' not in data or 'clicked' not in data:
        return jsonify({"error": "Invalid input"}), 400

    player_id = data['player_id']
    clicked = data['clicked']

    if player_id not in game_state:
        return jsonify({"error": "Invalid player_id"}), 400

    game_state[player_id]["clicked"] = clicked
    game_state[player_id]["ready"] = True

    if all(p["ready"] for p in [game_state["player1"], game_state["player2"]]):
        p1 = game_state["player1"]["clicked"]
        p2 = game_state["player2"]["clicked"]

        if p1 and p2:
            game_state["results"] = {
                "player1": "Enjoy the couch :)",
                "player2": "Enjoy the couch :)"
            }
        elif p1 and not p2:
            game_state["results"] = {
                "player1": "Try this excuse: an opposum is hiding in my house and I must coax it out",
                "player2": "Have fun!"
            }
        elif not p1 and p2:
            game_state["results"] = {
                "player1": "Have fun!",
                "player2": "Try this excuse: an opposum is hiding in my house and I must coax it out"
            }
        else:
            game_state["results"] = {
                "player1": "Neither of you canceled! Have fun!",
                "player2": "Neither of you canceled! Have fun!"
            }

        game_state["player1"]["ready"] = False
        game_state["player2"]["ready"] = False

        response = jsonify({"result": game_state["results"][player_id]})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


    return jsonify({"waiting": True})

@app.route('/result/<player_id>', methods=['GET'])
def get_result(player_id):
    result = game_state["results"].get(player_id)
    response = jsonify({"result": result})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/clear', methods=['POST'])
def clear():
    global game_state
    game_state = {
        "player1": {"clicked": None, "ready": False},
        "player2": {"clicked": None, "ready": False},
        "results": {}
    }
    response = jsonify({"message": "Game state cleared"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    # Avoid using debug mode to prevent multiprocessing issues in sandboxed environments
    app.run(host='0.0.0.0', port=5000, debug=False)
