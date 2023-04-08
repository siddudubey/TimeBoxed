from flask import Flask, redirect, request, render_template
import kiteconnect
import os
from instrument_data import calculate_stats

app = Flask(__name__, template_folder='templates')

api_key = os.environ.get('KITE_API_KEY')
kite = kiteconnect.KiteConnect(api_key)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/zlogin')
def zlogin():
    login_url = kite.login_url()
    return redirect(login_url)

@app.route('/zlogin/redirect')
def redirect_handler():
    # parse the response parameters
    res_params = {
        "request_token": request.args.get("request_token"),
        "status": request.args.get("status"),
        "action": request.args.get("action")
    }
    
    # check if the request was successful
    if res_params["status"] == "success":
        if res_params["action"] == "login":
            # get access token
            try:
                api_secret = os.environ.get('KITE_API_SECRET')
                session_response = kite.generate_session(res_params["request_token"], api_secret=api_secret)
                # store the access token in session
                kite.set_access_token(session_response["access_token"])
                print("access token set. " + session_response["access_token"])
                return redirect("/price_stats")
            except Exception as e:
                return "Error generating access token: " + str(e)
        else:
            return "Invalid action!"
    else:
        return "Authentication failed"
    
@app.route('/price_stats', methods=['GET', 'POST'])
def price_stats():
    if request.method == 'POST':
        instrument = int(request.form['instrument'])
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        # calculate the stats using the instrument_data module
        stats = calculate_stats(kite, instrument, start_time, end_time)
        return render_template('price_stats.html', stats=stats, instrument=instrument, start_time=start_time, end_time=end_time)
    else:
        return render_template('price_stats.html')

if __name__ == '__main__':
    app.run(debug=True)
