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
actualData = {}

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Temperature, Log

@app.route('/', methods=['GET'])
def index():
    response = ""
    for device in actualData.keys():
        response = response + device + "\t"
        response = response + actualData[device][0]+ ";" + actualData[device][1] + "\n"
    return response


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
        actualData[name] = (time, temp)
        return "Good temperature request with: " +name+time+temp

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
