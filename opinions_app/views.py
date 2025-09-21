from random import randrange

from flask import abort, flash, redirect, render_template, url_for

from opinions_app import app, db
from opinions_app.forms import OpinionForm
from opinions_app.models import Opinion


def random_opinion():
    """Возвращает случайную запись из модели Opinion.

    Функция подсчитывает общее количество мнений в базе данных.
    Если мнения присутствуют, генерируется случайное смещение (offset),
    и выбирается первая запись, начиная с этого смещения.
    Таким образом, выбирается случайное мнение.

    Returns:
        Opinion: Объект модели Opinion, если мнения существуют.
        None: Если в базе данных нет мнений.
    """
    quantity = Opinion.query.count()
    if quantity:
        offset_value = randrange(quantity)
        opinion = Opinion.query.offset(offset_value).first()
        return opinion


@app.route('/')
def index_view():
    opinion = random_opinion()
    if opinion is None:
        abort(500)

    return render_template('opinion.html', opinion=opinion)


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    form = OpinionForm()
    if form.validate_on_submit():
        text = form.text.data
        if Opinion.query.filter_by(text=text).first() is not None:
            flash(
                'Мнение с таким текстом уже существует',
                category='warning'
            )
            return render_template('add_opinion.html', form=form)
        opinion = Opinion(
            title=form.title.data,
            text=form.text.data,
            source=form.source.data
        )
        db.session.add(opinion)
        db.session.commit()
        return redirect(url_for('opinion_view', id=opinion.id))
    return render_template('add_opinion.html', form=form)


@app.route('/opinions/<int:id>')
def opinion_view(id):
    opinion = Opinion.query.get_or_404(id)
    return render_template('opinion.html', opinion=opinion)
