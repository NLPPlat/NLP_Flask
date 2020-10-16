from app import *

app = create_app("development")
celery = create_celery(app)
register_blueprint(app)

if __name__ == '__main__':
    app.run()
