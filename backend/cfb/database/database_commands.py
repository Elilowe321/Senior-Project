import psycopg2
import os
from dotenv import load_dotenv
from global_vars import Global


# Load environment vars from .env
load_dotenv()


# Configure to cfbd api
def cfbd_configuration():
    import cfbd

    configuration = cfbd.Configuration()
    configuration.api_key["Authorization"] = (
        "kjsyUDd6vFuPIPL6wDhlGPDrYILbYlZDoUo64iE8c8qtSLHwL6pX/iSEzz5fxbhJ"
    )
    configuration.api_key_prefix["Authorization"] = "Bearer"

    return configuration


# Function to create a connection to the PostgreSQL database
def create_connection():
    try:

        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            # host="localhost",
            port=os.getenv("DB_PORT"),
        )
        return connection
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)
        return None


# Select all from any table name
def select_table(connection, table_name):
    try:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT *
                FROM {table_name}
        """
        )
        rows = cursor.fetchall()
        connection.commit()
        cursor.close()

        return rows

    except psycopg2.Error as e:
        connection.rollback()
        print("Error creating 'game_stats' table in PostgreSQL:", e)


def get_team_average_stats_new(connection, columns, team_id, year, prefix):
    try:
        # Construct lists for home and away columns
        home_columns = [col for col in columns if col.startswith("home_")]
        away_columns = [col for col in columns if col.startswith("away_")]

        cursor = connection.cursor()

        # Query home and away averages in a single query for each
        home_avg_query = f"""
            SELECT {', '.join([f"AVG({col}) AS {prefix}{col.split('_', 1)[1]}" for col in home_columns])}
            FROM (
                SELECT 
                    tgs.*,
                    COALESCE(home_team.talent, 50) AS home_talent,
                    COALESCE(away_team.talent, 50) AS away_talent
                FROM 
                    team_game_stats tgs
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) home_team ON (home_team.id = tgs.home_school_id) AND (home_team.year = tgs.year)
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) away_team ON (away_team.id = tgs.away_school_id) AND (away_team.year = tgs.year)
            )
            WHERE home_school_id = {team_id}
            AND year = {year};
        """
        cursor.execute(home_avg_query)
        column_names = [desc[0] for desc in cursor.description]
        home_avgs = cursor.fetchone()
        home_avg_with_names = dict(zip(column_names, home_avgs))

        away_avg_query = f"""
            SELECT {', '.join([f"AVG({col}) AS {prefix}{col.split('_', 1)[1]}" for col in away_columns])}
            FROM (
                SELECT 
                    tgs.*,
                    COALESCE(home_team.talent, 50) AS home_talent,
                    COALESCE(away_team.talent, 50) AS away_talent
                FROM 
                    team_game_stats tgs
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) home_team ON (home_team.id = tgs.home_school_id) AND (home_team.year = tgs.year)
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) away_team ON (away_team.id = tgs.away_school_id) AND (away_team.year = tgs.year)
            )
            WHERE away_school_id = {team_id}
            AND year = {year};
        """
        cursor.execute(away_avg_query)
        column_names = [desc[0] for desc in cursor.description]
        away_avgs = cursor.fetchone()
        away_avg_with_names = dict(zip(column_names, away_avgs))

        # Combine home and away averages
        averages = {}
        for key in home_avg_with_names:
            home_value = home_avg_with_names[key]
            away_value = away_avg_with_names.get(key)
            if home_value is not None and away_value is not None:
                averages[key] = (home_value + away_value) / 2
            elif home_value is not None:
                averages[key] = home_value
            elif away_value is not None:
                averages[key] = away_value
            elif home_value is None and away_value is None:
                averages[key] = 0
    
        
        
        # print("ID: ", team_id)
        # print(averages)
        

        return averages

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


    #     for i, col in enumerate(home_columns):
    #         key = f"{prefix}{col.split('_', 1)[1]}"
    #         home_avg_value = home_avgs[i] if home_avgs and home_avgs[i] is not None else None
    #         away_avg_value = None  # Default to None since this is a home stat
    #         averages[key] = home_avg_value if home_avg_value is not None else 0

    #     for i, col in enumerate(away_columns):
    #         key = f"{prefix}{col.split('_', 1)[1]}"
    #         home_avg_value = averages.get(key, None)
    #         away_avg_value = away_avgs[i] if away_avgs and away_avgs[i] is not None else None

    #         if home_avg_value is not None and away_avg_value is not None:
    #             combined_avg = (home_avg_value + away_avg_value) / 2
    #         elif home_avg_value is not None:
    #             combined_avg = home_avg_value
    #         elif away_avg_value is not None:
    #             combined_avg = away_avg_value
    #         else:
    #             combined_avg = 0  # No data at all for either home or away

    #         averages[key] = combined_avg

    #     connection.commit()
    #     cursor.close()

    #     print(averages)

    #     return averages

    # except Exception as e:
    #     print(f"Error: {e}")
    #     return None


def get_team_average_stats(connection, columns, team_id, year, week, prefix):
    try:
        # Construct lists for home and away columns
        home_columns = [col for col in columns if col.startswith("home_")]
        away_columns = [col for col in columns if col.startswith("away_")]

        cursor = connection.cursor()

        # Query home and away averages in a single query for each
        home_avg_query = f"""
            SELECT {', '.join([f"AVG({col}) AS {prefix}{col.split('_', 1)[1]}" for col in home_columns])}
            FROM (
                SELECT 
                    tgs.*,
                    COALESCE(home_team.talent, 50) AS home_talent,
                    COALESCE(away_team.talent, 50) AS away_talent,
                    g.week
                FROM 
                    team_game_stats tgs
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) home_team ON (home_team.id = tgs.home_school_id) AND (home_team.year = tgs.year)
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) away_team ON (away_team.id = tgs.away_school_id) AND (away_team.year = tgs.year)
                LEFT JOIN 
                    games g ON g.id = tgs.game_id
                WHERE 
                    tgs.home_school_id = {team_id}
                    AND tgs.year = {year}
                    AND g.week < {week}
            ) subquery;
        """
        cursor.execute(home_avg_query)
        column_names = [desc[0] for desc in cursor.description]
        home_avgs = cursor.fetchone()
        home_avg_with_names = dict(zip(column_names, home_avgs))

        away_avg_query = f"""
            SELECT {', '.join([f"AVG({col}) AS {prefix}{col.split('_', 1)[1]}" for col in away_columns])}
            FROM (
                SELECT 
                    tgs.*,
                    COALESCE(home_team.talent, 50) AS home_talent,
                    COALESCE(away_team.talent, 50) AS away_talent,
                    g.week
                FROM 
                    team_game_stats tgs
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) home_team ON (home_team.id = tgs.home_school_id) AND (home_team.year = tgs.year)
                LEFT JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) away_team ON (away_team.id = tgs.away_school_id) AND (away_team.year = tgs.year)
                LEFT JOIN 
                    games g ON g.id = tgs.game_id
                WHERE 
                    tgs.away_school_id = {team_id}
                    AND tgs.year = {year}
                    AND g.week < {week}
            ) subquery;
        """
        cursor.execute(away_avg_query)
        column_names = [desc[0] for desc in cursor.description]
        away_avgs = cursor.fetchone()
        away_avg_with_names = dict(zip(column_names, away_avgs))

        print("YEAR: ", year, ", Week: ", week)
        print("TEAM ID: ", team_id)
        print("Home AVERAGE: ", home_avg_with_names)
        print("Away AVERAGE: ", away_avg_with_names)

        # Combine home and away averages
        averages = {}
        for key in home_avg_with_names:
            home_value = home_avg_with_names[key]
            away_value = away_avg_with_names.get(key)
            if home_value is not None and away_value is not None:
                averages[key] = (home_value + away_value) / 2
            elif home_value is not None:
                averages[key] = home_value
            elif away_value is not None:
                averages[key] = away_value
            elif home_value is None and away_value is None:
                averages[key] = 0
    

        return averages

    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def game_lines(connection, game_id):
    try:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            Select *
                from betting_lines
                where game_id = {game_id};
        """
        )
        rows = cursor.fetchall()
        connection.commit()
        cursor.close()

        return rows

    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'game_stats' table in PostgreSQL:", e)


