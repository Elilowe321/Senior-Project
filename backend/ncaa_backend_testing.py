# from ncaamb.create_tables import get_ncaa_teams
from cfb.create_tables import create_betting_lines_table
from cfb.database.database_commands import create_connection
import requests
import psycopg2
from dotenv import load_dotenv
import os

# Load environment vars from .env
load_dotenv()
 

connection = create_connection()


connection.close()

