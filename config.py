import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("postgresql://crediboostdb_user:Ht4pT3m1t7BN5ACHHTalZ92Jm8WlhdEx@dpg-curihnbv2p9s73aj56f0-a/crediboostdb")  # Uses environment variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False