def get_winner(connection, game_id):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT home_points, away_points
            FROM games
            WHERE id = {game_id};
            """
        )
        rows = cursor.fetchall()
        cursor.close()

        if not rows:
            return 0, 0  # Return (0, 0) if no rows are found

        home_points, away_points = rows[0]

        # Ensure the values are integers
        home_points = home_points if home_points is not None else 0
        away_points = away_points if away_points is not None else 0

        return home_points, away_points

    except psycopg2.Error as e:
        connection.rollback()
        print("Error fetching game data:", e)
        return 0, 0  # Return (0, 0) in case of an error
    
    

# Function to get the score of a specific game
def get_actual_score(connection, home_team, away_team):
    try:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT home_points, away_points, home_post_win_prob, away_post_win_prob
                FROM games
                WHERE home_team = '{home_team}'
                AND away_team = '{away_team}'
                AND season = {Global.year}
        """
        )
        rows = cursor.fetchall()
        connection.commit()
        cursor.close()

        return rows

    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'game_stats' table in PostgreSQL:", e)


# Function to create the "game_stats" table
def create_game_stats_table(connection):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_game_stats (
                game_id INT,
                year INT,
                home_school_id INT,
                home_home_away VARCHAR,
                home_points INT,
                home_rushingAttempts INT NULL,
                home_rushingYards INT NULL,
                home_yardsPerPass FLOAT NULL,
                home_completionPercentage INT NULL, 
                home_netPassingYards INT NULL,
                home_totalYards INT NULL,
                home_fourthDownEff INT NULL,
                home_thirdDownEff INT NULL,
                home_firstDowns INT NULL,
                home_rushingTDs INT NULL,
                home_puntReturnYards INT NULL,
                home_puntReturnTDs INT NULL,
                home_puntReturns INT NULL,
                home_passingTDs INT NULL,
                home_kickReturnYards INT NULL,
                home_kickReturnTDs INT NULL,
                home_kickReturns INT NULL,
                home_kickingPoints INT NULL,
                home_interceptionYards INT NULL,
                home_interceptionTDs INT NULL,
                home_passesIntercepted INT NULL,
                home_fumblesRecovered INT NULL,
                home_totalFumbles FLOAT NULL,
                home_tacklesForLoss FLOAT NULL,
                home_defensiveTDs INT NULL,
                home_tackles INT NULL,
                home_sacks INT NULL,
                home_qbHurries INT NULL,
                home_passesDeflected INT NULL,
                home_possessionTime INT NULL,
                home_interceptions INT NULL,
                home_fumblesLost INT NULL,
                home_turnovers INT NULL,
                home_totalPenaltiesYards INT NULL,
                home_yardsPerRushAttempt FLOAT NULL,
                away_school_id INT,
                away_home_away VARCHAR,
                away_points INT,
                away_rushingAttempts INT NULL,
                away_rushingYards INT NULL,
                away_yardsPerPass FLOAT NULL,
                away_completionPercentage INT NULL, 
                away_netPassingYards INT NULL,
                away_totalYards INT NULL,
                away_fourthDownEff INT NULL,
                away_thirdDownEff INT NULL,
                away_firstDowns INT NULL,
                away_rushingTDs INT NULL,
                away_puntReturnYards INT NULL,
                away_puntReturnTDs INT NULL,
                away_puntReturns INT NULL,
                away_passingTDs INT NULL,
                away_kickReturnYards INT NULL,
                away_kickReturnTDs INT NULL,
                away_kickReturns INT NULL,
                away_kickingPoints INT NULL,
                away_interceptionYards INT NULL,
                away_interceptionTDs INT NULL,
                away_passesIntercepted INT NULL,
                away_fumblesRecovered INT NULL,
                away_totalFumbles FLOAT NULL,
                away_tacklesForLoss FLOAT NULL,
                away_defensiveTDs INT NULL,
                away_tackles INT NULL,
                away_sacks INT NULL,
                away_qbHurries INT NULL,
                away_passesDeflected INT NULL,
                away_possessionTime INT NULL,
                away_interceptions INT NULL,
                away_fumblesLost INT NULL,
                away_turnovers INT NULL,
                away_totalPenaltiesYards INT NULL,
                away_yardsPerRushAttempt FLOAT NULL
            )
        """
        )

        connection.commit()
        cursor.close()

        print("Table 'game_stats' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'game_stats' table in PostgreSQL:", e)


# Function to insert data into the game_stats table
def insert_game_stats_data(connection, data, year):
    try:
        cursor = connection.cursor()

        # Go through every game
        for game in data:

            # Check if game was already added
            tableName = "team_game_stats"
            cursor.execute(
                f"""SELECT game_id
                            FROM {tableName}
                            """
            )

            # Fetch all rows
            rows = cursor.fetchall()

            # If the game has not been added, add it
            if game.id not in [row[0] for row in rows]:

                # Make dictonary for easy sql input
                game_data_dict = {}
                game_data_dict["game_id"] = game.id
                game_data_dict["year"] = year

                # In every game, go through each of the teams that played
                for team in game.teams:

                    if team.home_away == "home":
                        prefix = "home_"
                    else:
                        prefix = "away_"

                    # cat = f"{prefix}{team.stats[i].category}"

                    game_data_dict[f"{prefix}school_id"] = team.school_id
                    game_data_dict[f"{prefix}home_away"] = team.home_away
                    game_data_dict[f"{prefix}points"] = team.points

                    # For every team, go through each of the teams stats
                    for i in range(len(team.stats)):
                        cat = f"{prefix}{team.stats[i].category}"

                        # Change the format of completionAttempts and put it into percentage
                        if team.stats[i].category == "completionAttempts":
                            completions = int(team.stats[i].stat.split("-")[0])
                            attempts = int(team.stats[i].stat.split("-")[1])
                            if attempts == 0:
                                completion_percentage = None
                            else:
                                completion_percentage = (completions / attempts) * 100

                            game_data_dict[f"{prefix}completionPercentage"] = (
                                completion_percentage
                            )

                        # Change the format of thirdDownEff and put into percentage
                        elif team.stats[i].category == "thirdDownEff":
                            try:
                                completions = int(team.stats[i].stat.split("-")[0])
                                attempts = int(team.stats[i].stat.split("-")[1])
                                if attempts == 0:
                                    thirdDownEff = None
                                else:
                                    thirdDownEff = (completions / attempts) * 100

                                game_data_dict[cat] = thirdDownEff
                            except:
                                print("Error getting thirdDownEff")

                        # Change the format of fourthDownEff and put into percentage
                        elif team.stats[i].category == "fourthDownEff":
                            try:
                                completions = int(team.stats[i].stat.split("-")[0])
                                attempts = int(team.stats[i].stat.split("-")[1])
                                if attempts == 0:
                                    fourthDownEff = None
                                else:
                                    fourthDownEff = (completions / attempts) * 100

                                game_data_dict[cat] = fourthDownEff
                            except:
                                print("Error getting fourthDownEff")

                        # Change the format of totalPenaltiesYards
                        elif team.stats[i].category == "totalPenaltiesYards":
                            try:
                                totalPenaltiesYards = int(
                                    team.stats[i].stat.split("-")[1]
                                )
                                game_data_dict[cat] = totalPenaltiesYards

                            except:
                                print("Error getting totalPenaltiesYards")

                        # Format the time
                        elif team.stats[i].category == "possessionTime":
                            minutes = int(team.stats[i].stat.split(":")[0]) * 60
                            total_time = int(team.stats[i].stat.split(":")[1]) + minutes

                            game_data_dict[cat] = total_time

                        else:
                            game_data_dict[cat] = team.stats[i].stat

                # Generate the list of columns and corresponding values
                columns = ", ".join(game_data_dict.keys())
                placeholders = ", ".join(["%s"] * len(game_data_dict))
                values = tuple(game_data_dict.values())

                # Generate the dynamic INSERT statement
                insert_statement = f"""
                    INSERT INTO team_game_stats ({columns})
                    VALUES ({placeholders})
                """

                # Execute the dynamic INSERT statement
                cursor.execute(insert_statement, values)

        connection.commit()
        # cursor.close()

        # print("Data inserted successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error inserting data into game_stats table:", e)


# Function to create the "team_talent" table
def create_team_talent_table(connection):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_talent (
                school VARCHAR,
                talent FLOAT,
                year INT
            )
        """
        )

        connection.commit()
        cursor.close()

        print("Table 'team_talent' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'team_talent' table in PostgreSQL:", e)


