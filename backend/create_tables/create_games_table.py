from __future__ import print_function
import cfbd
from cfbd.rest import ApiException
from database.database_commands import (
    cfbd_configuration,
    create_connection,
    create_games_table,
    insert_games_data,
)

"""
Since all the games are determined before the season starts
and the database saves those games,
only need to call this at the start of each season

for year in range(2001, 2024): # TODO:: Not needed anymore
"""


def get_games(connection, year):

    # Configure API key authorization
    configuration = cfbd_configuration()

    # Create an instance of the API class
    games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))

    try:
        # Create the "games" table
        create_games_table(connection)

        # Get games data from the API
        api_response = games_api.get_games(year=year)

        # Insert data into the "games" table
        insert_games_data(connection, api_response)

    except ApiException as e:
        print("Exception when calling teams_api->get_teams: %s\n" % e)
