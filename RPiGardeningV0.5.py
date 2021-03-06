import RPi.GPIO as GPIO
import threading
import Adafruit_DHT as dht
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from time import sleep
from functools import wraps

app = Flask(__name__)

# Load the config file
app.config.from_pyfile('config.cfg')
app.static_folder = 'static'
app.secret_key = app.config['SECRETKEY']

GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, pin state, and timers:
pins = {
    app.config['DEVICE1PIN'] : {'name' : app.config['DEVICE1NAME'], 'state' : app.config['DEVICE1STATE'], 'timeon' : app.config['DEVICE1TIMEON'], 'timeoff' : app.config['DEVICE1TIMEOFF'], 'timerstate' : app.config['DEVICE1TIMER']},
    app.config['DEVICE2PIN'] : {'name' : app.config['DEVICE2NAME'], 'state' : app.config['DEVICE2STATE'], 'timeon' : app.config['DEVICE2TIMEON'], 'timeoff' : app.config['DEVICE2TIMEOFF'], 'timerstate' : app.config['DEVICE2TIMER']},
    app.config['DEVICE3PIN'] : {'name' : app.config['DEVICE3NAME'], 'state' : app.config['DEVICE3STATE'], 'timeon' : app.config['DEVICE3TIMEON'], 'timeoff' : app.config['DEVICE3TIMEOFF'], 'timerstate' : app.config['DEVICE3TIMER']},
    app.config['DEVICE4PIN'] : {'name' : app.config['DEVICE4NAME'], 'state' : app.config['DEVICE4STATE'], 'timeon' : app.config['DEVICE4TIMEON'], 'timeoff' : app.config['DEVICE4TIMEOFF'], 'timerstate' : app.config['DEVICE4TIMER']}
    }

# Set each pin as an output and make it low:
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    
# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap       

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('status'))       
    return render_template('login.html')
    

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))       
    
@app.route("/")
@login_required
def status():
    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)
    # Along with the pin dictionary, put the message into the template data dictionary:
    templateData = {
      'pins' : pins
    }

    return render_template('index.html', **templateData)  

# ajax GET call this function to set led state
# depeding on the GET parameter sent
@app.route("/_state")
@login_required
def _state():
    state = request.args.get('state')
    print(state)
    pin = request.args.get('pin')
    print(pin)
    if state=="Power ON":
        GPIO.output(int(pin), GPIO.LOW)
    else:
        GPIO.output(int(pin), GPIO.HIGH)
    for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)    
    return "" 

# ajax GET call this function periodically to read button state
# the state is sent back as json data
@app.route("/_temphum")
def _temphum():
    # Read the temp and humidity
    temphumid = app.config['TEMPHUMPIN']
    while 1:
        h,t = dht.read_retry(dht.DHT22, int(temphumid))
        CtoF = t*9/5+32
        temp = '{0:0.1f}'.format(CtoF)
        humidity = '{0:0.1f}'.format(h)
        return jsonify(tempState=temp, humState=humidity)    
   
# ------------------------------------- Timer section for all devices ---------------------------------------------------   
def Device1Timer(): # Timer for Device 1
    while 1:
        if app.config['DEVICE1TIMER'] == 'ON':
            time1 = app.config['DEVICE1TIMEON']
            time2 = app.config['DEVICE1TIMEOFF']
            GPIO.output(app.config['DEVICE1PIN'], GPIO.LOW)
            sleep(float(time1)*3600)
            GPIO.output(app.config['DEVICE1PIN'], GPIO.HIGH)
            sleep(float(time2)*3600)
        else:
            sleep(30)
        
def Device2Timer(): # Timer for Device 2
    while 1:
        if app.config['DEVICE2TIMER'] == 'ON':
            time1 = app.config['DEVICE2TIMEON']
            time2 = app.config['DEVICE2TIMEOFF']
            GPIO.output(app.config['DEVICE2PIN'], GPIO.LOW)
            sleep(float(time1)*3600)
            GPIO.output(app.config['DEVICE2PIN'], GPIO.HIGH)
            sleep(float(time2)*3600)
        else:
            sleep(30)
        
def Device3Timer(): # Timer for Device 3
    while 1:
        if app.config['DEVICE3TIMER'] == 'ON':
            time1 = app.config['DEVICE3TIMEON']
            time2 = app.config['DEVICE3TIMEOFF']
            GPIO.output(app.config['DEVICE3PIN'], GPIO.LOW)
            sleep(float(time1)*3600)
            GPIO.output(app.config['DEVICE3PIN'], GPIO.HIGH)
            sleep(float(time2)*3600)
        else:
            sleep(30)

def Device4Timer(): # Timer for Device 4
    while 1:
        if app.config['DEVICE4TIMER'] == 'ON':
            time1 = app.config['DEVICE4TIMEON']
            time2 = app.config['DEVICE4TIMEOFF']
            GPIO.output(app.config['DEVICE4PIN'], GPIO.LOW)
            sleep(float(time1)*3600)
            GPIO.output(app.config['DEVICE4PIN'], GPIO.HIGH)
            sleep(float(time2)*3600)
        else:
            sleep(30)
        
#------------------------------------------ Threads for timers --------------------------------------

# Device 1 timer thread        
thread1 = threading.Thread(target=Device1Timer)
thread1.daemon = True
thread1.start()

# Device 2 timer thead
thread2 = threading.Thread(target=Device2Timer)
thread2.daemon = True
thread2.start()

# Device 3 timer thead
thread3 = threading.Thread(target=Device3Timer)
thread3.daemon = True
thread3.start()

# Device 4 timer thread
thread4 = threading.Thread(target=Device4Timer)
thread4.daemon = True
thread4.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    looping = True