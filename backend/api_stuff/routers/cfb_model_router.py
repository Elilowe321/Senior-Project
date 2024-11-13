import time
from database.database_commands import create_connection
from ..pydantic_models import cfb_models
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from fastapi.security import OAuth2PasswordBearer
from ..routers.auth_router import get_current_user

from database.user_model_commands import (
    get_user_models,
    get_specific_user_model,
    create_user_model,
    delete_user_model,
)
import threading



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Database connection
def get_db():
    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()


# Gets the columns of database for frontend
@router.get("/models/columns")
def get_columns(connection=Depends(get_db)):

    try:
        table_name = "team_game_stats"
        cursor = connection.cursor()

        cursor.execute(
            f"""
                SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}';
            """
        )

        '''
        SELECT 
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
        ) away_team ON (away_team.id = tgs.away_school_id) AND (away_team.year = tgs.year);
        '''

        columns = cursor.fetchall()
        cursor.close()

        # Remove unneeded columns
        columns_to_remove = [
            "game_id",
            "year",
            "home_school_id",
            "away_school_id",
            "home_home_away",
            "away_home_away",
        ]

        # Remove the home_ and away_ so it displayed correctly
        filtered_columns = []
        for col in columns:
            if col[0] not in columns_to_remove and col[0].startswith("home_"):
                filtered_columns.append(col[0][5:])

        filtered_columns.append('talent')
        # filtered_columns.append('recruiting')
        return filtered_columns

    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return None


# Get all models that a user has
@router.get("/models/{user_id}")
def get_user_models_handler(
    user_id: int, connection=Depends(get_db)
) -> List[cfb_models.ReturnModel]:
    
    models = get_user_models(connection, user_id)
    if models:
        return [cfb_models.ReturnModel(**model) for model in models]
    else:
        raise HTTPException(status_code=404, detail="Error finding model")


# Define route to get user model
@router.get("/{user_id}/models/{model_id}")
def get_user_specific_model_handler(
    user_id: int, model_id: int, connection=Depends(get_db)
) -> cfb_models.ReturnModel:
        
    model = get_specific_user_model(connection, model_id)
    if model:
        return cfb_models.ReturnModel(**model)
    else:
        raise HTTPException(status_code=404, detail="Model not found")
    

# Define route to create user model
@router.post("/models/{user_id}")
def create_user_model_handler(
    user_model: cfb_models.CreateModel,
    # current_user: dict = Depends(get_current_user),
    connection=Depends(get_db),
) -> cfb_models.ReturnModel:
    
    cursor = connection.cursor()
    cursor.execute(
        f"""
        SELECT 1 
        FROM user_models 
        WHERE user_id = {user_model.user_id} 
        AND name = '{user_model.name}'
        """
    )

    existing_model = cursor.fetchone()

    if existing_model:
        raise HTTPException(status_code=404, detail="Name already in use")

    try:
        # Call the function to create a user model
        created_model = create_user_model(
            connection,
            user_model.user_id,
            cfb_models.chosen_columns(
                selected_columns=user_model.model_columns,
                target=user_model.target,
            ),
            user_model.name,
            user_model.type,
            user_model.target,
            user_model.description,
        )

        # Return the model
        return cfb_models.ReturnModel.model_validate(created_model)

    except:
        return "Failed creating user model"



# Define route to delete user model
@router.delete("/models/{user_id}/{model_id}")
def delete_user_model_handler(
    model_id: int,
    current_user: dict = Depends(get_current_user),
    connection=Depends(get_db),
):

    try:
        return delete_user_model(connection, model_id)

    except:
        # Close the database connection
        raise HTTPException(status_code=500, detail="Failed deleting model")


from create_tables.create_betting_lines_table import get_betting_lines
from database.user_model_commands import create_test_model_prev_year_table
from model_builders.predict_games import predict_games
from datetime import datetime  # Import datetime if you're using TIMESTAMP

from multiprocessing import Pool
from datetime import datetime


