#gunicorn 配置
from gevent import monkey
monkey.patch_all()
import multiprocessing
debug = True
loglevel = 'debug'
bind = '127.0.0.1:5000' # 绑定与Nginx通信的端口
pidfile = 'log/gunicorn.pid'
logfile = 'log/debug.log'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent' # 默认为阻塞模式，最好选择gevent模式


(venv)$ gunicorn -c /www/demo/gconfig.py run:app  #启动命令

# cd到/etc/nginx/的目录下
# 其中nginx.conf文件为主配置文件，可以用来修改其全局配置；
# sites-available存放你的配置文件，但是在这里添加配置是不会应用到Nginx的配置当中，
# 需要软连接到同目录下的sites-enabled当中。但是在我实际操作的过程中中，
# 当我在sites-available修改好配置文件后，会自动更新到sites-enabled。
# 如果没有的话，则需要像上述的操作那样，将修改好的配置文件软链接到sites-enabled当中

server {
        listen 80; # 监听的端口号
        root /www/demo; #Flask的项目目录
        server_name xxx.xx.xxx.xxx; # 你的公网ip或者域名
        location / {
            proxy_set_header x-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            include uwsgi_params;
            uwsgi_pass localhost:8001;
        }
        # 配置static的静态文件：
        location ~ ^\/static\/.*$ {
            root /www/demo; # 注意！这里不需要再加/static了
        }
}

$ nginx -s reload  #重启nginx