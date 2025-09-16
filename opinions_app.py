from datetime import datetime
import os
from random import randrange

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'SQLALCHEMY_DATABASE_URI', 'sqlite:///db.sqlite3'
)
db = SQLAlchemy(app)



class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

@app.route('/')
def index_view():
    quantity = Opinion.query.count()
    if not quantity:
        return '''
            <h1>Скоро тут будет случайное мнение о фильме!</h1>
            <p>Но пока что нет ни одного мнения.</p>
        '''
    offset_value = randrange(quantity)
    opinion = Opinion.query.offset(offset_value).first()
    return render_template('opinion.html', opinion=opinion)


@app.route('/add')
def add_opinion_view():
    return render_template('add_opinion.html')


if __name__ == '__main__':
    # app.run()
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