@router.get("/test-accuracy")
def test_accuracy(user_id: int, model_id: int):
    start_time = datetime.now()

    with Pool(processes=6) as pool:
        # args_list = [(user_id, model_id, year, safe_bet) for year in [2022, 2023] for safe_bet in [0, 1, 2]]
        args_list = [(user_id, model_id, year, safe_bet) for year in [2022, 2023] for safe_bet in [0]]

        results = pool.map(run_model_process, args_list)

    end_time = datetime.now()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    return results

def run_model_process(args):
    user_id, model_id, year, safe_bet = args
    result = run_model_on_prev_year(user_id, model_id, year, safe_bet)
    return result


def run_model_on_prev_year(user_id: int, model_id: int, year: int, safe_bet: int):

    connection = create_connection()
    
    start_time = datetime.now()

    create_test_model_prev_year_table(connection)

    model = get_user_specific_model_handler(user_id, model_id, connection)

    base_stake = 1
    weekly_stats = []
    data_to_insert = []

    for week in range(1, 17):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM test_model_prev_year
            WHERE user_id = %s AND model_id = %s AND year = %s AND week = %s AND safe_bet = %s
        """, (user_id, model_id, year, week, safe_bet))
        count = cursor.fetchone()[0]
        cursor.close()

        if count > 0:
            print(f"Skipping year {year}, week {week}, safe_bet {safe_bet} as it already exists in the database")
            continue

        week_correct_predictions = 0
        week_total_predictions = 0
        week_money_in = 0
        week_profit = 0
        week_total_out = 0

        week_correct_predictions_neg_odds = 0
        week_total_predictions_neg_odds = 0
        week_money_in_neg_odds = 0
        week_profit_neg_odds = 0
        week_total_out_neg_odds = 0

        week_correct_predictions_pos_odds = 0
        week_total_predictions_pos_odds = 0
        week_money_in_pos_odds = 0
        week_profit_pos_odds = 0
        week_total_out_pos_odds = 0

        class_filepath = model.file_location_class if model.type == "classification" else ""

        if class_filepath:
            predicted_games_class = predict_games(
                connection,
                year=year,
                week=week,
                type=model.type,
                target=model.target,
                chosen_columns=model.columns,
                class_file_path=class_filepath,
            )

            if predicted_games_class:
                for game_id, game_prediction in predicted_games_class.items():
                    cursor = connection.cursor()
                    cursor.execute(f"""
                        SELECT
                            CASE
                                WHEN home_points > away_points THEN 1
                                ELSE 0
                            END AS target
                        FROM team_game_stats
                        WHERE game_id = {game_id}
                    """)

                    rows = cursor.fetchone()
                    cursor.close()

                    if rows:
                        actual_result = rows[0]
                        odds = game_prediction["odds"]

                        if odds is not None and odds != 0:
                            week_total_predictions += 1

                            if safe_bet == 1:
                                stake = base_stake * 2 if odds < 0 else base_stake * 1
                            elif safe_bet == 2:
                                stake = base_stake * 1 if odds < 0 else base_stake * 2
                            else:
                                stake = base_stake

                            week_money_in += stake

                            if (actual_result == 1 and game_prediction['random_forest_class_prediction'] == 1) or (actual_result == 0 and game_prediction['random_forest_class_prediction'] == 0):
                                week_correct_predictions += 1
                                if odds < 0:
                                    week_profit += 100 / abs(odds) * stake
                                else:
                                    week_profit += odds / 100 * stake
                            else:
                                week_profit -= stake

                            if odds < 0:
                                week_total_predictions_neg_odds += 1
                                week_money_in_neg_odds += stake
                                if (actual_result == 1 and game_prediction['random_forest_class_prediction'] == 1) or (actual_result == 0 and game_prediction['random_forest_class_prediction'] == 0):
                                    week_correct_predictions_neg_odds += 1
                                    week_profit_neg_odds += 100 / abs(odds) * stake
                                else:
                                    week_profit_neg_odds -= stake

                            if odds > 0:
                                week_total_predictions_pos_odds += 1
                                week_money_in_pos_odds += stake
                                if (actual_result == 1 and game_prediction['random_forest_class_prediction'] == 1) or (actual_result == 0 and game_prediction['random_forest_class_prediction'] == 0):
                                    week_correct_predictions_pos_odds += 1
                                    week_profit_pos_odds += odds / 100 * stake
                                else:
                                    week_profit_pos_odds -= stake

                week_total_out = week_money_in + week_profit
                week_total_out_neg_odds = week_money_in_neg_odds + week_profit_neg_odds if week_total_predictions_neg_odds != 0 else 0
                week_total_out_pos_odds = week_money_in_pos_odds + week_profit_pos_odds if week_total_predictions_pos_odds != 0 else 0

                weekly_stats.append({
                    "week": week,
                    "total_predictions": week_total_predictions,
                    "correct_predictions": week_correct_predictions,
                    "money_in": week_money_in,
                    "profit": week_profit,
                    "total_out": week_total_out,
                    "negative_odds": {
                        "total_predictions": week_total_predictions_neg_odds,
                        "correct_predictions": week_correct_predictions_neg_odds,
                        "money_in": week_money_in_neg_odds,
                        "profit": week_profit_neg_odds,
                        "total_out": week_total_out_neg_odds,
                    },
                    "positive_odds": {
                        "total_predictions": week_total_predictions_pos_odds,
                        "correct_predictions": week_correct_predictions_pos_odds,
                        "money_in": week_money_in_pos_odds,
                        "profit": week_profit_pos_odds,
                        "total_out": week_total_out_pos_odds,
                    }
                })

                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO test_model_prev_year (
                        user_id, model_id, year, week, total_predictions, correct_predictions, money_in, profit, total_out,
                        total_predictions_neg_odds, correct_predictions_neg_odds, money_in_neg_odds, profit_neg_odds, total_out_neg_odds,
                        total_predictions_pos_odds, correct_predictions_pos_odds, money_in_pos_odds, profit_pos_odds, total_out_pos_odds,
                        safe_bet, time
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    model.user_id, model.model_id, year, week, week_total_predictions, week_correct_predictions, week_money_in, week_profit, week_total_out,
                    week_total_predictions_neg_odds, week_correct_predictions_neg_odds, week_money_in_neg_odds, week_profit_neg_odds, week_total_out_neg_odds,
                    week_total_predictions_pos_odds, week_correct_predictions_pos_odds, week_money_in_pos_odds, week_profit_pos_odds, week_total_out_pos_odds,
                    safe_bet, datetime.now()

                ))
                connection.commit()
                cursor.close()


    # Read from inserted stuff and return it
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT *
        FROM test_model_prev_year
        WHERE user_id = {user_id}
        AND model_id = {model_id}
        AND year = {year}
        AND safe_bet = {safe_bet}
    """)
    rows = cursor.fetchall()
    cursor.close()

    if rows:
        total_predictions = sum(row[5] for row in rows)
        correct_predictions = sum(row[6] for row in rows)
        accuracy = correct_predictions / total_predictions if total_predictions else 0
        money_in = sum(row[7] for row in rows)
        profit = sum(row[8] for row in rows)
        total_out = sum(row[9] for row in rows)
        
        total_predictions_neg_odds = sum(row[10] for row in rows)
        correct_predictions_neg_odds = sum(row[11] for row in rows)
        accuracy_neg_odds = correct_predictions_neg_odds / total_predictions_neg_odds if total_predictions_neg_odds else 0
        money_in_neg_odds = sum(row[12] for row in rows)
        profit_neg_odds = sum(row[13] for row in rows)
        total_out_neg_odds = sum(row[14] for row in rows)
        
        total_predictions_pos_odds = sum(row[15] for row in rows)
        correct_predictions_pos_odds = sum(row[16] for row in rows)
        accuracy_pos_odds = correct_predictions_pos_odds / total_predictions_pos_odds if total_predictions_pos_odds else 0
        money_in_pos_odds = sum(row[17] for row in rows)
        profit_pos_odds = sum(row[18] for row in rows)
        total_out_pos_odds = sum(row[19] for row in rows)
        
        weekly_stats = [{
            "week": row[4],
            "total_predictions": row[5],
            "correct_predictions": row[6],
            "money_in": row[7],
            "profit": row[8],
            "total_out": row[9],
            "total_predictions_neg_odds": row[10],
            "correct_predictions_neg_odds": row[11],
            "money_in_neg_odds": row[12],
            "profit_neg_odds": row[13],
            "total_out_neg_odds": row[14],
            "total_predictions_pos_odds": row[15],
            "correct_predictions_pos_odds": row[16],
            "money_in_pos_odds": row[17],
            "profit_pos_odds": row[18],
            "total_out_pos_odds": row[19],
        } for row in rows]


        end_time = datetime.now()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        connection.close()

        return {
            "year": year,
            "safe_bet": safe_bet,
            "total_predictions": total_predictions,
            "correct_predictions": correct_predictions,
            "accuracy": accuracy,
            "money_in": money_in,
            "profit": profit,
            "total_out": total_out,
            "negative_odds": {
                "total_predictions": total_predictions_neg_odds,
                "correct_predictions": correct_predictions_neg_odds,
                "accuracy": accuracy_neg_odds,
                "money_in": money_in_neg_odds,
                "profit": profit_neg_odds,
                "total_out": total_out_neg_odds,
            },
            "positive_odds": {
                "total_predictions": total_predictions_pos_odds,
                "correct_predictions": correct_predictions_pos_odds,
                "accuracy": accuracy_pos_odds,
                "money_in": money_in_pos_odds,
                "profit": profit_pos_odds,
                "total_out": total_out_pos_odds,
            },
            "weekly_stats": weekly_stats
        }

                