# Function to insert data into the "team_talent" table
def insert_team_talent_data(connection, data):
    try:
        cursor = connection.cursor()

        # Make sure not to run the same year twice and get duplicates
        tableName = "team_talent"
        cursor.execute(
            f"""SELECT 1 
                        FROM {tableName} 
                        WHERE school = '{data.school}' AND year = '{data.year}'
                        """
        )

        exists = cursor.fetchone()

        # Insert only if the combination does not exist
        if not exists:
            cursor.execute(
                """
                INSERT INTO team_talent (school, talent, year)
                VALUES (%s, %s, %s)
            """,
                (data.school, data.talent, data.year),
            )
            connection.commit()

        connection.commit()
        cursor.close()

    except psycopg2.Error as e:
        connection.rollback()

        print("Error inserting data into PostgreSQL:", e)


# Function to create the "games" table
def create_games_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id SERIAL PRIMARY KEY,
                season INT,
                week INT,
                season_type VARCHAR,
                start_date VARCHAR,
                start_time_tbd BOOLEAN,
                completed BOOLEAN,
                neutral_site BOOLEAN,
                conference_game BOOLEAN,
                attendance INT,
                venue_id INT,
                venue VARCHAR,
                home_id INT,
                home_team VARCHAR,
                home_conference VARCHAR,
                home_division VARCHAR,
                home_points INT,
                home_line_scores INT[],
                home_post_win_prob FLOAT,
                home_pregame_elo INT,
                home_postgame_elo INT,
                away_id INT,
                away_team VARCHAR,
                away_conference VARCHAR,
                away_division VARCHAR,
                away_points INT,
                away_line_scores INT[],
                away_post_win_prob FLOAT,
                away_pregame_elo INT,
                away_postgame_elo INT,
                excitement_index FLOAT,
                highlights VARCHAR,
                notes VARCHAR
            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'games' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'games' table in PostgreSQL:", e)


