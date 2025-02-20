from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mt5_login = db.Column(db.String(50), unique=True, nullable=False)
    mt5_password = db.Column(db.String(100), nullable=False)
    mt5_server = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.email}>'
