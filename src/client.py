#!/usr/bin/env python3

import os, sys, re
import socket as sock
sys.path.append("../lib")  # for params, IO, and tar
import framedIO

defaultAddress = "127.0.0.1"
defaultPort = 6767

for res in sock.getaddrinfo(defaultAddress, defaultPort):

    af, sockType, protocol, cname, socketAddr = res

    print(sockType)



