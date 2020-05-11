from flask import Flask, render_template, request, redirect
import get_page
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
from celery import Celery


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['CELERY_BROKER_URL'] = 'redis://192.168.1.79:6379'
#app.config['CELERY_RESULT_BACKEND'] = 'redis://192.168.1.79:6379'
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379'


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)
#!!!!!необходимо запустить процесс!!!!
#celery -A your_application.celery worker

db = SQLAlchemy(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


class Results(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    taskid = db.Column(db.Integer, unique=False, nullable=True)
    address = db.Column(db.String(300), unique=False, nullable=True)
    words_count = db.Column(db.Integer, unique=False, nullable=True)
    http_status_code = db.Column(db.Integer)

class TaskStatus (enum.Enum):
    NOT_STARTED = 1
    PENDING = 2
    FINISHED = 3

class Tasks(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(300), unique=False, nullable=True)
    timestamp = db.Column(db.DateTime())
    task_status = db.Column(db.Enum(TaskStatus))
    http_status = db.Column(db.Integer)

db.create_all()


@app.route('/')
def hello_world():
    search_results = Tasks.query.all()
    inspect_results = Results.query.all()
    return render_template('index.html', search_results = search_results, inspect_results = inspect_results)


@celery.task
def celery_test(db_url_id, word):
    task = Tasks.query.get(db_url_id)
    task.task_status = 'PENDING'
    db.session.commit()
    path = task.address
    result = get_page.test_func(path, word)
    res = Results(taskid = db_url_id, address = path, words_count = result['total'], http_status_code = result['http_status'])
    db.session.add(res)
    task.task_status = 'FINISHED'
    task.http_status = result['http_status']
    db.session.commit()


@app.route('/add-url', methods=['GET'])
def add_url():
    url = urlparse(request.args['url'])
    path = 'http://'+url.netloc+url.path+url.params+url.query

    #Пишем в базу
    db_url = Tasks(address = path, timestamp = datetime.now(tz=None), task_status = 'NOT_STARTED', http_status = 101)
    db.session.add(db_url)
    db.session.commit()
    #Запуск в бэкграунде
    celery_test.delay(db_url._id,'python')
    return redirect('/')

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0', port = 5000)
