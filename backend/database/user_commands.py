import psycopg2
from model_builders.model_loader import model_loader


# Function to create a user
def create_user_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                user_name VARCHAR(50) NOT NULL UNIQUE,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(50) NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                paid BOOLEAN NOT NULL,
                earnings INT NOT NULL
            )
        """
        )
        connection.commit()
        cursor.close()

        print("Table 'users' created successfully.")
    except psycopg2.Error as e:
        connection.rollback()

        print("Error creating 'users' table in PostgreSQL:", e)


# Function to insert data into the "user" table
def insert_user(connection, user_data):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
        INSERT INTO users (user_name, first_name, last_name, email, hashed_password, paid, earnings)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (
                user_data["user_name"],
                user_data["first_name"],
                user_data["last_name"],
                user_data["email"],
                user_data["hashed_password"],
                user_data["paid"],
                0
            ),
        )

        connection.commit()
        cursor.close()

        return "User created"

    except psycopg2.Error as e:
        connection.rollback()
        print("Error inserting data into PostgreSQL:", e)


# Return all users
def get_users(connection):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_id, user_name, first_name, last_name, email, hashed_password, paid, earnings
            FROM users;
            """
        )

        rows = cursor.fetchall()

        connection.commit()
        cursor.close()

        return rows

    except psycopg2.Error as e:
        connection.rollback()
        print("Error inserting data into PostgreSQL:", e)
        return []
