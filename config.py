import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("postgresql://postgres.bzaztdjdgpnpzocjvxnj:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres")  # Uses environment variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False
