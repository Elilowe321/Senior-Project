import requests
import psycopg2
from dotenv import load_dotenv
import os

# Load environment vars from .env
load_dotenv()


def get_ncaa_teams(connection):

    teams_url = f"https://api.sportradar.com/ncaamb/trial/v8/en/league/teams.json?api_key={os.getenv("API_KEY")}"
    headers = {"accept": "application/json"}

    try:
        team_response = requests.get(teams_url, headers=headers)

        create_ncaa_teams_table(connection)

        if team_response.status_code == 200:
            teams = team_response.json()

            insert_ncaa_teams(teams)

        else:
            print(f"Failed to fetch teams: HTTP {team_response.status_code} - {team_response.text}")

    except requests.RequestException as e:
        print(f"Exception when calling teams_url -> NCAA: {e}")


# Function to create the "ncaa_teams" table
def create_ncaa_teams_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ncaa_teams (
                id INT PRIMARY KEY,
                school VARCHAR(100),
                alias VARCHAR(30),
                mascot VARCHAR(50)
            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'ncaa_teams' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'ncaa_teams' table in PostgreSQL:", e)


def insert_ncaa_teams(connection, data):
    try:
        cursor = connection.cursor()
        for team in data['teams']:
            cursor.execute(
                """
                INSERT INTO ncaa_teams (id, school, alias, mascot)
                VALUES (%s, %s, %s, %s,)
            """,
                (
                    team.id,
                    team.market,
                    team.alias,
                    team.name
                ),
            )
        connection.commit()
        cursor.close()

        print("Data inserted successfully into NCAA teams.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error inserting data into PostgreSQL NCAA teams:", e)


