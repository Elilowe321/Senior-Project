from database.database_commands import create_connection, select_table
from database.user_model_commands import (
    create_user_model,
    insert_user_model,
    get_user_model,
    create_user_model_table,
)
from create_tables.create_game_stats_table import get_game_stats
from create_tables.create_games_table import get_games
from create_tables.create_teams_table import get_teams
from create_tables.create_team_talent_table import get_team_talent
from create_tables.create_recruiting_table import get_team_recruiting
from create_tables.create_betting_lines_table import get_betting_lines
from model_builders.predict_games import predict_games
from model_builders.model_loader import model_loader


import threading
from pprint import pprint


def yearly_script(year):

    # Create threads for each script
    get_teams_thread = threading.Thread(target=get_teams())
    get_team_recruiting_thread = threading.Thread(target=get_team_recruiting(year=year))
    get_team_talent_thread = threading.Thread(target=get_team_talent(year=year))
    get_games_thread = threading.Thread(target=get_games(year=year))

    # Start threads
    get_teams_thread.start()
    get_team_recruiting_thread.start()
    get_team_talent_thread.start()
    get_games_thread.start()

    print("Loading Data into Database")

    # Wait for both threads to finish
    get_teams_thread.join()
    get_team_recruiting_thread.join()
    get_team_talent_thread.join()
    get_games_thread.join()

    return "All scripts have finished executing."


def get_all_user_chosen_columns():
    user_chose_total_columns = [
        "home_points",
        "home_rush_attempts",
        "home_rush_yards",
        "home_yards_per_pass",
        "home_completion_percentage",
        "home_net_passing_yards",
        "home_total_yards",
        "home_fourth_down_eff",
        "home_third_down_eff",
        "home_first_downs",
        "home_rushing_tds",
        "home_punt_return_yards",
        "home_punt_return_tds",
        "home_punt_returns",
        "home_passing_tds",
        "home_kick_return_yards",
        "home_kick_return_tds",
        "home_kick_returns",
        "home_kicking_points",
        "home_interception_yards",
        "home_interception_tds",
        "home_passes_intercepted",
        "home_fumbles_recovered",
        "home_total_fumbles",
        "home_tackles_for_loss",
        "home_defensive_tds",
        "home_tackles",
        "home_sacks",
        "home_qb_hurries",
        "home_passes_deflected",
        "home_possession_time",
        "home_interceptions",
        "home_fumbles_lost",
        "home_turnovers",
        "home_total_penalties_yards",
        "home_yards_per_rush_attempt",
        "away_points",
        "away_rush_attempts",
        "away_rush_yards",
        "away_yards_per_pass",
        "away_completion_percentage",
        "away_net_passing_yards",
        "away_total_yards",
        "away_fourth_down_eff",
        "away_third_down_eff",
        "away_first_downs",
        "away_rushing_tds",
        "away_punt_return_yards",
        "away_punt_return_tds",
        "away_punt_returns",
        "away_passing_tds",
        "away_kick_return_yards",
        "away_kick_return_tds",
        "away_kick_returns",
        "away_kicking_points",
        "away_interception_yards",
        "away_interception_tds",
        "away_passes_intercepted",
        "away_fumbles_recovered",
        "away_total_fumbles",
        "away_tackles_for_loss",
        "away_defensive_tds",
        "away_tackles",
        "away_sacks",
        "away_qb_hurries",
        "away_passes_deflected",
        "away_possession_time",
        "away_interceptions",
        "away_fumbles_lost",
        "away_turnovers",
        "away_total_penalties_yards",
        "away_yards_per_rush_attempt",
        "target",
    ]

    return user_chose_total_columns


