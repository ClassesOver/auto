"""Advanced example using other configuration options."""

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



class Config:
    """App configuration."""
    
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    
    SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)}
    
    SCHEDULER_EXECUTORS = {"default": {"type": "threadpool", "max_workers": 1}}
    
    SCHEDULER_JOB_DEFAULTS = {"coalesce": False, "max_instances": 1}
    
    SCHEDULER_API_ENABLED = True


app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app)
scheduler = APScheduler()
scheduler.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)


if __name__ == "__main__":
    scheduler.start()
    from cron.zqsb import zqsb
    app.register_blueprint(zqsb, url_prefix="/zqsb")
    app.run()
