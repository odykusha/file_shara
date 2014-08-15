from flask.ext.script import Manager
from file_shara import app
import config

HOST_IP = config.HOST_IP
HOST_PORT = config.HOST_PORT
DEBUG = config.DEBUG

manager = Manager(app)


@manager.command
def run():
    "RUN APP"
    print('command: SERVER RUNNING')
    app.run(host=HOST_IP,
            port=HOST_PORT)

@manager.command
def stop():
    "STOP APP"
    print("command: SERVER STOPED")
    try:
        del(app)
    except UnboundLocalError:
        print("NOT FOUND RUNNING APP, try again")

@manager.command
def hello(name):
    "say HELLO to my friend"
    return 'HELLO %s' % name


if __name__ == '__main__':
    manager.run()