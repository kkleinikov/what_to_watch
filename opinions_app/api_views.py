from flask import jsonify, Response, request
from sqlalchemy.exc import SQLAlchemyError

from opinions_app import app, db
from opinions_app.error_handlers import InvalidAPIUsage
from opinions_app.models import Opinion
from opinions_app.views import random_opinion


@app.route('/api/opinions/<int:opinion_id>/', methods=['GET'])
def get_opinion(opinion_id: int) -> tuple[Response, int]:
    """Retrieve a specific opinion by its ID via a GET request.

    Args:
        opinion_id (int): The ID of the opinion to retrieve.

    Returns:
        tuple[Response, int]: A Flask response object with JSON data
        and HTTP status code 200.

    Raises:
        404: If no opinion is found with the provided ID.
    """
    opinion = Opinion.query.get(opinion_id)
    if opinion is None:
        raise InvalidAPIUsage(
            'Мнение с таким ID не найдено',
            404
        )
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:opinion_id>/', methods=['PATCH'])
def update_opinion(opinion_id: int) -> tuple[Response, int]:
    """Обновляет мнение по указанному идентификатору с использованием
    PATCH-запроса.

    Этот эндпоинт позволяет частично обновить поля мнения,
    отправив JSON-данные.
    Обновляются только те поля, которые были переданы в запросе.
    Остальные остаются без изменений.

    Args:
        opinion_id (int): Уникальный идентификатор мнения, которое необходимо
        обновить.

    Returns:
        tuple[Response, int]: Объект ответа Flask с данными обновлённого
                              мнения в формате JSON
                              и HTTP-статусом 200 (OK).

    Raises:
        InvalidAPIUsage: С 400 — если JSON некорректен.
                         С 409 — если мнение с таким текстом уже существует.
                         С 500 — при ошибке базы данных.
    """

    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(
            'Неверный JSON формат',400
        )
    if (
        'text' in data and
        Opinion.query.filter_by(text=data['text']).first() is not None
    ):
        raise InvalidAPIUsage('Мнение с таким текстом уже существует')

    opinion = Opinion.query.get_or_404(opinion_id)
    opinion.title = data.get('title', opinion.title)
    opinion.text = data.get('text', opinion.text)
    opinion.source = data.get('source', opinion.source)
    opinion.added_by = data.get('added_by', opinion.added_by)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise InvalidAPIUsage(
            f'Произошла ошибка базы данных ({str(e)}), '
            'при обновлении мнения',
            500
        )

    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:opinion_id>/', methods=['DELETE'])
def delete_opinion(opinion_id: int) -> tuple[str, int]:
    """Удаляет мнение по указанному идентификатору.

    Эта функция удаляет запись о мнении из базы данных. Если мнение с
    указанным ID не найдено, Flask выбрасывает исключение 404 (Not Found),
    которое обрабатывается автоматически.

    Args:
        opinion_id (int): Уникальный идентификатор мнения для удаления.

    Returns:
        tuple[str, int]: Пустая строка и HTTP-код 204 (No Content),
        сигнализирующий об успешном удалении.
    """
    opinion = Opinion.query.get_or_404(opinion_id)
    try:
        db.session.delete(opinion)
        db.session.commit()
    except SQLAlchemyError as e:
        # В случае ошибки откатываем транзакцию и возвращаем
        # 500 Internal Server Error
        db.session.rollback()
        return f'Ошибка при удалении мнения: {str(e)}', 500

    return '', 204


@app.route('/api/opinions/', methods=['GET'])
def get_opinions() -> tuple[Response, int]:
    """Возвращает список всех мнений.

    Эта функция выполняет запрос ко всем записям модели `Opinion` и
    преобразует их в формат JSON. Каждое мнение сериализуется с помощью
    метода `to_dict()`.

    Returns:
        tuple[Response, int]: Ответ Flask с данными в формате JSON
         и статус-кодом 200 (OK).
    """
    opinions = Opinion.query.all()
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200


@app.route('/api/opinions/', methods=['POST'])
def add_opinion() -> tuple[Response, int]:
    """Создаёт новое мнение на основе данных из JSON-запроса.

    Функция принимает данные в формате JSON, создает объект `Opinion`,
    заполняет его поля с помощью метода `from_dict()` и сохраняет
     в базу данных.

    В случае ошибки базы данных транзакция откатывается и возвращается
    сообщение об ошибке с кодом 500 (Internal Server Error).

    Returns:
        tuple[Response, int]: Ответ Flask с данными нового мнения
        в формате JSON и статус-кодом 201 (Created).

    Raises:
    InvalidAPIUsage: С 400 — если JSON некорректен.
                     С 409 — если мнение с таким текстом уже существует.
                     С 500 — при ошибке базы данных.
    """
    data = request.get_json(silent=True)

    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('Недостаточно данных для создания мнения')

    if Opinion.query.filter_by(text=data['text']).first() is not None:
        raise InvalidAPIUsage(
            'Мнение с таким текстом уже существует',
            409
        )

    opinion = Opinion()
    opinion.from_dict(data)
    try:
        db.session.add(opinion)
        db.session.commit()
    except SQLAlchemyError as e:
        raise InvalidAPIUsage(
            f'Произошла ошибка базы данных ({str(e)}), '
            'при добавлении мнения',
            500
        )

    return jsonify({'opinion': opinion.to_dict()}), 201


@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion() -> tuple[Response, int]:
    """Возвращает случайное мнение из базы данных.

    Эта функция вызывает вспомогательную функцию `random_opinion()`, которая
    выбирает случайную запись из модели `Opinion`. Если мнений нет,
    возвращается сообщение об ошибке и статус-код 404.

    Returns:
        tuple[Response, int]: Ответ Flask с данными мнения в формате JSON
                              и HTTP статус-кодом 200 (OK), либо сообщение
                              об ошибке и код 404, если мнений нет.
    """
    opinion = random_opinion()
    if opinion is None:
        raise InvalidAPIUsage(
            'В базе данных нет мнений',
            404
        )
    return jsonify({'opinion': opinion.to_dict()}), 200
