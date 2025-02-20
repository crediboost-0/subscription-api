from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mt5_login = db.Column(db.String(20), unique=True, nullable=False)
    broker_server = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.mt5_login}>"
