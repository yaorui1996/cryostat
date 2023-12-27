import socket
from matplotlib import pyplot as plt
import numpy as np
import time


class DL7:
    
    def __init__(self, ip: str = '192.168.30.131') -> None:
        self.__ip = ip
        self.__client = socket.socket()
        self.__client.connect((self.__ip, 8234))
        self.__recv_cache = b''  # len = 14, fmt = N.N  E - N Pa\r
        self.init_recv_cache()
    
    def close(self) -> None:
        self.__client.close()
        
    def init_recv_cache(self) -> None:  # deal with first data is incomplete
        time.sleep(1)
        self.__recv_cache += self.__client.recv(256)
        term_pos = self.__recv_cache.find(b'\r')
        if term_pos not in (-1, 13):
            self.__recv_cache = self.__recv_cache[term_pos+1:]

    def get_pressure(self) -> str:  # unit is Pa
        self.__recv_cache += self.__client.recv(256)
        last_term_pos = self.__recv_cache.rfind(b'\r')
        if not last_term_pos == -1:
            last_data = self.__recv_cache[last_term_pos-13:last_term_pos+1]
            pressure = last_data[:-3].decode().replace(' ', '')
            self.__recv_cache = self.__recv_cache[last_term_pos+1:]
            return pressure
        else:
            return '0'


if __name__ == '__main__':
    dl7 = DL7()
    print(dl7.get_pressure())
    dl7.close()