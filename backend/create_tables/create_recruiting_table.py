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


"""
Gets Recruiting rankings for a team in a specific year
"""


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
