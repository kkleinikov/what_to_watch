from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from settings import Config

app = Flask(__name__)
app.config.from_object(Config)

# Конфигурация Swagger UI
SWAGGER_URL = '/docs'  # URL, где будет доступна документация
API_URL = '/static/swagger.yaml'  # путь к вашему файлу OpenAPI

# Создаем blueprint для Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "What to Watch API",
        'layout': "BaseLayout"
    }
)

# Регистрируем blueprint
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from opinions_app import api_views, cli_commands, error_handlers, views
