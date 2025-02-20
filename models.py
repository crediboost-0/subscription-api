from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets  # Generates secure random API keys

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    api_key = db.Column(db.String(64), unique=True, default=lambda: secrets.token_hex(32))  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"
