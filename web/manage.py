#!/usr/bin/env python

from app import create_app
from flask_migrate import MigrateCommand
from flask_script import Command, Manager
from tasks import run_celery

manager = Manager(create_app)
manager.add_option("-c", "--config", dest="config_file", required=False)
manager.add_command("db", MigrateCommand)
manager.add_command("runcelery", Command(run_celery))

if __name__ == "__main__":
    manager.run()
