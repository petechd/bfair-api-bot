import betfairlightweight
from secrets import (
    address,
    password,
    certs,
    country,
    sport,
    app_key,
    teams,
    rating_teams,
    rating_address,
)
from betfairlightweight import filters
from urllib.request import urlopen
from bs4 import BeautifulSoup
from ast import literal_eval
import re
import time
import random


# dirs = os.listdir( path )

# This would print all the files and directories
# for file in dirs:
#    print(file)

trading = betfairlightweight.APIClient(address, password, app_key=app_key, certs=certs)

# login
trading.login()

# make event type request to find sport event type
football_event_type_id = trading.betting.list_event_types(
    filter=filters.market_filter(text_query=sport)
)
# returns one result
print(football_event_type_id)

file = open("dict.txt")
x = file.read()
favourable_odds = literal_eval(x)
f = open("dict_old.txt", "w")
f.write(str(favourable_odds))
f.close()


for event_type in football_event_type_id:
    # prints id, name and market count
    print(
        f"ID: {event_type.event_type.id}, Name: {event_type.event_type.name}, Market Count: {event_type.market_count}"
    )

    football_id = event_type.event_type.id
    for country in country:
        # list all sport market catalogues
        market_catalogues = trading.betting.list_market_catalogue(
            filter=filters.market_filter(
                event_type_ids=["1"],  # filter on just sport
                market_countries=[country],  # filter on just certain country
                in_play_only=False,
                # market_ids=['1.167981157'],
                # market_type_codes=['WIN'],  # filter on just WIN market types
                market_type_codes=["MATCH_ODDS"],
            ),
            market_projection=[
                "MARKET_START_TIME",
                "RUNNER_DESCRIPTION",
            ],  # runner description required
            max_results=1000,
        )

        print(f"Market catalogues returned: {len(market_catalogues)}")
        print("\n")
        print("\n")
        runner_dict = {}
        for market_catalogue in market_catalogues:
            # prints market id, market name and market start time
            if market_catalogue.market_name == "Match Odds":
                # print(
                #     market_catalogue.market_id, market_catalogue.market_name, market_catalogue.market_start_time
                # )
                runners = {}

                id_home = market_catalogue.runners[0].selection_id
                id_away = market_catalogue.runners[1].selection_id

                # print(market_catalogue.market_id)
                # print(f'{market_catalogue.runners[0].runner_name}({id_home}) vs. {market_catalogue.runners[1].runner_name}({id_away})')

                for runner in market_catalogue.runners:
                    runners[runner.selection_id] = runner.runner_name
                    if runner.runner_name != "The Draw":
                        runner_dict[runner.runner_name] = runner.selection_id
                    # if runner.runner_name != 'The Draw':
                    #     print(runner.selection_id, runner.runner_name)

                # market book request
                market_books = trading.betting.list_market_book(
                    market_ids=[market_catalogue.market_id],
                    price_projection=filters.price_projection(
                        price_data=filters.price_data(ex_all_offers=True)
                    ),
                )
                for market_book in market_books:
                    print(
                        f"Checking: {market_catalogue.runners[0].runner_name}({id_home}) vs. {market_catalogue.runners[1].runner_name}({id_away})"
                    )
                    try:
                        if list(teams.keys())[list(teams.values()).index(id_home)]:
                            team_name_home = list(teams.keys())[
                                list(teams.values()).index(id_home)
                            ]
                            team_name_away = list(teams.keys())[
                                list(teams.values()).index(id_away)
                            ]
                            time.sleep(random.randint(0, 0))
                            html = urlopen(
                                rating_address
                                + str(rating_teams[team_name_home])
                                + "&team2="
                                + str(rating_teams[team_name_away])
                            )
                            bs = BeautifulSoup(html.read(), "html5lib")
                            for child in bs.find(
                                "table", {"class": "bigtable"}
                            ).children:
                                test = child.text
                                regex = re.compile(r"\d.\d\d\d.\d\d\d.\d\d")
                                mo = regex.search(test)
                                if mo is not None:
                                    text2 = mo.group()
                                    if text2[0] != '0':
                                        n = 4
                                        text3 = [
                                            text2[i: i + n]
                                            for i in range(0, len(text2), n)
                                        ]
                                        rating_home = text3[0]
                                        rating_draw = text3[1]
                                        rating_away = text3[2]
                                    else:
                                        regex = re.compile(r"\d\d.\d\d\d.\d\d\d.\d\d")
                                        mo = regex.search(test)
                                        if mo is not None:
                                            text2 = mo.group()
                                            rating_home = text2[0:5]
                                            rating_draw = text2[5:9]
                                            rating_away = text2[9:13]
                                else:
                                    regex = re.compile(r"\d.\d\d\d.\d\d\d\d.\d\d")
                                    mo = regex.search(test)
                                    if mo is not None:
                                        text2 = mo.group()
                                        rating_home = text2[0:4]
                                        rating_draw = text2[4:8]
                                        rating_away = text2[8:13]
                                    else:
                                        regex = re.compile(r"\d.\d\d\d\d.\d\d\d\d.\d\d")
                                        mo = regex.search(test)
                                        text2 = mo.group()
                                        rating_home = text2[0:4]
                                        rating_draw = text2[4:9]
                                        rating_away = text2[9:14]
                                all_three = [rating_home, rating_draw, rating_away]
                            counter = 0
                            while counter <= 2:
                                for runner in runners:

                                    if float(
                                        market_book.runners[counter]
                                        .ex.available_to_back[0]
                                        .price
                                    ) > float(all_three[counter]):
                                        if (
                                            float(market_book.runners[counter].ex.available_to_back[0].price)
                                            < 3.0
                                        ):
                                            if (
                                                float(market_book.runners[counter].ex.available_to_back[0].price)
                                                - float(all_three[counter])
                                            ) > 0.20:
                                                print(
                                                    f"Event id: {market_catalogue.market_id}"
                                                )
                                                print(
                                                    f"{market_catalogue.runners[0].runner_name}({id_home}) vs. {market_catalogue.runners[1].runner_name}({id_away})"
                                                )
                                                print(
                                                    market_book.runners[counter],
                                                    market_book.runners[
                                                        counter
                                                    ].last_price_traded,
                                                )

                                                available_to_back = market_book.runners[
                                                    counter
                                                ].ex.available_to_back
                                                print(f"Home fair odds: {rating_home}")
                                                print(f"Draw fair odds: {rating_draw}")
                                                print(f"Away fair odds: {rating_away}")
                                                print("Back:")
                                                for price in available_to_back:
                                                    print(price)
                                                if counter == 0:
                                                    if (str(market_catalogue.market_id) + "/" + str(id_home)) not in favourable_odds.keys():
                                                        print("New event added to the list of events back home team)!")
                                                        favourable_odds[str(market_catalogue.market_id) + "/" + str(id_home)] = available_to_back[0].price
                                                elif counter == 2:
                                                    if (str(market_catalogue.market_id) + "/" + str(id_away)) not in favourable_odds.keys():
                                                        print("New event added to the list of events (back away team)!")
                                                        favourable_odds[str(market_catalogue.market_id) + "/" + str(id_away)] = available_to_back[0].price
                                    counter += 1
                            print("Checked!")
                    except ValueError:
                        continue
        print(runner_dict)

        # available_to_back = runner.ex.available_to_back
        # print('Back:')
        # for price in available_to_back:
        #     print(price)
        # available_to_lay = runner.ex.available_to_lay
        # print('Lay:')
        # for price in available_to_lay:
        #     print(price)
        # print('\n')

# logout
print(favourable_odds)
f = open("dict.txt", "w")
f.write(str(favourable_odds))
f.close()
trading.logout()
