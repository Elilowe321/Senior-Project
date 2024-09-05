
'''
from __future__ import print_function
import time
import cfbd
from cfbd.rest import ApiException
from pprint import pprint
from database.database_commands import (
    cfbd_configuration,
    create_connection,
    create_recruiting_table,
    insert_recruiting_data,
)


def get_team_recruiting(connection, year):

    # Configure API key authorization: ApiKeyAuth
    configuration = cfbd_configuration()

    # create an instance of the API class
    api_instance = cfbd.RecruitingApi(cfbd.ApiClient(configuration))

    try:
        # Create recruting table
        create_recruiting_table(connection)

        api_response = api_instance.get_recruiting_teams(year=year)
        # print(api_response)
        insert_recruiting_data(connection, api_response)

    except ApiException as e:
        print("Exception when calling RecruitingApi->get_recruiting_teams: %s\n" % e)



connection = create_connection()

get_team_recruiting(connection, 2024)

connection.close()
'''


import cfbd
from cfbd.rest import ApiException
from database.database_commands import (
    create_connection,
    cfbd_configuration,
    create_team_talent_table,
    insert_team_talent_data,
    create_game_stats_table,
    insert_game_stats_data,
    create_betting_lines_table,
    insert_betting_lines_data,
)
from global_vars import Global


'''
Run once a year at beginning of season
'''
def get_team_talent(connection, year):
    # Configure API key authorization: ApiKeyAuth
    configuration = cfbd_configuration()

    # Create an instance of the API class
    api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))

    try:

        # Create table
        create_team_talent_table(connection)

        # Team talent composite rankings for a given year
        api_response = api_instance.get_talent(year=year)

        for school in api_response:
            # print(school.school, school.talent, school.year)
            insert_team_talent_data(connection, school)

    except ApiException as e:
        print("Exception when calling TeamsApi->get_talent: %s\n" % e)

'''
Run weekly before games
'''
def get_betting_lines(connection, year, week):
    # Configure API key authorization
    configuration = cfbd_configuration()

    # create an instance of the API class
    api_instance = cfbd.BettingApi(cfbd.ApiClient(configuration))

    try:

        # Create betting table
        create_betting_lines_table(connection)

        # For each team get all data
        api_response = api_instance.get_lines(year=year, week=week)

        # TODO:: Sometimes hometeam is different in games table and betting_lines table

        insert_betting_lines_data(connection, api_response)

    except ApiException as e:
        print("Exception when calling BettingApi->get_lines: %s\n" % e)


'''
Run weekly after games
'''
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


connection = create_connection()


for year in [2022, 2023]:
    for week in range(1, 17):
        get_betting_lines(connection, year, week)


# get_team_talent(connection, Global.year)
# get_betting_lines(connection, Global.year, Global.week)
# get_game_stats(connection, Global.year, Global.week-1)

connection.close()
