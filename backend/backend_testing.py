
import pandas as pd
from pprint import pprint

from sklearn.metrics import (
    accuracy_score,
    mean_squared_error,
)

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingRegressor,
)
from sklearn.model_selection import train_test_split
from joblib import dump


def model_loader(
    connection, given_columns, user_id, name, type, target, description=None
):

    # Get all game stats through sql database command
    rows = get_column_stats(connection, given_columns)

    # Convert to DataFrame and sort
    df = pd.DataFrame(rows, columns=given_columns)
    df = df.sort_index(axis=1)


    print(df.head)

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
    

def model_columns():
    return [
        'away_completionpercentage', 'away_defensivetds', 'away_firstdowns', 'away_fourthdowneff', 
        'away_fumbleslost', 'away_fumblesrecovered', 'away_interceptions', 'away_interceptiontds', 
        'away_interceptionyards', 'away_kickingpoints', 'away_kickreturns', 'away_kickreturntds', 
        'away_kickreturnyards', 'away_netpassingyards', 'away_passesdeflected', 'away_passesintercepted', 
        'away_passingtds', 'away_points', 'away_possessiontime', 'away_puntreturns', 'away_puntreturntds', 
        'away_puntreturnyards', 'away_qbhurries', 'away_rushingattempts', 'away_rushingtds', 'away_rushingyards', 
        'away_sacks', 'away_tackles', 'away_tacklesforloss', 'away_talent', 'away_thirddowneff', 
        'away_totalfumbles', 'away_totalpenaltiesyards', 'away_totalyards', 'away_turnovers', 'away_yardsperpass', 
        'away_yardsperrushattempt', 'home_completionpercentage', 'home_defensivetds', 'home_firstdowns', 
        'home_fourthdowneff', 'home_fumbleslost', 'home_fumblesrecovered', 'home_interceptions', 
        'home_interceptiontds', 'home_interceptionyards', 'home_kickingpoints', 'home_kickreturns', 
        'home_kickreturntds', 'home_kickreturnyards', 'home_netpassingyards', 'home_passesdeflected', 
        'home_passesintercepted', 'home_passingtds', 'home_points', 'home_possessiontime', 'home_puntreturns', 
        'home_puntreturntds', 'home_puntreturnyards', 'home_qbhurries', 'home_rushingattempts', 'home_rushingtds', 
        'home_rushingyards', 'home_sacks', 'home_tackles', 'home_tacklesforloss', 'home_talent', 
        'home_thirddowneff', 'home_totalfumbles', 'home_totalpenaltiesyards', 'home_totalyards', 
        'home_turnovers', 'home_yardsperpass', 'home_yardsperrushattempt', 'target'
    ]



from database.database_commands import create_connection
 

connection = create_connection()

model_loader(connection=connection, given_columns=model_columns(), user_id=34, name="Test1", type='classification', target='target', description=None)

connection.close()