# Function to insert data into the "games" table
def insert_games_data(connection, data):
    try:
        cursor = connection.cursor()
        for game in data:
            cursor.execute(
                """
                INSERT INTO games (id, season, week, season_type, start_date, start_time_tbd, completed, neutral_site,
                conference_game, attendance, venue_id, venue, home_id, home_team, home_conference, home_division,
                home_points, home_line_scores, home_post_win_prob, home_pregame_elo, home_postgame_elo, away_id,
                away_team, away_conference, away_division, away_points, away_line_scores, away_post_win_prob,
                away_pregame_elo, away_postgame_elo, excitement_index, highlights, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    game.id,
                    game.season,
                    game.week,
                    game.season_type,
                    game.start_date,
                    game.start_time_tbd,
                    game.completed,
                    game.neutral_site,
                    game.conference_game,
                    game.attendance,
                    game.venue_id,
                    game.venue,
                    game.home_id,
                    game.home_team,
                    game.home_conference,
                    game.home_division,
                    game.home_points,
                    game.home_line_scores,
                    game.home_post_win_prob,
                    game.home_pregame_elo,
                    game.home_postgame_elo,
                    game.away_id,
                    game.away_team,
                    game.away_conference,
                    game.away_division,
                    game.away_points,
                    game.away_line_scores,
                    game.away_post_win_prob,
                    game.away_pregame_elo,
                    game.away_postgame_elo,
                    game.excitement_index,
                    game.highlights,
                    game.notes,
                ),
            )
        connection.commit()
        cursor.close()

        print("Data inserted successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error inserting data into PostgreSQL:", e)


# Function to create the "recruiting" table
def create_recruiting_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recruiting (
                points FLOAT,
                rank INT,
                team VARCHAR,
                year INT
            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'recruiting' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'recruiting' table in PostgreSQL:", e)


# Function to insert data into the "recruiting" table
def insert_recruiting_data(connection, data):
    try:
        cursor = connection.cursor()

        for team in data:

            if team.team == "Hawai'i":
                team.team = "Hawaii"

            # Make sure not to run the same year twice and get duplicates
            tableName = "recruiting"
            cursor.execute(
                f"""SELECT 1 
                    FROM {tableName} 
                    WHERE team = '{team.team}' AND year = {team.year}
                    """
            )

            exists = cursor.fetchone()

            # Insert only if the combination does not exist
            if not exists:
                cursor.execute(
                    """
                    INSERT INTO recruiting (points, rank, team, year)
                    VALUES (%s, %s, %s, %s)
                """,
                    (team.points, team.rank, team.team, team.year),
                )
                print("Data inserted successfully.")

        connection.commit()
        cursor.close()

    except psycopg2.Error as e:
        connection.rollback()

        print("Error inserting data into PostgreSQL:", e)



# Function to create the "teams" table
def create_teams_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS teams (
                id INT PRIMARY KEY,
                school VARCHAR(100),
                location VARCHAR(30),
                abbreviation VARCHAR(50),
                classification VARCHAR(50),
                color VARCHAR(50),
                conference VARCHAR(500),
                division VARCHAR(50),
                twitter VARCHAR(100),
                mascot VARCHAR(100),
                alt_name_1 VARCHAR(100),
                alt_name_2 VARCHAR(100),
                alt_name_3 VARCHAR(100),
                alt_color VARCHAR(50),
                logos TEXT
            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'teams' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'teams' table in PostgreSQL:", e)


# Function to insert data into the "teams" table
def insert_teams_data(connection, data):
    try:
        cursor = connection.cursor()
        for team in data:
            cursor.execute(
                """
                INSERT INTO teams (id, school, location, abbreviation, classification, color, conference, division, twitter,
                mascot, alt_name_1, alt_name_2, alt_name_3, alt_color, logos)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    team.id,
                    team.school,
                    team.location.state,
                    team.abbreviation,
                    team.classification,
                    team.color,
                    team.conference,
                    team.division,
                    team.twitter,
                    team.mascot,
                    team.alt_name_1,
                    team.alt_name_2,
                    team.alt_name_3,
                    team.alt_color,
                    team.logos,
                ),
            )
        connection.commit()
        cursor.close()

        print("Data inserted successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error inserting data into PostgreSQL:", e)


