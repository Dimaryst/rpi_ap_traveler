from flask import Flask, render_template, url_for, request, Response, jsonify
from flask_restful import Resource, Api
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

db = SQLAlchemy()

app = Flask(__name__, static_folder="static")
app.config.from_pyfile('db/pg_conf.py')

db.init_app(app)

@app.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

@app.route('/requests', methods=['GET'])
def requests_page():
    sql = f"""SELECT * FROM users;"""
    result = db.session.execute(sql)
    usrs = []
    for r in result:
            usrs.append(r)
    print(usrs)
    return render_template('requests.html', users = usrs)

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
