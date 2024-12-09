from cfb.database.database_commands import create_connection, create_game_bets_table, insert_game_bets
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from ..routers.cfb_model_router import get_user_specific_model_handler
from model_builders.cfb_model_loader import predict_games
from cfb.create_tables.create_betting_lines_table import get_betting_lines
from global_vars import Global
from cfb.database.user_model_commands import create_test_model_prev_year_table

router = APIRouter() 


# Database connection
def get_db():
    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()


'''
When a user clicks on a model to find the predicted games,
1. Will get updated betting lines 
2. Get the model and predict the games
3. Add the betting lines to the games
'''
@router.post("/{user_id}/cfb/{model_id}")
def model_predicted_games(user_id: int, model_id: int, connection=Depends(get_db)):

    # Update betting lines for the given year and week
    get_betting_lines(connection, Global.year, Global.week)

    model = get_user_specific_model_handler(user_id, model_id, connection)

    create_game_bets_table(connection)

    # Get file path
    class_filepath = ""
    reg_filepath = ""
    if model.type == "classification":
        class_filepath = model.file_location_class
        predicted_games_class = predict_games(
            connection,
            year=Global.year,
            week=Global.week,
            type=model.type,
            target=model.target,
            season_type=Global.season_type,
            chosen_columns=model.columns,
            class_file_path=class_filepath,
        )

        if predicted_games_class:
            # Convert the dictionary to a list of items and return the first item

            insert_game_bets(connection, predicted_games_class, model_id)

            return predicted_games_class

        else:
            return {"error": "No predictions available"}

    elif model.type == "regression":
        reg_filepath = model.file_location_reg
        predicted_games_reg = predict_games(
            connection,
            year=Global.year,
            week=Global.week,
            type=model.type,
            target=model.target,
            season_type=Global.season_type,
            chosen_columns=model.columns,
            reg_file_path=reg_filepath,
        )

        if predicted_games_reg:
            # Convert the dictionary to a list of items and return the first item
            # first_prediction = list(predicted_games_reg.items())[0]
            # return {first_prediction[0]: first_prediction[1]}
            return predicted_games_reg

        else:
            return {"error": "No predictions available"}

    else:
        return {"error": "Invalid model type"}


@router.get("/betting_lines")
def betting_lines(connection=Depends(get_db)):
    get_betting_lines(connection, Global.year, Global.week)






import matplotlib.pyplot as plt
import io
import base64

def generate_graph(data, title):
    fig, ax = plt.subplots()
    weeks = [entry['week'] for entry in data]
    profits = [entry['profit'] for entry in data]
    
    ax.plot(weeks, profits, marker='o', linestyle='-', color='b')
    ax.set_xlabel('Week')
    ax.set_ylabel('Profit')
    ax.set_title(title)
    
    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    
    # Encode the plot as base64
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_str

def generate_cumulative_graph(data, title):
    fig, ax = plt.subplots()
    weeks = [entry['week'] for entry in data]
    profits = [entry['profit'] for entry in data]
    
    # Calculate cumulative profit
    cumulative_profit = [sum(profits[:i+1]) for i in range(len(profits))]
    
    ax.plot(weeks, cumulative_profit, marker='o', linestyle='-', color='g')
    ax.set_xlabel('Week')
    ax.set_ylabel('Cumulative Profit')
    ax.set_title(title)
    
    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    
    # Encode the plot as base64
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_str

