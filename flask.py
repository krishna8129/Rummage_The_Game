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
