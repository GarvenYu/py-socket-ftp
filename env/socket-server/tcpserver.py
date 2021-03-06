#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import select
import logging
import time
import os

logging.basicConfig(level=logging.INFO,
                    filename='server_connect.log',
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )
IMG_DIRECTORY = '/home/freesia_blog_edition2/env/app/blogimg/'+time.strftime('%Y%m%d',time.localtime(time.time()))+'/'
DOMAIN_NAME = 'http://resource.fre3sia.site'


class TcpServer(object):

    def __init__(self, host, port, conn_num, time_out, buf_size):
        """
        初始化TcpServer类
        :param host: 主机
        :param port: 端口
        :param conn_num: 最大连接数
        :param time_out: 超时时间
        :param buf_size: 缓冲区大小
        """
        self.host = host
        self.port = port
        self.conn_num = conn_num
        self.time_out = time_out
        self.buf_size = buf_size
        self.img_url = ''

    def start_server(self):
        server_socket = socket.socket()
        server_socket.bind((self.host, self.port))
        server_socket.setblocking(False)
        server_socket.listen(5)
        epoll = select.epoll()
        epoll.register(server_socket.fileno(), select.EPOLLIN)
        fd_to_socket = {server_socket.fileno(): server_socket}
        while True:
            logging.info("等待连接...")
            # 轮询注册的事件集合，返回值为[(文件句柄，对应的事件)，(...),....]
            events = epoll.poll(self.time_out)
            if not events:
                logging.info("无事件发生,重新轮询...")
                continue
            logging.info("有"+str(len(events))+"个事件发生,开始处理...")
            # 进行处理
            for fd, event in events:
                event_socket = fd_to_socket.get(fd)
                if event_socket == server_socket:
                    # 有新连接
                    conn, address = server_socket.accept()
                    logging.info("新连接："+str(address))
                    # conn.setblocking(False)
                    epoll.register(conn.fileno(), select.EPOLLIN)
                    fd_to_socket[conn.fileno()] = conn
                # elif event & select.EPOLLHUP:
                #     # 文件描述符关闭
                #     logging.info("客户端关闭")
                #     epoll.unregister(fd)
                #     fd_to_socket[fd].close()
                #     del fd_to_socket[fd]
                elif event & select.EPOLLIN:
                    # 文件描述符可读(对端数据传入)
                    # 文件大小
                    # file_size = event_socket.recv(self.buf_size)
                    # logging.info("文件大小 %d" % int(file_size.decode('UTF-8')))
                    recv_size = 0
                    file_name = str(int(time.time())) + '.jpg'
                    if not os.path.exists(IMG_DIRECTORY): 
                        # 目录不存在
                        os.mkdir(IMG_DIRECTORY)    
                    file_path = IMG_DIRECTORY + file_name
                    with open(file_path, mode='wb+') as file:
                        while True:
                            # 文件数据二进制
                            data = event_socket.recv(self.buf_size)
                            recv_size += len(data)
                            file.write(data)
                            if len(data) < self.buf_size:  # 客户端传finish
                                # 接收完毕
                                break
                    logging.info("上传完成。文件路径 %s, 接收大小 %d" % (file_path, recv_size))
                    self.img_url = DOMAIN_NAME + '/blogimg/'+time.strftime('%Y%m%d',time.localtime(time.time()))+'/'+ file_name
                    epoll.modify(fd, select.EPOLLOUT)
                elif event & select.EPOLLOUT:
                    # 文件描述符可写
                    # 返回资源在服务器的地址
                    # 关闭连接
                    event_socket.send(self.img_url.encode(encoding='UTF-8'))
                    logging.info("回传图片地址 %s 到客户端 %s." % (self.img_url, event_socket.getpeername()))
                    logging.info("服务端关闭连接..")
                    epoll.unregister(fd)
                    fd_to_socket[fd].close()
                    del fd_to_socket[fd]
        self.stop_server(server_socket, epoll)

    @staticmethod
    def stop_server(server_socket, epoll):
        epoll.unregister(server_socket.fileno())
        epoll.close()
        server_socket.close(server_socket.fileno())


tcpServer = TcpServer('172.18.107.169', 8001, 10, 10, 4096)
tcpServer.start_server()