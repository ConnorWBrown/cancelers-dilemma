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
from flask_sqlalchemy import SQLAlchemy
import uuid
import json
from datetime import datetime


app = Flask(__name__)
# Simple SQLite DB in project root; change as needed for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)  # Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": ["http://192.168.49.2:30500", "http://192.168.1.24:3000", "http://172.20.10.2:3000", "http://localhost:3000", "http://127.0.0.1:58244", "http://127.0.0.1:58214", "http://frontend.cancelers-dilemma.svc.cluster.local:80", "http://backend.cancelers-dilemma.svc.cluster.local:80"]}})


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.String(36), primary_key=True)
    player1_clicked = db.Column(db.Boolean, nullable=True)
    player1_ready = db.Column(db.Boolean, default=False)
    player2_clicked = db.Column(db.Boolean, nullable=True)
    player2_ready = db.Column(db.Boolean, default=False)
    results = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'player1_clicked': self.player1_clicked,
            'player1_ready': self.player1_ready,
            'player2_clicked': self.player2_clicked,
            'player2_ready': self.player2_ready,
            'results': json.loads(self.results) if self.results else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


with app.app_context():
    db.create_all()

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
    # Expecting: { player_id: 'player1'|'player2', clicked: bool, optional game_id: uuid }
    data = request.get_json()
    if not data or 'player_id' not in data or 'clicked' not in data:
        return jsonify({"error": "Invalid input"}), 400

    player_id = data['player_id']
    clicked = data['clicked']
    game_id = data.get('game_id')

    if player_id not in ('player1', 'player2'):
        return jsonify({"error": "Invalid player_id"}), 400

    # create new game if no game_id provided
    if not game_id:
        game_id = str(uuid.uuid4())[:8]
        game = Game(id=game_id)
        db.session.add(game)
        db.session.commit()
    else:
        game = Game.query.get(game_id)
        if not game:
            # create new game with provided id
            game = Game(id=game_id)
            db.session.add(game)
            db.session.commit()

    # update player state
    if player_id == 'player1':
        game.player1_clicked = bool(clicked)
        game.player1_ready = True
    else:
        game.player2_clicked = bool(clicked)
        game.player2_ready = True

    db.session.commit()

    # If both ready -> compute result
    if (game.player1_ready or game.player1_clicked is not None) and (game.player2_ready or game.player2_clicked is not None) and game.player1_ready and game.player2_ready:
        p1 = bool(game.player1_clicked)
        p2 = bool(game.player2_clicked)

        excuse = cancel_excuses[0]

        results = {}
        if p1 and p2:
            results = {"player1": "Enjoy the couch :)", "player2": "Enjoy the couch :)"}
        elif p1 and not p2:
            results = {"player1": "Try this excuse: \"" + excuse + "\" if you would like to for-real cancel.", "player2": "Have fun!"}
        elif not p1 and p2:
            results = {"player1": "Have fun!", "player2": "Try this excuse: \"" + excuse + "\" if you would like to for-real cancel."}
        else:
            results = {"player1": "Neither of you canceled! Have fun!", "player2": "Neither of you canceled! Have fun!"}

        game.results = json.dumps(results)
        # reset ready flags for next round
        game.player1_ready = False
        game.player2_ready = False
        db.session.commit()

        response = jsonify({"game_id": game.id, "result": results[player_id]})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # otherwise indicate to caller that we are waiting. return game_id so client can poll
    return jsonify({"waiting": True, "game_id": game.id})

@app.route('/result/<game_id>/<player_id>', methods=['GET'])
def get_result(game_id, player_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    results = json.loads(game.results) if game.results else {}
    result = results.get(player_id)
    response = jsonify({"result": result})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/clear', methods=['POST'])
def clear():
    # If game_id provided, clear that game; otherwise clear all games
    game_id = request.args.get('game_id')
    if game_id:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
        db.session.delete(game)
        db.session.commit()
        return jsonify({"message": f"Game {game_id} cleared"})
    else:
        # clear all
        num = Game.query.delete()
        db.session.commit()
        return jsonify({"message": f"Cleared {num} games"})

if __name__ == '__main__':
    # Avoid using debug mode to prevent multiprocessing issues in sandboxed environments
    app.run(port=30500, debug=False)
