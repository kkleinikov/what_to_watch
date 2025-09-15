import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'SQLALCHEMY_DATABASE_URI', 'sqlite:///db.sqlite3'
)
db = SQLAlchemy(app)

@app.route('/')
def index_view():
    print(app.config)
    return 'Совсем скоро тут будет случайное мнение о фильме!'

if __name__ == '__main__':
    # app.run()
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