@router.get("/display-past-results")
def display_past_results(user_id: int, model_id: int, connection=Depends(get_db)):
    
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT *
            FROM test_model_prev_year
            WHERE user_id = {user_id}
            AND model_id = {model_id}
            AND year = 2023
            AND safe_bet = 0
    """)

    rows = cursor.fetchall()
    cursor.close()

    if rows:
        total_predictions = sum(row[5] for row in rows)
        correct_predictions = sum(row[6] for row in rows)
        accuracy = correct_predictions / total_predictions if total_predictions else 0
        money_in = sum(row[7] for row in rows)
        profit = sum(row[8] for row in rows)
        total_out = sum(row[9] for row in rows)
        
        total_predictions_neg_odds = sum(row[10] for row in rows)
        correct_predictions_neg_odds = sum(row[11] for row in rows)
        accuracy_neg_odds = correct_predictions_neg_odds / total_predictions_neg_odds if total_predictions_neg_odds else 0
        money_in_neg_odds = sum(row[12] for row in rows)
        profit_neg_odds = sum(row[13] for row in rows)
        total_out_neg_odds = sum(row[14] for row in rows)
        
        total_predictions_pos_odds = sum(row[15] for row in rows)
        correct_predictions_pos_odds = sum(row[16] for row in rows)
        accuracy_pos_odds = correct_predictions_pos_odds / total_predictions_pos_odds if total_predictions_pos_odds else 0
        money_in_pos_odds = sum(row[17] for row in rows)
        profit_pos_odds = sum(row[18] for row in rows)
        total_out_pos_odds = sum(row[19] for row in rows)
        
        weekly_stats = [{
            "week": row[4],
            "total_predictions": row[5],
            "correct_predictions": row[6],
            "money_in": row[7],
            "profit": row[8],
            "total_out": row[9],
            "total_predictions_neg_odds": row[10],
            "correct_predictions_neg_odds": row[11],
            "money_in_neg_odds": row[12],
            "profit_neg_odds": row[13],
            "total_out_neg_odds": row[14],
            "total_predictions_pos_odds": row[15],
            "correct_predictions_pos_odds": row[16],
            "money_in_pos_odds": row[17],
            "profit_pos_odds": row[18],
            "total_out_pos_odds": row[19],
        } for row in rows]
        
        return {
            "total_predictions": total_predictions,
            "correct_predictions": correct_predictions,
            "accuracy": accuracy,
            "money_in": money_in,
            "profit": profit,
            "total_out": total_out,
            "negative_odds": {
                "total_predictions": total_predictions_neg_odds,
                "correct_predictions": correct_predictions_neg_odds,
                "accuracy": accuracy_neg_odds,
                "money_in": money_in_neg_odds,
                "profit": profit_neg_odds,
                "total_out": total_out_neg_odds,
            },
            "positive_odds": {
                "total_predictions": total_predictions_pos_odds,
                "correct_predictions": correct_predictions_pos_odds,
                "accuracy": accuracy_pos_odds,
                "money_in": money_in_pos_odds,
                "profit": profit_pos_odds,
                "total_out": total_out_pos_odds,
            },
            "weekly_stats": weekly_stats
        }


@router.get("/model_accuracy_live")
def model_accuracy_live(user_id:int, model_id: int, connection=Depends(get_db)):
    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT game_id, prediction, probability, odds
            FROM game_bets
            WHERE model_id = %s
    """, (model_id,))

    predictions = cursor.fetchall()

    finished_games = []
    correct_predictions = 0
    total_predictions = len(predictions)
    
    # Debug statement: Print initial prediction count
    print(f"Total predictions in model_accuracy_live: {total_predictions}")

    for game in predictions:
        game_id, prediction, probability, odds = game

        cursor.execute(f"""
            SELECT
                CASE
                    WHEN home_points > away_points THEN 1
                    ELSE 0
                END AS target
            FROM team_game_stats
            WHERE game_id = %s
        """, (game_id,))

        result = cursor.fetchone()
        
        if result is not None:
            target = result[0]
            finished_games.append({
                "game_id": game_id,
                "prediction": prediction,
                "actual": target,
                "probability": probability,
                "odds": odds,
                "is_correct": prediction == target
            })
            if prediction == target:
                correct_predictions += 1

    cursor.close()

    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    
    # Debug statement: Print accuracy calculation details
    print(f"Correct predictions in model_accuracy_live: {correct_predictions}")
    print(f"Accuracy in model_accuracy_live: {accuracy}%")

    return {
        "model_id": model_id,
        "accuracy": accuracy,
        "finished_games": finished_games
    }


