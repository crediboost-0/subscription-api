import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("https://bzaztdjdgpnpzocjvxnj.supabase.co")  # Uses environment variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False
