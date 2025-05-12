import csv
import os
import time
import snap7
import struct
from snap7.type import Areas
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


def check_setpoint_range(min_val: float, max_val: float):
    def decorator(func):
        def wrapper(self, val: float, *args, **kwargs):
            if min_val <= val <= max_val:
                return func(self, val, *args, **kwargs)
        return wrapper
    return decorator


class PLC():

    def __init__(self, ip: str, rack: int = 0, slot: int = 1) -> None:
        self.__client = snap7.client.Client()
        self.__client.connect(address=ip, rack=rack, slot=slot)

    def close(self) -> None:
        self.__client.disconnect()
        
    def get_sv1(self) -> int:
        Q0 = struct.unpack('b', self.__client.read_area(Areas.PA, 0, 0, 1))[0]
        return 1 if Q0 & 1 else 0

    def get_sv2(self) -> int:
        Q0 = struct.unpack('b', self.__client.read_area(Areas.PA, 0, 0, 1))[0]
        return 1 if Q0 >> 1 & 1 else 0
    
    def switch_sv1(self) -> None:
        M2 = struct.unpack('b', self.__client.read_area(Areas.MK, 0, 2, 1))[0]
        # rising edge trigger, set M2.0 to 0 -> 1 -> 0
        self.__client.write_area(Areas.MK, 0, 2, bytearray(struct.pack('b', M2 & ~1)))
        self.__client.write_area(Areas.MK, 0, 2, bytearray(struct.pack('b', M2 | 1)))
        self.__client.write_area(Areas.MK, 0, 2, bytearray(struct.pack('b', M2 & ~1)))
    
    def switch_sv2(self) -> None:
        M2 = struct.unpack('b', self.__client.read_area(Areas.MK, 0, 2, 1))[0]
        # rising edge trigger, set M2.1 to 0 -> 1 -> 0
        self.__client.write_area(Areas.MK, 0, 2, bytearray(struct.pack('b', M2 & ~(1 << 1))))
        self.__client.write_area(Areas.MK, 0, 2, bytearray(struct.pack('b', M2 | (1 << 1))))
        self.__client.write_area(Areas.MK, 0, 2, bytearray(struct.pack('b', M2 & ~(1 << 1))))
    
    def set_sv1(self, val:int) -> None:
        if val in (0, 1) and not self.get_sv1() == val:
            self.switch_sv1()
    
    def set_sv2(self, val:int) -> None:
        if val in (0, 1) and not self.get_sv2() == val:
            self.switch_sv2()

    def get_p01(self) -> float:
        MD116 = struct.unpack('>f', self.__client.read_area(Areas.MK, 0, 116, 4))[0]
        return MD116

    def get_setpoint_a(self) -> float:
        MD100 = struct.unpack('>f', self.__client.read_area(Areas.MK, 0, 100, 4))[0]
        return MD100

    def get_setpoint_b(self) -> float:
        MD104 = struct.unpack('>f', self.__client.read_area(Areas.MK, 0, 104, 4))[0]
        return MD104

    def get_setpoint_c(self) -> float:
        MD108 = struct.unpack('>f', self.__client.read_area(Areas.MK, 0, 108, 4))[0]
        return MD108

    def get_setpoint_d(self) -> float:
        MD112 = struct.unpack('>f', self.__client.read_area(Areas.MK, 0, 112, 4))[0]
        return MD112

    def get_t1(self) -> float:
        MD124 = struct.unpack('>f', self.__client.read_area(Areas.MK, 0, 124, 4))[0]
        return MD124

    @check_setpoint_range(0, 300)  # unit is K
    def set_setpoint_a(self, val: float) -> None:
        self.__client.write_area(Areas.MK, 0, 100, bytearray(struct.pack('>f', val)))

    @check_setpoint_range(0, 1.068)  # unit is bar
    def set_setpoint_b(self, val: float) -> None:
        self.__client.write_area(Areas.MK, 0, 104, bytearray(struct.pack('>f', val)))

    @check_setpoint_range(0, 1.068)  # unit is bar
    def set_setpoint_c(self, val: float) -> None:
        self.__client.write_area(Areas.MK, 0, 108, bytearray(struct.pack('>f', val)))

    @check_setpoint_range(0, 1.068)  # unit is bar
    def set_setpoint_d(self, val: float) -> None:
        self.__client.write_area(Areas.MK, 0, 112, bytearray(struct.pack('>f', val)))

    def set_t1(self, val: float) -> None:
        self.__client.write_area(Areas.MK, 0, 124, bytearray(struct.pack('>f', val)))

    def get_manual_or_auto(self) -> int:
        M3 = struct.unpack('b', self.__client.read_area(Areas.MK, 0, 3, 1))[0]
        return 1 if M3 & 1 else 0

    def set_manual_or_auto(self, val: int) -> None:
        # manual = 0, auto = 1
        if val in (0, 1):
            self.__client.write_area(Areas.MK, 0, 3, bytearray(struct.pack('b', val)))


def query(inst: PLC, data_file: str) -> None:
    new_row = [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')]
    
    sv1 = inst.get_sv1()
    sv2 = inst.get_sv2()
    manual_or_auto = inst.get_manual_or_auto()
    p01 = inst.get_p01()
    setpoint_a = inst.get_setpoint_a()
    setpoint_b = inst.get_setpoint_b()
    setpoint_c = inst.get_setpoint_c()
    setpoint_d = inst.get_setpoint_d()
    t1 = inst.get_t1()
    
    new_row += [sv1, sv2, manual_or_auto, p01]
    new_row += [setpoint_a, setpoint_b, setpoint_c, setpoint_d, t1]
    
    print(new_row)
    with open(data_file, 'a', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(new_row)


if __name__ == '__main__':
    data_file = '_data_plc.csv'
    
    columns = [
        'Time',
        'SV1', 'SV2', 'MANUAL_OR_AUTO', 'P1(bar)',
        'SETPOINT_A(K)', 'SETPOINT_B(bar)', 'SETPOINT_C(bar)', 'SETPOINT_D(bar)', 'T1(K)'
    ]

    if not os.path.exists(data_file):
        with open(data_file, 'w', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow(columns)
    
    inst = PLC(ip='192.168.21.10')
    
    """参数设置区域开始"""
    inst.set_setpoint_a(300)
    inst.set_setpoint_b(1.01)
    inst.set_setpoint_c(1.02)
    inst.set_setpoint_d(1.03)
    inst.set_t1(299)
    inst.set_manual_or_auto(1)
    """参数设置区域结束"""

    next_whole_second = (datetime.now() + timedelta(seconds=1)).replace(microsecond=0)
    sched = BackgroundScheduler()
    sched.add_job(query, 'interval', seconds=1, start_date=next_whole_second, args=[inst, data_file])
    sched.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sched.shutdown(wait=True)
        inst.close()
        print("\n检测到 Ctrl+C，程序退出。")