@router.get("/model_accuracy_live_with_probability")
def model_accuracy_live_with_probability(user_id: int, model_id: int, min_probability: float = 0, connection=Depends(get_db)):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT game_id, prediction, probability, odds
        FROM game_bets
        WHERE model_id = %s
    """, (model_id,))

    predictions = cursor.fetchall()
    
    finished_games = []
    correct_predictions = 0
    total_predictions = 0  # Count predictions that meet min_probability threshold
    pos_predictions = 0 
    neg_predictions = 0 


    # Debug statement: Print total predictions before filtering
    print(f"Total predictions in model_accuracy_live_with_probability: {len(predictions)}")

    for game in predictions:
        game_id, prediction, probability, odds = game

        # Check if the probability meets the minimum threshold
        if probability < min_probability:
            continue

        # Increment counter for filtered predictions
        total_predictions += 1

        if(odds > 0 ):
            pos_predictions += 1
        else:
            neg_predictions += 1


        cursor.execute("""
            SELECT
                CASE
                    WHEN home_points > away_points THEN 1
                    ELSE 0
                END AS target
            FROM team_game_stats
            WHERE game_id = %s
        """, (game_id,))

        result = cursor.fetchone()
        
        if result is not None:
            target = result[0]
            finished_games.append({
                "game_id": game_id,
                "prediction": prediction,
                "actual": target,
                "probability": probability,
                "odds": odds,
                "is_correct": prediction == target
            })
            if prediction == target:
                correct_predictions += 1

    cursor.close()

    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    
    # Debug statements: Print calculation details for filtered predictions
    print(f"Filtered predictions with min_probability >= {min_probability}: {total_predictions}")
    print(f"Correct predictions in model_accuracy_live_with_probability: {correct_predictions}")
    print(f"Accuracy in model_accuracy_live_with_probability: {accuracy}%")

    return {
        "model_id": model_id,
        "accuracy": accuracy,
        "min_probability": f"{min_probability}%",
        "total_predictions": total_predictions,
        "positive_predictions": pos_predictions,
        "negative_predictions": neg_predictions,
        "finished_games": finished_games,
    }
