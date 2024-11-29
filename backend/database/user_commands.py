import psycopg2
from model_builders.model_loader import model_loader
from fastapi import HTTPException


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


from fastapi import HTTPException

# Function to insert data into the "user" table
def insert_user(connection, user_data):
    try:
        cursor = connection.cursor()

        # Check if username is already in use
        cursor.execute(
            """
            SELECT * FROM users WHERE user_name = %s
            """, (user_data["user_name"],)
        )
        users = cursor.fetchall()
        if users:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Check if email is already in use
        cursor.execute(
            """
            SELECT * FROM users WHERE email = %s
            """, (user_data["email"],)
        )
        emails = cursor.fetchall()
        if emails:
            raise HTTPException(status_code=400, detail="Email already in use")

        # Insert new user
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
        raise HTTPException(status_code=500, detail="Internal Server Error")



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
