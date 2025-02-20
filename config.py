import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    os.getenv("postgresql://crediboostdb_user:Ht4pT3m1t7BN5ACHHTalZ92Jm8WlhdEx@dpg-curihnbv2p9s73aj56f0-a/crediboostdb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