# Returns the stats for given columns
def get_column_stats(connection, columns):
    try:
        # Need to remove for select query
        removed = False
        if "target" in columns:
            columns.remove("target")
            removed = True

        # Construct the list of columns for SQL query
        columns_str = ", ".join(columns)
        cursor = connection.cursor()

        if removed:
            # Execute the SQL query with the formatted columns string
            cursor.execute(
                f"""
                SELECT {columns_str},
                    CASE
                        WHEN home_points > away_points THEN 1
                        ELSE 0
                    END AS target
                FROM (SELECT 
                    tgs.*,
                    home_team.talent AS home_talent,
                    away_team.talent AS away_talent
                FROM 
                    team_game_stats tgs
                JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) home_team ON (home_team.id = tgs.home_school_id) AND (home_team.year = tgs.year)
                JOIN (
                    SELECT 
                        t.id, 
                        tt.talent, 
                        tt.year
                    FROM 
                        team_talent tt
                    JOIN 
                        teams t ON t.school = tt.school
                ) away_team ON (away_team.id = tgs.away_school_id) AND (away_team.year = tgs.year));
                """
            )

        else:
            cursor.execute(
                f"""
                SELECT {columns_str}
                    FROM (SELECT 
                        tgs.*,
                        home_team.talent AS home_talent,
                        away_team.talent AS away_talent
                    FROM 
                        team_game_stats tgs
                    JOIN (
                        SELECT 
                            t.id, 
                            tt.talent, 
                            tt.year
                        FROM 
                            team_talent tt
                        JOIN 
                            teams t ON t.school = tt.school
                    ) home_team ON (home_team.id = tgs.home_school_id) AND (home_team.year = tgs.year)
                    JOIN (
                        SELECT 
                            t.id, 
                            tt.talent, 
                            tt.year
                        FROM 
                            team_talent tt
                        JOIN 
                            teams t ON t.school = tt.school
                    ) away_team ON (away_team.id = tgs.away_school_id) AND (away_team.year = tgs.year));
                """
            )

        # Fetch all rows
        rows = cursor.fetchall()
        cursor.close()

        # Add back removed column
        if removed:
            columns.append("target")

        return rows

    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return None