def get_all_predictor_columns():

    all_predictor_columns = [
        "home_rush_attempts",
        "home_rush_yards",
        "home_yards_per_pass",
        "home_completion_percentage",
        "home_net_passing_yards",
        "home_total_yards",
        "home_fourth_down_eff",
        "home_third_down_eff",
        "home_first_downs",
        "home_rushing_tds",
        "home_punt_return_yards",
        "home_punt_return_tds",
        "home_punt_returns",
        "home_passing_tds",
        "home_kick_return_yards",
        "home_kick_return_tds",
        "home_kick_returns",
        "home_kicking_points",
        "home_interception_yards",
        "home_interception_tds",
        "home_passes_intercepted",
        "home_fumbles_recovered",
        "home_total_fumbles",
        "home_tackles_for_loss",
        "home_defensive_tds",
        "home_tackles",
        "home_sacks",
        "home_qb_hurries",
        "home_passes_deflected",
        "home_possession_time",
        "home_interceptions",
        "home_fumbles_lost",
        "home_turnovers",
        "home_total_penalties_yards",
        "home_yards_per_rush_attempt",
        "away_rush_attempts",
        "away_rush_yards",
        "away_yards_per_pass",
        "away_completion_percentage",
        "away_net_passing_yards",
        "away_total_yards",
        "away_fourth_down_eff",
        "away_third_down_eff",
        "away_first_downs",
        "away_rushing_tds",
        "away_punt_return_yards",
        "away_punt_return_tds",
        "away_punt_returns",
        "away_passing_tds",
        "away_kick_return_yards",
        "away_kick_return_tds",
        "away_kick_returns",
        "away_kicking_points",
        "away_interception_yards",
        "away_interception_tds",
        "away_passes_intercepted",
        "away_fumbles_recovered",
        "away_total_fumbles",
        "away_tackles_for_loss",
        "away_defensive_tds",
        "away_tackles",
        "away_sacks",
        "away_qb_hurries",
        "away_passes_deflected",
        "away_possession_time",
        "away_interceptions",
        "away_fumbles_lost",
        "away_turnovers",
        "away_total_penalties_yards",
        "away_yards_per_rush_attempt",
    ]

    return all_predictor_columns


"""
Thoughts on how to go about.
1. For first game, will have to use stats from last year to make predictions
2. Each year: Run get_teams, get_games, get_team_talent, get_recruiting
3. Each week: Run get_game_stats, get_betting_lines
"""


def main(year, week):
    """
    # Testing database stuff
    print("Hello")
    conn = create_connection()
    rows = select_table(conn, "game_stats")
    print(rows[0])
    """

    # ========== Run each Year ==========
    # yearly_script(year=year)

    # ========== Run each Week Before Games Are Played ==========
    # get_betting_lines(year=year, week=week)

    # ========== Run each Week After Games Are Played ==========
    # get_game_stats(year=year, week=week)

    # ========== Predict Games Each Week ==========
    # predictions = predict_games(year=2024, week=1)
    # pprint(predictions)

    # ========== Create Models and get columns they use ==========
    connection = create_connection()

    user_id = 1
    name = "Keep8"
    model_columns = get_all_user_chosen_columns()
    description = "TEXT"
    # create_user_model_table(connection)
    # model = model_loader(get_all_user_chosen_columns(), user_id=user_id, name=name, description='Cool Description')
    # insert_user_model(connection, model)

    created_model_id = create_user_model(
        connection, model_columns, user_id, name, description
    )

    print(created_model_id)

    # cursor = connection.cursor()
    # cursor.execute(f"""
    #     SELECT id
    #             FROM user_models
    #             WHERE user_id = {user_id}
    #             AND name = '{name}'
    #  """)

    # rows = cursor.fetchone()
    # connection.commit()

    # print(rows[0])

    # # print(rows[0][0])

    # #TODO:: If model doesn't drop the null row >500, will need to update get_team_average to replace the null values
    # predicted_games = predict_games(2024, 1, get_all_predictor_columns(), chosen_columns=rows[0][2], class_file_path=rows[0][0], reg_file_path=rows[0][1])
    # pprint(predicted_games)

    # model = get_user_model(connection, 3)
    # pprint(model)

    # cursor.close()
    connection.close()

    # predicted_games = predict_games(2024, 1, get_all_predictor_columns(), models[0]['columns'])
    # pprint(predicted_games)

    # ========== After getting all data from previous week, do machine learning on the data ==========


if __name__ == "__main__":
    main(year=2024, week=1)
