#!/usr/bin/env python
import os,sys
# from celery import Celery
from flask import g
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

# sys.path.append(os.path.dirname(sys.path[0]))
from app import create_app, db


# def make_celery(app):
#     celery_app = Celery('genbu_job',broker=app.config['CELERY_BROKER'],include=['tasks.ci_tasks'])
#     celery_app.config.timezone ='Asia/Shanghai'
#     celery_app.config.task_routes={
#         'ci_task.*':{'queue':'ci_queue'},
#         'cd_task.*':{'queue':'cd_queue'},
#         'sync_task.*':{'queue':'sync_queue'}
#     }
#     TaskBase = celery_app.Task
#     class ContexTask(TaskBase):
#         abstract = True

#         def __call__(self,*args,**kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self,*args,**kwargs)
#     celery_app.Task = ContexTask
#     return celery_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# #celery
# create_app = make_celery(app)
# #路由
# from app.urls import create_router
# create_router(app)


#插入脚本
# manager = Manager(app)
# migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


# manager.add_command("shell", Shell(make_context=make_shell_context))
# manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # print(g.user_id,g.username)
    # manager.run()
    # print(app.url_map)
    app.run()
    
