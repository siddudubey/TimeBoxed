from kiteconnect import KiteConnect
from datetime import datetime, date
from calendar import monthrange

def calculate_stats(kite, instrument, start_time, end_time):
    #instrument_token = get_instrument_token(kite, instrument)
    start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
    end_dt = datetime.strptime(end_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

    # Convert the start and end times to datetime objects
    # start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    # end_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    # Get the historical data for the instrument
    interval = "minute"
    historical_data = kite.historical_data(instrument, start_dt, end_dt, interval)

    # Calculate the statistics   
    high = max(historical_data, key=lambda x: x['high'])['high']
    low = min(historical_data, key=lambda x: x['low'])['low']
    close_prices = [candle['close'] for candle in historical_data]
    avg = sum(close_prices) / len(close_prices)
 
    # Return the statistics as a dictionary
    return {
        'high': high,
        'low': low,
        'avg': avg
    }

def nifty_nearest_atm_otions(kite):
    # Get quote for NIFTY 50 index
    nifty_index_level = kite.quote("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
    # print(f"Current NIFTY level: {nifty_index_level}")

    # Example NIFTY CE/PE: symbol=NIFTY2341317600CE is for NIFTY 13 April 2023 17600 CE

    # we want all symbols for NIFTY options expiring in current month
    current_date = date.today()
    cur_month_last_date = date(current_date.year,
                                         current_date.month,
                                         monthrange(current_date.year, current_date.month)[1])
    # another way to find these symbols is to use a string match like "NIFTY234" to get all options expiring in Aplir 2023
    # commenting this option for now and using the month's last date to find all expiries in month 
    # month = int(current_date.strftime("%m"))
    # nifty_option_symbol_cur_month = "NIFTY" + current_date.strftime(f"%y{month}")
    
    nfo_instruments = kite.instruments("NFO")
    # Filter instruments for NIFTY index options expiring in current month
    nfo_cur_month_instruments = [instrument for instrument in nfo_instruments
                                    if (instrument["name"] == "NIFTY" and
                                        instrument["segment"] == "NFO-OPT" and
                                        instrument["expiry"] <= cur_month_last_date)]

    # If information is not found, raise an error
    if nfo_cur_month_instruments is None:
        raise ValueError("Could not find NIFTY options expiring before ", cur_month_last_date)

    # Get the nearest expiry date from the current date
    nearest_expiry = min(nfo_cur_month_instruments,
                         key=lambda x: abs(x['expiry'] - current_date))['expiry']
    nfo_cur_week_instruments = [instrument for instrument in nfo_cur_month_instruments
                                 if instrument["expiry"] == nearest_expiry]

    # If current week expiry information is not found, raise an error
    if nfo_cur_week_instruments is None:
        raise ValueError("Could not find NIFTY options expiring in this week, on: ", nearest_expiry)

    # Find nearest ATM call option
    atm_call_option = None
    atm_put_option = None
    for option in nfo_cur_week_instruments:
        if option["instrument_type"] == "CE":
            if not atm_call_option or abs(option["strike"] - nifty_index_level) < abs(atm_call_option["strike"] - nifty_index_level):
                atm_call_option = option
        elif option["instrument_type"] == "PE":
            if not atm_put_option or abs(option["strike"] - nifty_index_level) < abs(atm_put_option["strike"] - nifty_index_level):
                atm_put_option = option

    # print(f"\n\n{atm_call_option}\n\n{atm_put_option}\n\n")
    # Return instrument name, instrument ID, and price for ATM call and put options
    if atm_call_option and atm_put_option:
        # Get the current price of the ATM option
        atm_option_quote = kite.quote([atm_call_option['instrument_token'], atm_put_option['instrument_token']])
        atm_call_option_price = atm_option_quote[f"{atm_call_option['instrument_token']}"]["last_price"]
        atm_call_option['last_price'] = atm_call_option_price
        atm_put_option_price = atm_option_quote[f"{atm_put_option['instrument_token']}"]["last_price"]
        atm_put_option['last_price'] = atm_put_option_price
        print("ATM Call Option: ",
                atm_call_option['tradingsymbol'],
                atm_call_option['instrument_token'],
                atm_call_option['last_price'],
                atm_call_option_price)
        print("ATM Put Option: ",
                atm_put_option['tradingsymbol'],
                atm_put_option['instrument_token'],
                atm_put_option['last_price'],
                atm_put_option_price)
    else:
        raise ValueError("Could not nearest CE and PE to NIFTY ATM")

    # Return the statistics as a dictionary
    return [nifty_index_level, atm_call_option, atm_put_option]
