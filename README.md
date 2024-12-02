# Final Project
Web app that predicts the outcome of college football games

## Description of scripts
# create_teams_table.py:
  - Params: N/A
  - Calls cfbd api and gets all teams into database
  - Run once a year in case new teams get added
# create_team_talent_table.py:
  - Params: year
  - Calls cfbd api, gets each team and there talent ranking
  - Run once a year to get updated team talents
# create_recruiting_table.py:
  - Params: year
  - Calls cfbd api, gets recruiting ranking for every team that year
  - Run once a year to get updated team recruitment rankings
# create_games_table.py:
  - Params: year
  - Calls cfbd api, gets game data for games that have happened or are yet to happen
  - Some games will have scores and some may not have been finished
  - Run once a year to get all game ids and data
# create_game_stats_table.py:
  - Params: year, week
  - Calls cfbd api, gets game stats for a game that has already happened.
  - Run once a week after games are finshed to get fresh data.
# create_betting_lines_table.py
  - Params: year, week
  - Calls cfbd api, gets betting lines for a game that hasn't happened
  - Run once a week before games to get betting lines

## .env Vars
| Name | Description |
|------|-----------------|
| PGADMIN_EMAIL | Email for sql editor |
| PGADMIN_PASSWORD | Password for sql editor |
| DB_NAME | Name of db |
| DB_USER | User for db |
| DB_PASSWORD | Password for db |
| DB_HOST | db host |
| DB_PORT | db port |

## Run Program
1. Set up .env with appropriate variables in root folder (PGADMIN="..")
2. Run: 
```sh
docker compose up -d
```
or 

```sh
docker compose up --build
```
3. For Frontend: Go to localhost:3000
4. For API: Go to 127.0.0.1:8000/docs
5. For SQL Editor: Go to 127.0.0.1/5050

