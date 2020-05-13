import betfairlightweight
from betfairlightweight import filters
from secrets import (
    address,
    password,
    certs,
    country,
    sport,
    app_key,
    teams,
    rating_teams,
)
from ast import literal_eval

# create trading instance
trading = betfairlightweight.APIClient(address, password, app_key=app_key, certs=certs)

# login
trading.login()

# update for test


def place_order():
    file = open("dict.txt")
    x = file.read()
    y = literal_eval(x)
    file = open("dict_old.txt")
    a = file.read()
    b = literal_eval(a)
    for k in y:
        if k not in b:
            print(k)
            # placing an order
            market_id = k.split("/")[0]
            selection_id = k.split("/")[1]
            limit_order = filters.limit_order(
                size=2.00, price=y[k], persistence_type="LAPSE"
            )
            instruction = filters.place_instruction(
                order_type="LIMIT",
                selection_id=selection_id,
                side="BACK",
                limit_order=limit_order,
            )
            place_orders = trading.betting.place_orders(
                market_id=market_id, instructions=[instruction]  # list
            )

            print(place_orders.status)
            for order in place_orders.place_instruction_reports:
                print(
                    "Status: %s, BetId: %s, Average Price Matched: %s "
                    % (order.status, order.bet_id, order.average_price_matched)
                )


def update_order(bet_id):
    # updating an order
    instruction = filters.update_instruction(
        bet_id=bet_id, new_persistence_type="PERSIST"
    )
    update_order = trading.betting.update_orders(
        market_id=market_id, instructions=[instruction]
    )

    print(update_order.status)
    for order in update_order.update_instruction_reports:
        print("Status: %s" % order.status)


def replace_order(bet_id):
    # replacing an order
    instruction = filters.replace_instruction(bet_id=bet_id, new_price=1.10)
    replace_order = trading.betting.replace_orders(
        market_id=market_id, instructions=[instruction]
    )

    print(replace_order.status)
    for order in replace_order.replace_instruction_reports:
        place_report = order.place_instruction_reports
        cancel_report = order.cancel_instruction_reports
        print(
            "Status: %s, New BetId: %s, Average Price Matched: %s "
            % (order.status, place_report.bet_id, place_report.average_price_matched)
        )


def cancel_order(bet_id):
    # cancelling an order
    instruction = filters.cancel_instruction(bet_id=bet_id, size_reduction=2.00)
    cancel_order = trading.betting.cancel_orders(
        market_id=market_id, instructions=[instruction]
    )

    print(cancel_order.status)
    for cancel in cancel_order.cancel_instruction_reports:
        print(
            "Status: %s, Size Cancelled: %s, Cancelled Date: %s"
            % (cancel.status, cancel.size_cancelled, cancel.cancelled_date)
        )


carry_on = input("Do you want to bet?")
if carry_on == "y":
    place_order()
    trading.logout()
