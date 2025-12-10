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
import random
from flask import request


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": ["http://192.168.49.2:30500", "http://172.20.10.2:3000", "http://localhost:3000", "http://127.0.0.1:58244", "http://127.0.0.1:58214", "http://frontend.cancelers-dilemma.svc.cluster.local:80", "http://backend.cancelers-dilemma.svc.cluster.local:80"]}})

# Helper function to initialize game state
def initialize_game_state():
    return {
        "player1": {"clicked": None, "ready": False},
        "player2": {"clicked": None, "ready": False},
        "results": {}
    }

# In-memory game state
game_state = initialize_game_state()

# Excuses:
cancel_excuses = [
    "an opposum is hiding in my house and I must coax it out",
    "I have to wash my hair, even though I just did it yesterday",
    "I’m in a committed relationship with my couch and we have plans",
    "I’m currently in a staring contest with my cat and I can’t lose",
    "I have to reorganize my sock drawer by color, size, and emotional significance",
    "I’m in a deep philosophical debate with my houseplants about the meaning of life",
    "I have to finish a very important Netflix documentary about cheese",
    "I was emotionally ambitious when I made those plans",
    "I’m currently in pajamas and the window to change has closed",
    "Let’s pretend we hung out and it was amazing. Great job, us",
    "I used all my social energy on a 3-minute phone call with the pharmacy",
    "I'm not ghosting — I'm just buffering in real life",
    "I can't make it. I’m deep in a spiral about whether avocados have feelings",
    "My will to interact was last seen at 3pm. It has not returned",
    "I need a night off from pretending I have it together",
    "Today's vibe is ‘do nothing and overthink it.’ Raincheck?",
    "Love you deeply, but I’ve entered goblin mode and there’s no turning back tonight",
    
    # Astrology excuses
    "Mercury's in retrograde and so is my entire life",
    "My birth chart says today is a ‘stay in and avoid all humans’ kind of day",
    "The moon is in my feelings house and I cannot emotionally relocate",
    "Saturn just gave me a performance review. I failed",
    
    # Apocalyptic emergencies
    "The skies turned orange again and my motivation evaporated",
    "Ran out of coffee and civilization shortly followed",
    "My fridge is making a sound I can only describe as 'final warning'",
    "I opened my email and unleashed a minor portal to another realm",
    "It’s raining sideways and I took that personally",
    "My existential dread needs a night in"
]

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

        excuse = cancel_excuses[0]
        # excuse = cancel_excuses[random.randint(0, len(cancel_excuses) - 1)]

        if p1 and p2:
            game_state["results"] = {
                "player1": "Enjoy the couch :)",
                "player2": "Enjoy the couch :)"
            }
        elif p1 and not p2:
            game_state["results"] = {
                # "player1": "Try this excuse: \"an opposum is hiding in my house and I must coax it out\"",
                "player1": "Try this excuse: \"" + excuse + "\" if you would like to for-real cancel.",
                "player2": "Have fun!"
            }
        elif not p1 and p2:
            game_state["results"] = {
                "player1": "Have fun!",
                # "player2": "Try this excuse: \"an opposum is hiding in my house and I must coax it out\""
                "player2": "Try this excuse: \"" + excuse + "\" if you would like to for-real cancel."

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
    event = request.args.get('event')
    response = jsonify({"message": "Game state cleared"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    # Avoid using debug mode to prevent multiprocessing issues in sandboxed environments
    app.run(host='0.0.0.0', port=5000, debug=False)
