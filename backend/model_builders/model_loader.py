import pandas as pd
from database.database_commands import (
    get_column_stats,
)
from model_builders.create_models import (
    gradient_boost,
    random_forest,
    user_created_model,
    target_provided,
)
from model_builders.predict_games import predict_games
from pprint import pprint


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
