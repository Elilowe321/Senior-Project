import pandas as pd
import numpy as np
from joblib import load, dump
from collections import OrderedDict
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    mean_squared_error,
)
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingRegressor,
)

from cfb.database.database_commands import (
    create_connection,
    get_team_average_stats,
    get_team_average_stats_new,
    game_lines,
    get_column_stats,
    get_winner
)


def model_loader(
    connection, given_columns, user_id, name, type, target, description=None
):

    # Get all game stats through sql database command
    rows = get_column_stats(connection, given_columns)

    # Convert to DataFrame and sort
    df = pd.DataFrame(rows, columns=given_columns)
    df = df.sort_index(axis=1)

    # Call different models to compare which is the best
    model = target_provided(
        user_id=user_id,
        name=name,
        df=df,
        type=type,
        target=target,
        description=description,
    )

    return model



def target_provided(user_id, name, df, type, target, description=None):

    if type == "classification":
        print("Creating Classification Model")

        # Drop na columns if > 200 and other rows
        # df = df.dropna(thresh=len(df) - 500, axis=1)
        df = df.dropna()

        x_model_name = df.drop([target], axis=1)  # TODO:: Fix home and away points
        y_model_name = df[target]  # Target variable: win

        # Split data into training and testing sets for classification and regression
        X_train_class, X_test_class, y_train_class, y_test_class = train_test_split(
            x_model_name, y_model_name, test_size=0.2, random_state=42
        )

        # Create models
        classification_model = RandomForestClassifier(n_estimators=100)

        # Fit models
        classification_model.fit(X_train_class, y_train_class)

        # Model Evaluation
        y_pred_class = classification_model.predict(X_test_class)

        # Check Accuracy
        classification_accuracy = accuracy_score(y_test_class, y_pred_class)
        print("Classification Accuracy: ", classification_accuracy)

        # Save models
        class_file_name = f"models/{user_id}_class_{name}.joblib"
        dump(classification_model, filename=class_file_name)

        mse_home = None
        mse_away = None
        reg_file_name = None

        # Return Model
        # df = df.drop([target], axis=1)
        stats = {
            "classification_accuracy": round(classification_accuracy, 2),
            "mse_home": mse_home,
            "mse_away": mse_away,
        }

        model = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "type": type,
            "target": target,
            "file_location_class": class_file_name,
            "file_location_reg": reg_file_name,
            "columns": df.columns.tolist(),
            "stats": stats,
        }

        return model

    if type == "regression":
        target_home = f"home_{target}"
        target_away = f"away_{target}"

        print("Creating Regression Model")

        # Gradient Boost
        df = df.dropna()

        X_regression = df.drop([target_home, target_away], axis=1)
        y_regression = df[
            [target_home, target_away]
        ] 


        X_train, X_test, y_train, y_test = train_test_split(
            X_regression, y_regression, test_size=0.2, random_state=42
        )

        regression_model_home = GradientBoostingRegressor(n_estimators=100)
        regression_model_away = GradientBoostingRegressor(n_estimators=100)

        regression_model_home.fit(X_train, y_train[target_home])
        regression_model_away.fit(X_train, y_train[target_away])

        y_pred_home = regression_model_home.predict(X_test)
        y_pred_away = regression_model_away.predict(X_test)


        mse_home = mean_squared_error(y_test[target_home], y_pred_home)
        mse_away = mean_squared_error(y_test[target_away], y_pred_away)

        print("mse_home:", mse_home)

        reg_file_name_home = f"models/{user_id}_gradient_reg_home_{name}.joblib"
        reg_file_name_away = f"models/{user_id}_gradient_reg_away_{name}.joblib"

        dump(regression_model_home, filename=reg_file_name_home)
        dump(regression_model_away, filename=reg_file_name_away)

        classification_accuracy = None
        class_file_name = None

        stats = {
            "classification_accuracy": classification_accuracy,
            "mse_home": mse_home,
            "mse_away": mse_away,
        }

        model = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "type": type,
            "target": target,
            "file_location_class": class_file_name,
            "file_location_reg": reg_file_name_home,
            "columns": df.columns.tolist(),
            "stats": stats,
        }

        return model

        '''
        # THIS IS THE WORKING ONE FOR RANDOM FOREST
        
        # Drop na columns if > 200 and other rows
        # df = df.dropna(thresh=len(df) - 500, axis=1)
        df = df.dropna()

        x_model_name = df.drop([target_home, target_away], axis=1)
        y_model_name = df[[target_home, target_away]]

        X_train, X_test, y_train, y_test = train_test_split(
            x_model_name, y_model_name, test_size=0.2, random_state=42
        )

        # Create models
        regression_model = RandomForestRegressor(n_estimators=100)

        # Fit models
        regression_model.fit(X_train, y_train)

        # Model Evaluation
        y_pred = regression_model.predict(X_test)

        y_pred_home = y_pred[:, 0]
        y_pred_away = y_pred[:, 1]

        # Check Accuracy
        mse_home = mean_squared_error(y_test[target_home], y_pred_home)
        mse_away = mean_squared_error(y_test[target_away], y_pred_away)

        print("MSE Home: ", mse_home)
        print("MSE Away: ", mse_away)

        # Save models
        reg_file_name = f"models/{user_id}_reg_{name}.joblib"

        dump(regression_model, filename=reg_file_name)

        classification_accuracy = None
        class_file_name = None

        # Return Model
        # df = df.drop([target_home, target_away], axis=1)
        stats = {
            "classification_accuracy": classification_accuracy,
            "mse_home": mse_home,
            "mse_away": mse_away,
        }

        model = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "type": type,
            "target": target,
            "file_location_class": class_file_name,
            "file_location_reg": reg_file_name,
            "columns": df.columns.tolist(),
            "stats": stats,
        }

        return model
        '''

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
        week = 15

    if type == "classification":
        print("Making Classification Predictions")
        random_forest_class_model = load(filename=class_file_path)

        # Go through all games 
        for row in rows:
            game_id, home_id, home_team, away_id, away_team = row

            # Get average stats for the teams in each game
            # home_average_stats = get_team_average_stats_new(
            #     connection, chosen_columns, home_id, year, "home_"
            # )
            # away_average_stats = get_team_average_stats_new(
            #     connection, chosen_columns, away_id, year, "away_"
            # )


            home_average_stats = get_team_average_stats(
                connection, chosen_columns, home_id, year, week, "home_"
            )
            away_average_stats = get_team_average_stats(
                connection, chosen_columns, away_id, year, week, "away_"
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
