

import pandas as pd
from pprint import pprint
from sklearn.feature_selection import RFECV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, f1_score, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from joblib import dump



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



def target_provided(user_id, name, df, type, target, description=None):
    """Automatically optimize and train the best model with feature selection."""
    df = df.dropna()
    X = df.drop(columns=[target])
    y = df[target]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if type == "classification":
        print("Optimizing Classification Model...")
        
        # Initialize models to compare
        models = {
            "RandomForest": RandomForestClassifier(random_state=42),
            "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
            "SVM": SVC(random_state=42),
        }

        # Feature selection using RFE
        selector = RFECV(RandomForestClassifier(random_state=42), step=1, cv=5, scoring='accuracy')
        X_train_selected = selector.fit_transform(X_train, y_train)
        X_test_selected = selector.transform(X_test)

        # Compare models
        best_model = None
        best_score = 0
        best_model_name = None

        for model_name, model in models.items():
            model.fit(X_train_selected, y_train)
            y_pred = model.predict(X_test_selected)
            score = accuracy_score(y_test, y_pred)

            print(f"{model_name} Accuracy: {score}")
            if score > best_score:
                best_score = score
                best_model = model
                best_model_name = model_name

        # Evaluate best model
        y_pred = best_model.predict(X_test_selected)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f"Best Model: {best_model_name}")
        print(f"Classification Accuracy: {accuracy}")
        print(f"F1 Score: {f1}")

        # Save model
        file_path = f"models/{user_id}_class_{name}.joblib"
        dump(best_model, file_path)

        stats = {"accuracy": accuracy, "f1_score": f1}

    elif type == "regression":
        print("Optimizing Regression Model...")
        
        # Initialize models to compare
        models = {
            "RandomForestRegressor": RandomForestRegressor(random_state=42),
            "GradientBoosting": GradientBoostingRegressor(random_state=42),
        }

        # Feature selection using RFE
        selector = RFECV(GradientBoostingRegressor(random_state=42), step=1, cv=5, scoring='neg_mean_squared_error')
        X_train_selected = selector.fit_transform(X_train, y_train)
        X_test_selected = selector.transform(X_test)

        # Compare models
        best_model = None
        best_score = float('inf')
        best_model_name = None

        for model_name, model in models.items():
            model.fit(X_train_selected, y_train)
            y_pred = model.predict(X_test_selected)
            score = mean_squared_error(y_test, y_pred)

            print(f"{model_name} MSE: {score}")
            if score < best_score:
                best_score = score
                best_model = model
                best_model_name = model_name

        # Evaluate best model
        y_pred = best_model.predict(X_test_selected)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Best Model: {best_model_name}")
        print(f"Mean Squared Error: {mse}")
        print(f"R² Score: {r2}")

        # Save model
        file_path = f"models/{user_id}_reg_{name}.joblib"
        dump(best_model, file_path)

        stats = {"mse": mse, "r2_score": r2}

    else:
        raise ValueError("Invalid model type. Choose 'classification' or 'regression'.")

    return {
        "user_id": user_id,
        "name": name,
        "model_type": type,
        "file_path": file_path,
        "stats": stats,
    }


def model_columns():
    return [
        'away_completionpercentage', 'home_completionpercentage',
        'away_defensivetds', 'home_defensivetds',
        'away_firstdowns', 'home_firstdowns',
        'away_fourthdowneff', 'home_fourthdowneff',
        'away_fumbleslost', 'home_fumbleslost',
        'away_fumblesrecovered', 'home_fumblesrecovered',
        'away_interceptions', 'home_interceptions',
        'away_interceptiontds', 'home_interceptiontds',
        'away_interceptionyards', 'home_interceptionyards',
        'away_kickingpoints', 'home_kickingpoints',
        'away_kickreturns', 'home_kickreturns',
        'away_kickreturntds', 'home_kickreturntds',
        'away_kickreturnyards', 'home_kickreturnyards',
        'away_netpassingyards', 'home_netpassingyards',
        'away_passesdeflected', 'home_passesdeflected',
        'away_passesintercepted', 'home_passesintercepted',
        'away_passingtds', 'home_passingtds',
        # 'away_points', 'home_points',
        'away_possessiontime', 'home_possessiontime',
        'away_puntreturns', 'home_puntreturns',
        'away_puntreturntds', 'home_puntreturntds',
        'away_puntreturnyards', 'home_puntreturnyards',
        'away_qbhurries', 'home_qbhurries',
        'away_rushingattempts', 'home_rushingattempts',
        'away_rushingtds', 'home_rushingtds',
        'away_rushingyards', 'home_rushingyards',
        'away_sacks', 'home_sacks',
        'away_tackles', 'home_tackles',
        'away_tacklesforloss', 'home_tacklesforloss',
        'away_talent', 'home_talent',
        'away_thirddowneff', 'home_thirddowneff',
        'away_totalfumbles', 'home_totalfumbles',
        'away_totalpenaltiesyards', 'home_totalpenaltiesyards',
        'away_totalyards', 'home_totalyards',
        'away_turnovers', 'home_turnovers',
        'away_yardsperpass', 'home_yardsperpass',
        'away_yardsperrushattempt', 'home_yardsperrushattempt',
        'target'
    ]




from cfb.database.database_commands import create_connection
 
connection = create_connection()

model_loader(connection=connection, given_columns=model_columns(), user_id=34, name="Test1", type='classification', target='target', description=None)

connection.close()



'''
import cfbd
from cfbd.rest import ApiException
from pprint import pprint
from cfb.database.database_commands import (
    create_connection,
    cfbd_configuration,
    create_team_talent_table,
    insert_team_talent_data,
    create_game_stats_table,
    insert_game_stats_data,
    create_betting_lines_table,
    insert_betting_lines_data,
    create_games_table,
    insert_games_data
)
from global_vars import Global

# Run weekly before games
def get_betting_lines(connection, year, week, season_type):
    # Configure API key authorization
    configuration = cfbd_configuration()

    # create an instance of the API class
    api_instance = cfbd.BettingApi(cfbd.ApiClient(configuration))

    try:

        # Create betting table
        create_betting_lines_table(connection)

        # For each team get all data
        api_response = api_instance.get_lines(year=year, week=week, season_type=season_type)
        pprint(api_response)
        print(len(api_response))

        insert_betting_lines_data(connection, api_response)

    except ApiException as e:
        print("Exception when calling BettingApi->get_lines: %s\n" % e)


def get_games(connection, year, season_type):

    # Configure API key authorization
    configuration = cfbd_configuration()

    # Create an instance of the API class
    games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))

    try:
        # Create the "games" table
        create_games_table(connection)

        # Get games data from the API
        api_response = games_api.get_games(year=year, season_type=season_type)

        # Insert data into the "games" table
        insert_games_data(connection, api_response)

    except ApiException as e:
        print("Exception when calling teams_api->get_teams: %s\n" % e)


# Run weekly after games
def get_game_stats(connection, year, week, season_type):

    configuration = cfbd_configuration()

    # create an instance of the API class
    games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))

    try:
        # Create the "games" table
        create_game_stats_table(connection)

        api_response = games_api.get_team_game_stats(
            year=year, week=1, season_type=season_type
        )

        insert_game_stats_data(connection, api_response, year)


    except ApiException as e:
        print("Exception when calling GamesApi->get_team_game_stats: %s\n" % e)



connection = create_connection()

get_games(connection, Global.year, Global.season_type)
get_betting_lines(connection, Global.year, Global.week, Global.season_type)
get_game_stats(connection, Global.year, Global.week, Global.season_type)

connection.close()


'''