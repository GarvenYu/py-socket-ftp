#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import select

class TcpServer(object):

    def __init__(self, host, port, conn_num, time_out):
        """
        初始化TcpServer类
        :param host: 主机
        :param port: 端口
        :param conn_num: 最大连接数
        :param time_out: 超时时间
        """
        self.host = host
        self.port = port
        self.conn_num = conn_num
        self.time_out = time_out

    def start_server(self):
        server_socket = socket.socket()
        server_socket.bind((self.host, self.port))
        server_socket.setblocking(False)
        server_socket.listen(5)
        epoll = select.epoll()
        epoll.register(server_socket.fileno(), select.EPOLLIN)
        fd_to_socket = {server_socket.fileno() : server_socket}
        # 打印日志
        while True:
            # 打印日志
            # 轮询注册的事件集合，返回值为[(文件句柄，对应的事件)，(...),....]
            events = epoll.poll(self.time_out)
            if not events:
                # 打印日志
                continue
            # 打印日志
            # 进行处理
            for fd, event in events:
                pass


tcpServer = TcpServer('', 8001, 10, 10)
tcpServer.start_server()