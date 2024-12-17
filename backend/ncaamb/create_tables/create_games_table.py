import requests
import psycopg2
from dotenv import load_dotenv
import os

# Load environment vars from .env
load_dotenv()


def get_ncaa_games(connection, year, season_type):

    API_KEY = os.getenv("API_KEY")

    games_url = f"https://api.sportradar.com/ncaamb/trial/v8/en/games/{year}/{season_type}/schedule.json?api_key={API_KEY}"

    headers = {"accept": "application/json"}

    try:
        games_response = requests.get(games_url, headers=headers)

        create_ncaa_games_table(connection)

        if games_response.status_code == 200:
            games = games_response.json()

            insert_ncaa_games(connection, games)

        else:
            print(f"Failed to fetch teams: HTTP {games_response.status_code} - {games_response.text}")

    except requests.RequestException as e:
        print(f"Exception when calling games_url -> NCAA: {e}")


# Function to create the "ncaa_games" table
def create_ncaa_games_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ncaa_games (
                id VARCHAR(100) PRIMARY KEY,
                home_team VARCHAR(100),
                away_team VARCHAR(100),
                year INT NULL,
                date VARCHAR(100) NULL,
                season VARCHAR(100) NULL,
                conference_game BOOLEAN NULL,
                time_zone_venue VARCHAR(30) NULL,
                time_zone_home_team VARCHAR(30) NULL,
                time_zone_away_team VARCHAR(30) NULL,
                venue VARCHAR(100) NULL
            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'ncaa_games' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'ncaa_games' table in PostgreSQL:", e)



def insert_ncaa_games(connection, data):
    try:

        cursor = connection.cursor()

        year = data['season']['year']
        season = data['season']['id']

        for game in data['games']:
            cursor.execute(
                """
                INSERT INTO ncaa_games (id, home_team, away_team, year, date, season, conference_game, time_zone_venue, time_zone_home_team, time_zone_away_team, venue)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    game['id'],
                    game['home']['id'],
                    game['away']['id'],
                    year,
                    game['scheduled'],
                    season,
                    game['conference_game'],
                    game['time-zones']['venue'],
                    game['time-zones']['home'],
                    game['time-zones']['away'],
                    game['venue']['id']
                ),
            )
        connection.commit()
        cursor.close()

        print("Data inserted successfully into NCAA games.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error inserting data into PostgreSQL NCAA games:", e)

