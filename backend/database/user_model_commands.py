import psycopg2
from model_builders.model_loader import model_loader
import json
from psycopg2 import sql


# Function to create a model for a user
def create_user_model_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_models (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(50) NOT NULL CHECK (name <> ''),
                description VARCHAR(255) NULL,
                type VARCHAR(20) NULL,
                target VARCHAR(50) NULL,
                file_location_class VARCHAR(50) NULL,
                file_location_reg VARCHAR(50) NULL,
                classification_accuracy FLOAT NULL,
                mse_home FLOAT NULL,
                mse_away FLOAT NULL,
                columns VARCHAR(50)[],
                UNIQUE (user_id, name)  -- Unique constraint on user_id and name

            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'user_models' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'user_models' table in PostgreSQL:", e)


# Function to insert data into the "user_model" table
def insert_user_model(connection, model_data):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
        INSERT INTO user_models (user_id, name, description, type, target, file_location_class, file_location_reg, classification_accuracy, mse_home, mse_away, columns)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                model_data["user_id"],
                model_data["name"],
                model_data["description"],
                model_data["type"],
                model_data["target"],
                model_data["file_location_class"],
                model_data["file_location_reg"],
                model_data["stats"]["classification_accuracy"],
                model_data["stats"]["mse_home"],
                model_data["stats"]["mse_away"],
                model_data["columns"],
            ),
        )

        connection.commit()
        cursor.close()

    except psycopg2.Error as e:
        connection.rollback()
        print("Error inserting data into PostgreSQL:", e)


# Gets a users models
def get_user_models(connection, user_id: int):
    try:
        cursor = connection.cursor()
        query = sql.SQL(
            """
            SELECT *
            FROM user_models
            WHERE user_id = %s
        """
        )
        cursor.execute(query, (user_id,))

        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        if rows:
            result = [dict(zip(column_names, row)) for row in rows]
            return result
        return None

    except psycopg2.Error as e:
        connection.rollback()
        print("Error getting user_model:", e)
        return None
    finally:
        cursor.close()


def get_specific_user_model(connection, model_id: int):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT *
            FROM user_models
            WHERE id = %s
            """,
            (model_id,),
        )

        row = cursor.fetchone()
        cursor.close()

        if row:
            column_names = [desc[0] for desc in cursor.description]
            result = dict(zip(column_names, row))
            return result

        return None

    except psycopg2.Error as e:
        connection.rollback()
        print("Error getting user_model:", e)
        return None
    finally:
        cursor.close()


# Creates a user model
def create_user_model(
    connection, user_id, model_columns, name, type, target, description=None
):
    try:
        create_user_model_table(connection)

        # Make sure the user doesn't have a model with that name already
        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT 1 
                    FROM user_models 
                    WHERE user_id = {user_id} 
                    AND name = '{name}'
                    """
        )

        existing_model = cursor.fetchone()

        if existing_model:
            return "Already created name"

        # Create model with given values
        model = model_loader(
            connection, model_columns, user_id, name, type, target, description
        )

        # Insert into database
        insert_user_model(connection, model)

        cursor.execute(
            f"""
            SELECT *
                FROM user_models
                WHERE user_id = {user_id}
                AND name = '{name}'
        """
        )

        row = cursor.fetchone()
        cursor.close()

        if row:
            column_names = [desc[0] for desc in cursor.description]
            result = dict(zip(column_names, row))
            return result

    except:
        return "Failed Creating"


# Updates a user model
def update_user_model(
    connection,
    model_id,
    model_columns=None,
    name=None,
    description=None,
    type=None,
    target=None,
):
    try:
        cursor = connection.cursor()

        # Build the SQL query dynamically
        important_change = False
        fields = []
        values = []

        if name is not None:
            fields.append("name = %s")
            values.append(name)

        if description is not None:
            fields.append("description = %s")
            values.append(description)

        if type is not None:
            fields.append("type = %s")
            values.append(type)

        if target is not None:
            fields.append("target = %s")
            values.append(target)

        if model_columns is not None:
            model_columns = json.dumps(model_columns)  # Convert list to JSON string
            model_columns = json.loads(model_columns)  # Deserialize JSON string to list
            fields.append("columns = %s")
            values.append(model_columns)

        if not fields:
            raise ValueError("No fields to update")

        update_query = f"UPDATE user_models SET {', '.join(fields)} WHERE id = %s"
        values.append(model_id)  # Append the model_id at the end for the WHERE clause

        cursor.execute(update_query, values)
        connection.commit()

        cursor.execute(
            f"""
            SELECT *
                FROM user_models
                WHERE id = '{model_id}'
        """
        )

        row = cursor.fetchone()
        cursor.close()

        if row:
            column_names = [desc[0] for desc in cursor.description]
            result = dict(zip(column_names, row))
            return result

    except:
        return "Failed updating"


# Delete a users models
def delete_user_model(connection, model_id):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            DELETE FROM user_models
            WHERE id = {model_id}
        """
        )
        connection.commit()
        cursor.close()
        return True  # Indicate successful deletion

    except psycopg2.Error as e:
        connection.rollback()
        print("Error deleting user model from PostgreSQL:", e)
        return False  # Indicate failure to delete




def create_test_model_prev_year_table(connection):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_model_prev_year (
                id SERIAL PRIMARY KEY,
                user_id INT,
                model_id INT,
                year INT,
                week INT,
                total_predictions INT,
                correct_predictions INT,
                money_in FLOAT,
                profit FLOAT,
                total_out FLOAT,
                total_predictions_neg_odds INT,
                correct_predictions_neg_odds INT,
                money_in_neg_odds FLOAT,
                profit_neg_odds FLOAT,
                total_out_neg_odds FLOAT,
                total_predictions_pos_odds INT,
                correct_predictions_pos_odds INT,
                money_in_pos_odds FLOAT,
                profit_pos_odds FLOAT,
                total_out_pos_odds FLOAT,
                safe_bet INT,
                min_probability FLOAT,
                time TIMESTAMP
            )
        """
        )

        connection.commit()
        cursor.close()

        # print("Table 'game_stats' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'test_model_prev_year' table in PostgreSQL:", e)