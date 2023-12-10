from flask import Flask, redirect, request, render_template, send_from_directory
import kiteconnect
import os
from instrument_data import calculate_stats, nifty_nearest_atm_otions

app = Flask(__name__, template_folder='templates')

if os.environ.get('FLASK_ENV') == 'production':
    from flask_sslify import SSLify
    sslify = SSLify(app)

api_key = os.environ.get('KITE_API_KEY')
kite = kiteconnect.KiteConnect(api_key)

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/resume')
def download_resume():
    return send_from_directory('static', 'vivekanand_resume.pdf', as_attachment=True)

@app.route('/sirius')
def sirius():
    # return render_template('sirius.html', title='Project Sirius')
    classes = [
        {"title": "Time and space complexity, Part 1", "description": "Theoretical background of time and space complexity in analysis of algorithms.", "link": "https://tldv.io/app/meetings/64ecc5024bfc27001357bf2c"},
        {"title": "Time and space complexity, Part 2", "description": "Theoretical background of time and space complexity in analysis of algorithms.", "link": "https://tldv.io/app/meetings/64ee16c54ce21000122d24ec"},
        {"title": "Binary Search, Part 1", "description": "We explore the binary search technique in this class.", "link": "https://youtu.be/1ELX88hH--8"},
        {"title": "Binary Search, Part 2", "description": "Continued binary search class after part 1", "link": "https://youtu.be/MAMEctg-Zss"},
        {"title": "Binary Search, Part 3", "description": "Solving problems using binary search technique.", "link": "https://tldv.io/app/meetings/64f60138ef183d001390f2bb"},
        {"title": "Backtracking", "description": "Exploration of backtracking concept and solving a problem with a large number of options.", "link": "https://tldv.io/app/meetings/650876cbe2cf6900135828c7"},
        {"title": "Two Pointers, Part 2", "description": "We discuss variety of problems solvable using two pointer technique.", "link": "https://tldv.io/app/meetings/653655293993ed0012ead7b7"},
        
        # Add more classes as needed
    ]
    return render_template('sirius.html', classes=classes, title='Project Sirius')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Me')

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
                print("access token set. ") # + session_response["access_token"])
                return redirect("/nearest")
            except Exception as e:
                return "Error generating access token: " + str(e)
        else:
            return "Invalid action!"
    else:
        return "Authentication failed"
    
@app.route('/timeboxed', methods=['GET', 'POST'])
def price_stats():
    if request.method == 'POST':
        instrument = int(request.form['instrument'])
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        # calculate the stats using the instrument_data module
        stats = calculate_stats(kite, instrument, start_time, end_time)
        return render_template('timeboxed.html',
                                stats=stats,
                                instrument=instrument,
                                start_time=start_time,
                                end_time=end_time)
    else:
        return render_template('timeboxed.html')

@app.route('/nearest', methods=['GET', 'POST'])
def nearest_options():
    if request.method == 'GET':
        [nifty_index_level, atm_call_option, atm_put_option] = nifty_nearest_atm_otions(kite)
        return render_template('nearest_instruments.html',
                                nifty_level=nifty_index_level,
                                call_option=atm_call_option,
                                put_option=atm_put_option)
    else:
        return "Nothing to be done!"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=443, ssl_context=('server.crt', 'server.key'))