def get_all_game_stats(connection):

    # Create a cursor object using the connection
    cursor = connection.cursor()

    # cursor.execute(f'''SELECT home_id, away_id, target
    cursor.execute(
        f"""
                   -- Makes the home team always appear first
                    SELECT * ,
        CASE
            WHEN home_points > away_points THEN 1
            ELSE 0
        END AS target
    FROM (
        SELECT gs_home.school_id AS home_id,
            gs_home.points AS home_points,
            gs_home.rushingAttempts AS home_rush_attempts,
            gs_home.rushingYards AS home_rush_yards,
            gs_home.yardsPerPass AS home_yards_per_pass,
            gs_home.completionPercentage AS home_completion_percentage,
            gs_home.netPassingYards AS home_net_passing_yards,
            gs_home.totalYards AS home_total_yards,

            gs_home.fourthdowneff AS home_fourth_down_eff,
            gs_home.thirddowneff AS home_third_down_eff,
            gs_home.firstdowns AS home_first_downs,
            gs_home.rushingtds AS home_rushing_tds,
            gs_home.puntreturnyards AS home_punt_return_yards,
            gs_home.puntreturntds AS home_punt_return_tds,
            gs_home.puntreturns AS home_punt_returns,
            gs_home.passingtds AS home_passing_tds,
            gs_home.kickreturnyards AS home_kick_return_yards,
            gs_home.kickreturntds AS home_kick_return_tds,
            gs_home.kickreturns AS home_kick_returns,
            gs_home.kickingpoints AS home_kicking_points,
            gs_home.interceptionyards AS home_interception_yards,
            gs_home.interceptiontds AS home_interception_tds,
            gs_home.passesintercepted AS home_passes_intercepted,
            gs_home.fumblesrecovered AS home_fumbles_recovered,
            gs_home.totalfumbles AS home_total_fumbles,
            gs_home.tacklesforloss AS home_tackles_for_loss,
            gs_home.defensivetds AS home_defensive_tds,
            gs_home.tackles AS home_tackles,
            gs_home.sacks AS home_sacks,
            gs_home.qbhurries AS home_qb_hurries,
            gs_home.passesdeflected AS home_passes_deflected,
            gs_home.possessiontime AS home_possession_time,
            gs_home.interceptions AS home_interceptions,
            gs_home.fumbleslost AS home_fumbles_lost,
            gs_home.turnovers AS home_turnovers,
            gs_home.totalpenaltiesyards AS home_total_penalties_yards,
            gs_home.yardsperrushattempt AS home_yards_per_rush_attempt,

            gs_away.school_id AS away_id,
            gs_away.points AS away_points,
            gs_away.rushingAttempts AS away_rush_attempts,
            gs_away.rushingYards AS away_rush_yards,
            gs_away.yardsPerPass AS away_yards_per_pass,
            gs_away.completionPercentage AS away_completion_percentage,
            gs_away.netPassingYards AS away_net_passing_yards,
            gs_away.totalYards AS away_total_yards,

            gs_away.fourthdowneff AS away_fourth_down_eff,
            gs_away.thirddowneff AS away_third_down_eff,
            gs_away.firstdowns AS away_first_downs,
            gs_away.rushingtds AS away_rushing_tds,
            gs_away.puntreturnyards AS away_punt_return_yards,
            gs_away.puntreturntds AS away_punt_return_tds,
            gs_away.puntreturns AS away_punt_returns,
            gs_away.passingtds AS away_passing_tds,
            gs_away.kickreturnyards AS away_kick_return_yards,
            gs_away.kickreturntds AS away_kick_return_tds,
            gs_away.kickreturns AS away_kick_returns,
            gs_away.kickingpoints AS away_kicking_points,
            gs_away.interceptionyards AS away_interception_yards,
            gs_away.interceptiontds AS away_interception_tds,
            gs_away.passesintercepted AS away_passes_intercepted,
            gs_away.fumblesrecovered AS away_fumbles_recovered,
            gs_away.totalfumbles AS away_total_fumbles,
            gs_away.tacklesforloss AS away_tackles_for_loss,
            gs_away.defensivetds AS away_defensive_tds,
            gs_away.tackles AS away_tackles,
            gs_away.sacks AS away_sacks,
            gs_away.qbhurries AS away_qb_hurries,
            gs_away.passesdeflected AS away_passes_deflected,
            gs_away.possessiontime AS away_possession_time,
            gs_away.interceptions AS away_interceptions,
            gs_away.fumbleslost AS away_fumbles_lost,
            gs_away.turnovers AS away_turnovers,
            gs_away.totalpenaltiesyards AS away_total_penalties_yards,
            gs_away.yardsperrushattempt AS away_yards_per_rush_attempt

        FROM games g
        JOIN game_stats gs_home ON g.id = gs_home.game_id AND gs_home.school_id = g.home_id
        JOIN game_stats gs_away ON g.id = gs_away.game_id AND gs_away.school_id = g.away_id
                    );

                   """
    )

    """  
    SELECT *,
                        CASE
                            WHEN home_points > away_points THEN 1
                            ELSE 0
                        END AS target
                    FROM (
                        SELECT gs_home.school_id AS home_id,
                            gs_home.points AS home_points,
                            gs_home.rushingAttempts AS home_rush_attempts,
                            gs_home.rushingYards AS home_rush_yards,
                            gs_home.yardsPerPass AS home_yards_per_pass,
                            gs_home.completionPercentage AS home_completion_percentage,
                            gs_home.netPassingYards AS home_net_passing_yards,
                            gs_home.totalYards AS home_total_yards,

                            gs_away.school_id AS away_id,
                            gs_away.points AS away_points,
                            gs_away.rushingAttempts AS away_rush_attempts,
                            gs_away.rushingYards AS away_rush_yards,
                            gs_away.yardsPerPass AS away_yards_per_pass,
                            gs_away.completionPercentage AS away_completion_percentage,
                            gs_away.netPassingYards AS away_net_passing_yards,
                            gs_away.totalYards AS away_total_yards
                        FROM games g
                        JOIN game_stats gs_home ON g.id = gs_home.game_id AND gs_home.school_id = g.home_id
                        JOIN game_stats gs_away ON g.id = gs_away.game_id AND gs_away.school_id = g.away_id
                    ) AS subquery;

    """

    # Fetch all rows
    rows = cursor.fetchall()
    cursor.close()

    return rows


