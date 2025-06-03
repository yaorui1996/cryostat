import time
import serial
import serial.tools.list_ports
import numpy as np
from matplotlib import pyplot as plt


def find_com_name(serial_number:str) -> str:
    comports_dict = {comport.name:comport.serial_number for comport in serial.tools.list_ports.comports()}
    names = [k for k,v in comports_dict.items() if v == serial_number]
    if names:
        return names[0]
    else:
        raise


def notch_search(frq: list[float], s11: list[float]) -> (float, float, float, float, float, float):
    max, argmax = np.max(s11), np.argmax(s11)
    min, argmin = np.min(s11), np.argmin(s11)
    l_argmin = np.argmin(np.abs(s11[: argmin] - (max - 3)))
    r_argmin = np.argmin(np.abs(s11[argmin:] - (max - 3))) + argmin
    
    center, s11_center = frq[argmin], min
    center_left_3db, s11_left_3db = frq[l_argmin], s11[l_argmin]
    center_right_3db, s11_right_3db = frq[r_argmin], s11[r_argmin]
    frq_s11_max, s11_max = frq[argmax], max
    
    return center, s11_center, center_left_3db, s11_left_3db, center_right_3db, s11_right_3db, frq_s11_max, s11_max


class DeepVNA:
    
    def __init__(self,  serial_number:str = None, com:str = None, baudrate = 115200) -> None:
        if serial_number:
            port = find_com_name(serial_number)
        elif com:
            port = com
        else:
            raise
        self.__ser = serial.Serial(port=port, baudrate=baudrate)
        self.__ser.timeout = 0
        self.init_dev()
    
    def close(self) -> None:
        self.__ser.close()
        
    def query(self, cmd: str) -> str:
        self.__ser.write(f'{cmd}\r'.encode())
        time.sleep(0.001)
        recv = self.__ser.read(1024).decode('utf-8')
        while not recv.endswith('ch> '):
            time.sleep(0.01)
            recv += self.__ser.read(1024).decode('utf-8')
        res = recv.replace(f'{cmd}\r\n', '').replace('ch> ', '')
        return res
    
    def init_dev(self) -> None:
        self.query('trace 0 logmag 0')
        self.query('trace 1 off')
        self.query('trace 2 off')
        self.query('trace 3 off')
        
    def sweep(self, center: float, span: float, points: int = 301) -> None:
        start = center - span / 2
        stop = center + span / 2
        self.query(f'sweep {start} {stop} {points}')
    
    def sweep_once(self, sampling_time: float = 2) -> None:
        self.query('resume')
        time.sleep(sampling_time)
        self.query('pause')
    
    def frequencies(self) -> list[float]:
        res = self.query('frequencies')
        return [float(x) for x in res.split('\r\n')[:-1]]
    
    def data0(self) -> list[list[float, float]]:
        res = self.query('data 0')
        return [[float(y) for y in x.split(' ')] for x in res.split('\r\n')[:-1]]
        

if __name__ == '__main__':
    deepvna = DeepVNA(serial_number='6561E2CB0E32')
    deepvna.sweep(400e6, 200e6)
    frq = deepvna.frequencies()
    s11 = [20 * np.log10(np.linalg.norm(x)) for x in deepvna.data0()]
    deepvna.close()
    
    center, s11_center, center_left_3db, s11_left_3db, center_right_3db, s11_right_3db, frq_s11_max, s11_max = notch_search(frq, s11)
    reflect = s11_center - s11_max
    quality = center / (center_right_3db - center_left_3db)
    print(center, reflect, quality)
    
    plt.plot([x * 1e-6 for x in frq], s11)
    plt.plot(center * 1e-6, s11_center, 'o')
    plt.plot(center_left_3db * 1e-6, s11_left_3db, 'o')
    plt.plot(center_right_3db * 1e-6, s11_right_3db, 'o')
    plt.plot(frq_s11_max * 1e-6, s11_max, 'o')
    plt.xlabel('Frq (MHz)')
    plt.ylabel('S11 (dB)')
    plt.show()
    