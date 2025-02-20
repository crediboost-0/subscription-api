import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("postgresql://postgres:[Zesh1604!]@db.bzaztdjdgpnpzocjvxnj.supabase.co:5432/postgres")  # Uses environment variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False
