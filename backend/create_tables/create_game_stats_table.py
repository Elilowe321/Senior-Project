from __future__ import print_function
import cfbd
from cfbd.rest import ApiException
from database.database_commands import (
    cfbd_configuration,
    create_game_stats_table,
    insert_game_stats_data,
)

"""
Need to run each week (besides first week)
to get updated team stats for every game.
"""


def get_game_stats(connection, year, week):
    # Configure API key authorization: ApiKeyAuth
    configuration = cfbd_configuration()

    # create an instance of the API class
    games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))

    try:
        # Create the "games" table
        create_game_stats_table(connection)

        api_response = games_api.get_team_game_stats(
            year=year, week=week
        )

        insert_game_stats_data(connection, api_response, year)

    except ApiException as e:
        print("Exception when calling teams_api->get_fbs_teams: %s\n" % e)