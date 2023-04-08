from kiteconnect import KiteConnect
from datetime import datetime

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
