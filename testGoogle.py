# coding: utf8


import threading
import time
import datetime
import socket
import ssl

# import socketserver
# from io import StringIO, BytesIO
# import struct
# import threading
# import redis
# import json


# pool来管理对一个redis server的所有连接，避免每次建立、释放连接的开销
# 加上 decode_responses=True，写入的键值对中的value为str类型，不加这个参数写入的则为字节类型。
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASS = ''
MAX_CONNECTIONS = 10000
DECODE_RESPONSES = False
REDIS_PRIFIX = 'domains'    # Redis name 前缀

# def getFromRedis(name, key):
#     pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,password=REDIS_PASS,
#                                 max_connections=MAX_CONNECTIONS, decode_responses=DECODE_RESPONSES)
#     db = redis.Redis(connection_pool=pool)
#     result = db.hget(name, key)
#     if result is not None:  # 是否有值
#         result = json.loads(result)  # 转换成字典
#         if result['is_ssl']:  # 是否有证书, 如有证书，返回证书信息
#             cert, key = result['ssl']['cert'], result['ssl']['key']
#             return cert, key
#         return False, {'msg': 'SSL is not turned on.'}
#     return False, {'msg': 'This domain Not Found.'}

        
# r1, r2 = getFromRedis(name=REDIS_PRIFIX, key="2.com")

# if not r1:
#     print(json.dumps({
#         'code': 200,
#         'msg': r2['msg'],
#         'data': ''
#     }))

# print(True)


def pipe(sock_in, sock_out):
    try:
        while True:
            b = sock_in.recv(65536)
            if not b:
                break
            sock_out.sendall(b)
    except socket.error:
        pass
    finally:
        time.sleep(1)
        sock_in.close()
        sock_out.close()


def connecting(cli_sock, _):
    cli_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)
    httpd_sock = socket.socket()
    

    try:
        httpd_sock.connect(('336.se', 443))
    except socket.error:
        cli_sock.close()
        return
    httpd_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    threading.Thread(target=pipe, args=(cli_sock, httpd_sock)).start()
    pipe(httpd_sock, cli_sock)


def main():
    serv_sock = socket.socket()
    serv_sock.bind(('0.0.0.0', 444))
    serv_sock.listen(50)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
    serv_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    while True:
        threading.Thread(target=connecting, args=serv_sock.accept()).start()


if __name__ == '__main__':
    main()