# Function to create the "betting_lines" table
def create_betting_lines_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS betting_lines (
                game_id INT PRIMARY KEY,
                home_moneyline FLOAT NULL,
                away_moneyline FLOAT NULL,
                spread FLOAT NULL,
                over_under FLOAT NULL,
                provider VARCHAR
            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'betting_lines' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'betting_lines' table in PostgreSQL:", e)


# Function to insert or update data in the "betting_lines" table
def insert_betting_lines_data(connection, data):
    try:
        cursor = connection.cursor()

        for line in data:
            for bets in line.lines:
                if bets.home_moneyline is not None:
                    cursor.execute(
                        """
                        INSERT INTO betting_lines (game_id, home_moneyline, away_moneyline, spread, over_under, provider)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (game_id) DO UPDATE SET
                            home_moneyline = EXCLUDED.home_moneyline,
                            away_moneyline = EXCLUDED.away_moneyline,
                            spread = EXCLUDED.spread,
                            over_under = EXCLUDED.over_under,
                            provider = EXCLUDED.provider
                        """,
                        (
                            line.id,
                            bets.home_moneyline,
                            bets.away_moneyline,
                            bets.spread,
                            bets.over_under,
                            bets.provider,
                        ),
                    )
                    break

        connection.commit()
        cursor.close()
    except psycopg2.Error as e:
        connection.rollback()
        print("Error inserting/updating data into PostgreSQL:", e)



# Function to create the "game_bets" table
def create_game_bets_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS game_bets (
                game_id INT,
                model_id INT,
                home_team VARCHAR(50) NULL,
                away_team VARCHAR(50) NULL,
                prediction INT NULL,
                probability FLOAT NULL,
                odds FLOAT NULL, 
                PRIMARY KEY (game_id, model_id)

            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'game_bets' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'game_bets' table in PostgreSQL:", e)

# Insert game predictions for a model
def insert_game_bets(connection, data, model_id):
    try:
        cursor = connection.cursor()

        # Go through every game prediction
        for game_id, game_info in data.items():
            # Check if the game_id already exists in the table
            cursor.execute(
                """
                SELECT 1 FROM game_bets WHERE game_id = %s AND model_id = %s
                """,
                (game_id, model_id)
            )
            exists = cursor.fetchone()

            if exists:
                # Update the existing record
                cursor.execute(
                    """
                    UPDATE game_bets
                    SET home_team = %s,
                        away_team = %s,
                        prediction = %s,
                        probability = %s,
                        odds = %s
                    WHERE game_id = %s AND model_id = %s
                    """,
                    (
                        game_info['home_team'],
                        game_info['away_team'],
                        game_info['random_forest_class_prediction'],
                        game_info['random_forest_class_proba'],
                        game_info['odds'],
                        game_id,
                        model_id
                    ),
                )
            else:
                # Insert a new record
                cursor.execute(
                    """
                    INSERT INTO game_bets (game_id, model_id, home_team, away_team, prediction, probability, odds)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        game_id,
                        model_id,
                        game_info['home_team'],
                        game_info['away_team'],
                        game_info['random_forest_class_prediction'],
                        game_info['random_forest_class_proba'],
                        game_info['odds']
                    ),
                )

        connection.commit()
        cursor.close()
    except psycopg2.Error as e:
        connection.rollback()
        print("Error inserting/updating data into PostgreSQL:", e)
