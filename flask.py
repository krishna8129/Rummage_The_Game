from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import random
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

class GameSession(db.Model):
    id = db.Column(db.String, primary_key=True)
    host_id = db.Column(db.String, db.ForeignKey('user.id'))
    players = db.Column(db.PickleType)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(id=str(uuid.uuid4()), username=data['username'], password=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': 'registered'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        user.last_active = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'logged_in'})
    return jsonify({'status': 'failed'})

@app.route('/create_session', methods=['POST'])
def create_session():
    if 'user_id' not in session:
        return jsonify({'status': 'unauthorized'})
    game_id = str(uuid.uuid4())
    game = GameSession(id=game_id, host_id=session['user_id'], players=[session['user_id']])
    db.session.add(game)
    db.session.commit()
    return jsonify({'game_id': game_id})

@app.route('/join_session/<game_id>', methods=['POST'])
def join_session(game_id):
    if 'user_id' not in session:
        return jsonify({'status': 'unauthorized'})
    game = GameSession.query.get(game_id)
    if game and game.is_active:
        game.players.append(session['user_id'])
        db.session.commit()
        return jsonify({'status': 'joined'})
    return jsonify({'status': 'failed'})

@app.route('/end_session/<game_id>', methods=['POST'])
def end_session(game_id):
    game = GameSession.query.get(game_id)
    if game and game.host_id == session.get('user_id'):
        game.is_active = False
        db.session.commit()
        return jsonify({'status': 'ended'})
    return jsonify({'status': 'unauthorized'})

@app.route('/score', methods=['POST'])
def update_score():
    if 'user_id' not in session:
        return jsonify({'status': 'unauthorized'})
    data = request.json
    user = User.query.get(session['user_id'])
    user.score += data.get('points', 0)
    lb = Leaderboard(user_id=user.id, score=user.score)
    db.session.add(lb)
    db.session.commit()
    return jsonify({'new_score': user.score})

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    top = Leaderboard.query.order_by(Leaderboard.score.desc()).limit(10).all()
    result = [{'user_id': l.user_id, 'score': l.score} for l in top]
    return jsonify(result)

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Welcome to the game server'})

@socketio.on('join_game')
def handle_join_game(data):
    room = data.get('game_id')
    join_room(room)
    emit('player_joined', {'player': session.get('user_id')}, room=room)

@socketio.on('leave_game')
def handle_leave_game(data):
    room = data.get('game_id')
    leave_room(room)
    emit('player_left', {'player': session.get('user_id')}, room=room)

@socketio.on('game_event')
def handle_game_event(data):
    room = data.get('game_id')
    emit('event', data, room=room)

def cleanup_sessions():
    while True:
        now = datetime.utcnow()
        expired = GameSession.query.filter(GameSession.created_at < now - timedelta(hours=1)).all()
        for game in expired:
            game.is_active = False
        db.session.commit()
        threading.Event().wait(3600)

threading.Thread(target=cleanup_sessions, daemon=True).start()

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000)
