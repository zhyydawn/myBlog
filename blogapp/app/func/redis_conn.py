from redis import StrictRedis
REDIS_HOST='localhost'
REDIS_PORT=6379
# REDIS_PASSWORD='root123'

r_db =StrictRedis(host=REDIS_HOST,
                   port=REDIS_PORT,
                   password=None,
                   decode_responses=True,   # decode_responses=True，写入value中为str类型，否则为字节型
                   db='1')                  # 默认不写是db0


