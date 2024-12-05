from __future__ import print_function
import cfbd
from cfbd.rest import ApiException
from pprint import pprint
from database.database_commands import (
    cfbd_configuration,
    create_connection,
    create_teams_table,
    insert_teams_data,
)

"""
Since all the teams are determined before the season starts
and the database saves those games,
only need to call this at the start of each season

for year in range(2001, 2024): # TODO:: Not needed anymore
"""


def get_teams(connection):
    # Configure API key authorization: ApiKeyAuth
    configuration = cfbd_configuration()

    # create an instance of the API class
    teams_api = cfbd.TeamsApi(cfbd.ApiClient(configuration))

    try:
        # Create the "teams" table
        create_teams_table(connection)

        # Get all fbs teams
        api_response = teams_api.get_teams()

        # Insert data into the "teams" table
        insert_teams_data(connection, api_response)
        print(f"Num of Teams: {len(api_response)}")

    except ApiException as e:
        print("Exception when calling teams_api->get_teams: %s\n" % e)
