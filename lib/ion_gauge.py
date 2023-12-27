import re
import time
import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def query(cmd):
    inst.send(f'{cmd}\r'.encode())
    time.sleep(0.1)
    recv = inst.recv(1024).decode()
    res = re.compile(r'>(\S+)\r').findall(recv)
    # res = re.compile(r'>(\d+\.*\d*[eE][-+]?\d+)\r').findall(recv)
    return res[0] if res else ''


instrument_ip = '192.168.30.129'
inst = socket.socket()
inst.connect((instrument_ip, 4001))
# print(query('#0030UHFIG1'))  # Set Emission OFF
# print(query('#0031UHFIG1'))  # Set Emission ON (Fil 1)
# print(query('#0033UHFIG1'))  # Set Emission ON (Fil 2)
print(query('#0032UHFIG1'))  # Read Emission status
print(query('#0002UHFIG1'))  # Read Pressure
inst.close()

