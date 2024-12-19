from __future__ import print_function
import time
import cfbd
from cfbd.rest import ApiException
from pprint import pprint
from cfb.database.database_commands import (
    cfbd_configuration,
    create_connection,
    create_betting_lines_table,
    insert_betting_lines_data,
) 


def get_betting_lines(connection, year, week, season_type):
    # Configure API key authorization
    configuration = cfbd_configuration()

    # create an instance of the API class
    api_instance = cfbd.BettingApi(cfbd.ApiClient(configuration))

    try:

        # Create betting table
        create_betting_lines_table(connection)

        # For each team get all data
        api_response = api_instance.get_lines(year=year, week=week, season_type=season_type)
        pprint(api_response)
        print(len(api_response))

        insert_betting_lines_data(connection, api_response)

    except ApiException as e:
        print("Exception when calling BettingApi->get_lines: %s\n" % e)