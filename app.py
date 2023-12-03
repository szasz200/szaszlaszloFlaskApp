import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_folder='static')

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)
setConfig = False
time = datetime.now().timestamp()
sleep = 5

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Temperature, Log

@app.route('/', methods=['GET'])
def index():
    deviceData = Temperature.query.all()
    actualData = {}
    for device in deviceData:
        if (device.name not in actualData.keys()) or (actualData[device.name].time < device.time):
            device.time = str(datetime.fromtimestamp(int(device.time.replace('"',""))))
            actualData[device.name] = device
    return render_template('index.html', devices = actualData.values())

@app.route('/history', methods=['GET'])
def history():
    datas = Temperature.query.all()
    return render_template('history.html', devices = datas)

@app.route('/logs', methods=['GET'])
def logs():
    datas = Log.query.all()
    return render_template('logs.html', devices = datas)

@app.route('/delete', methods=['GET'])
def deleteDatas():
    db.session.query(Temperature).delete()
    db.session.query(Log).delete()
    db.session.commit()
    datas = Temperature.query.all()
    return render_template('index.html', devices = datas)

@app.route('/configure', methods=['GET'])
def configure():
    return render_template('configure.html')

def add_config():
    try:
        time = request.values.get('current_time')
        sleep = request.values.get('sleep_min')
    except (KeyError):
        return "Wrong temperature request."
    else:
        setConfig = True
        index()

@app.route('/temp', methods=['POST'])
def add_temp():
    try:
        name = request.values.get('device_name')
        time = request.values.get('time')
        temp = request.values.get('temp')
    except (KeyError):
        return "Wrong temperature request."
    else:
        temperature = Temperature()
        temperature.name = name
        temperature.time = time
        temperature.temperature = temp
        db.session.add(temperature)
        db.session.commit()
        if setConfig:
            return str(time)+"|"+str(sleep), 200
        else:
            return "Good temperature request with: " +name+time+temp, 201

@app.route('/log', methods=['POST'])
def add_log():
    try:
        time = request.values.get('time')
        content = request.values.get('content')
    except (KeyError):
        #Redisplay the question voting form.
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        log = Log()
        log.time = time
        log.content = content
        db.session.add(log)
        db.session.commit()

    return "Good log."

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
