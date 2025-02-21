from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_key = db.Column(db.String(32), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.email} - Active: {self.is_active}>"
