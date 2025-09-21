from datetime import datetime
from typing import Dict, Any

from opinions_app import db


VALID_FIELDS = {'title', 'text', 'source', 'added_by'}


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
    added_by = db.Column(db.String(64))

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance into a dictionary for JSON serialization.

        Returns:
            Dict[str, Any]: A dictionary representation of the model.
        """
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'source': self.source,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'added_by': self.added_by
        }


    def from_dict(self, data: Dict[str, Any]) -> None:
        """Заполняет атрибуты экземпляра данными из словаря.

        Аргумент:
            data (Dict[str, Any]): Словарь с данными, где ключи соответствуют
                                   именам полей модели.

        Поведение:
            Обходит список допустимых полей и устанавливает значения атрибутов
            только если они присутствуют в переданном словаре. Это позволяет
            обновлять модель частично, без перезаписи всех полей.
        """

        for field in data:
            if field in VALID_FIELDS:
                setattr(self, field, data[field])
