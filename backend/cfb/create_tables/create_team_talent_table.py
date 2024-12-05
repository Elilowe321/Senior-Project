import cfbd
from cfbd.rest import ApiException
from pprint import pprint
from database.database_commands import (
    cfbd_configuration,
    create_connection,
    create_team_talent_table,
    insert_team_talent_data,
)

"""
Run Once a year
"""


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
            print(school.school, school.talent, school.year)
            insert_team_talent_data(connection, school)

    except ApiException as e:
        print("Exception when calling TeamsApi->get_talent: %s\n" % e)
