from database.database_commands import (
    create_connection,
    get_team_average_stats,
    get_team_average_stats_new,
    game_lines,
    get_winner
)
from joblib import load
import numpy as np
import pandas as pd
from collections import OrderedDict
from global_vars import Global
from create_tables.create_betting_lines_table import get_betting_lines


def predict_games(
    connection,
    year,
    week,
    type,
    target,
    chosen_columns,
    class_file_path=None,
    reg_file_path=None,
):
    
    # Needed ffor getting upcoming betting lines
    # get_betting_lines(connection, year, week)

    # Get all games 
    cursor = connection.cursor()
    cursor.execute(
        f"""
            SELECT id as game_id,
                home_id,
                home_team,
                away_id,
                away_team
            FROM games
            WHERE season = {year}
            AND week = {week};
        """
    )

    rows = cursor.fetchall()
    connection.commit()
    cursor.close()

    all_predictions = {}

    # If week 1, get stats from last year since there are none from this year
    if(week == 1):
        year = year-1

    if type == "classification":
        print("Making Classification Predictions")
        random_forest_class_model = load(filename=class_file_path)

        # Go through all games 
        for row in rows:
            game_id, home_id, home_team, away_id, away_team = row

            # Get average stats for the teams in each game
            home_average_stats = get_team_average_stats_new(
                connection, chosen_columns, home_id, year, "home_"
            )
            away_average_stats = get_team_average_stats_new(
                connection, chosen_columns, away_id, year, "away_"
            )

            # If its the first week, get last years stats on everything besides team talent
            if 'home_talent' in chosen_columns and week == 1:
                home_average_stats.pop('home_talent', None)
                away_average_stats.pop('away_talent', None)

                # get talent for this year
                cursor = connection.cursor()
                cursor.execute(
                    f"""
                        SELECT tt.talent
                        FROM team_talent tt
                        JOIN teams t ON t.school = tt.school
                        WHERE t.id = {home_id}
                        AND year = {year+1};
                    """
                )
                home_talent = cursor.fetchone()
                cursor.close()

                cursor = connection.cursor()
                cursor.execute(
                    f"""
                        SELECT tt.talent
                        FROM team_talent tt
                        JOIN teams t ON t.school = tt.school
                        WHERE t.id = {away_id}
                        AND year = {year+1};
                    """
                )
                away_talent = cursor.fetchone()
                cursor.close()

                # Extract the single value from the tuple
                home_talent = home_talent[0] if home_talent else None
                away_talent = away_talent[0] if away_talent else None

                home_average_stats['home_talent'] = home_talent
                away_average_stats['away_talent'] = away_talent


            merged_stats = home_average_stats.copy()
            merged_stats.update(away_average_stats)

            # Create a DataFrame from merged_stats and sort
            df = pd.DataFrame([merged_stats.values()], columns=merged_stats.keys())
            df = df.sort_index(axis=1)

            # print(home_team, home_id, merged_stats)

            random_forest_class_prediction = random_forest_class_model.predict(df)
            random_forest_class_proba = random_forest_class_model.predict_proba(df)

            if(random_forest_class_prediction[0] == 1):
                proba = random_forest_class_proba[0][1] * 100
            else:
                proba = random_forest_class_proba[0][0] * 100

            
            betting_lines = game_lines(connection, game_id)

            odds = None  # Default value if betting_lines is None or empty
            if betting_lines:
                if(random_forest_class_prediction == 1):
                    odds = betting_lines[0][1]
                else:
                    odds = betting_lines[0][2]

            if(odds is None):
                odds = 0


            all_predictions[game_id] = OrderedDict(
                {
                    "game_id": game_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "random_forest_class_prediction": int(
                        random_forest_class_prediction
                    ),
                    "random_forest_class_proba": int(proba),
                    "odds": odds,
                }
            )

    elif type == "regression":

        print("Making Regression Predictions")
        random_forest_model_home = load(filename=reg_file_path)

        away_filename = reg_file_path.replace("_home_", "_away_")
        random_forest_model_away = load(filename=away_filename)


        for row in rows:
            game_id, home_id, home_team, away_id, away_team = row

            home_average_stats = get_team_average_stats_new(
                connection, chosen_columns, home_id, year, "home_"
            )
            away_average_stats = get_team_average_stats_new(
                connection, chosen_columns, away_id, year, "away_"
            )

            merged_stats = home_average_stats.copy()
            merged_stats.update(away_average_stats)

            # Create a DataFrame from merged_stats, drop targets, and sort
            df = pd.DataFrame([merged_stats.values()], columns=merged_stats.keys())
            drop_targets = [f"home_{target}", f"away_{target}"]
            df = df.drop(columns=drop_targets)
            df = df.sort_index(axis=1)

            random_forest_home = random_forest_model_home.predict(df)
            random_forest_away = random_forest_model_away.predict(df)

            all_predictions[game_id] = OrderedDict(
                {
                    "game_id": game_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "random_forest_home": float(np.round(random_forest_home, 2)),
                    "random_forest_away": float(np.round(random_forest_away, 2)),
                }
            )

    return all_predictions



    '''
    # This is working for Random forest
    print("Making Regression Predictions")
    random_forest_model = load(filename=reg_file_path)

    for row in rows:
        game_id, home_id, home_team, away_id, away_team = row

        home_average_stats = get_team_average_stats_new(
            connection, chosen_columns, home_id, 2023, "home_"
        )
        away_average_stats = get_team_average_stats_new(
            connection, chosen_columns, away_id, 2023, "away_"
        )

        merged_stats = home_average_stats.copy()
        merged_stats.update(away_average_stats)

        # Create a DataFrame from merged_stats, drop targets, and sort
        df = pd.DataFrame([merged_stats.values()], columns=merged_stats.keys())
        drop_targets = [f"home_{target}", f"away_{target}"]
        df = df.drop(columns=drop_targets)
        df = df.sort_index(axis=1)

        random_forest = random_forest_model.predict(df)
        random_forest_home = random_forest[0][0]
        random_forest_away = random_forest[0][1]

        all_predictions[game_id] = OrderedDict(
            {
                "game_id": game_id,
                "home_team": home_team,
                "away_team": away_team,
                "random_forest_home": float(round(random_forest_home, 2)),
                "random_forest_away": float(round(random_forest_away, 2)),
            }
        )

return all_predictions
'''
