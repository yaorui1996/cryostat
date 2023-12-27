import snap7
import struct
from snap7.util import Areas


rack = 0
slot = 1
P_MAX = 1.068  # unit is bar


class HeliumStabilizer():

    def __init__(self, ip='192.168.30.130') -> None:
        self.__ip = ip
        self.__client = snap7.client.Client()
        self.reconnect()

    def close(self) -> None:
        self.__client.disconnect()
    
    def reconnect(self) -> None:
        self.close()
        self.__client.connect(self.__ip, rack=rack, slot=slot)
        
    def get_sv1(self) -> int:
        try:
            M2 = struct.unpack(
                'b', self.__client.read_area(Areas.MK, 0, 2, 1))[0]
            return 1 if M2 & 1 else 0
        except RuntimeError:
            self.reconnect()
            return -1

    def get_sv2(self) -> int:
        try:
            M2 = struct.unpack(
                'b', self.__client.read_area(Areas.MK, 0, 2, 1))[0]
            return 1 if M2 >> 1 & 1 else 0
        except RuntimeError:
            self.reconnect()
            return -1

    def get_pressure_1(self) -> float:
        try:
            MD116 = struct.unpack(
                '>f', self.__client.read_area(Areas.MK, 0, 116, 4))[0]
            return round(MD116, 6)
        except RuntimeError:
            self.reconnect()
            return -1

    def get_setpoint_a(self) -> float:
        try:
            MD100 = struct.unpack(
                '>f', self.__client.read_area(Areas.MK, 0, 100, 4))[0]
            return round(MD100, 4)
        except RuntimeError:
            self.reconnect()
            return -1

    def get_setpoint_b(self) -> float:
        try:
            MD104 = struct.unpack(
                '>f', self.__client.read_area(Areas.MK, 0, 104, 4))[0]
            return round(MD104, 4)
        except RuntimeError:
            self.reconnect()
            return -1

    def get_setpoint_c(self) -> float:
        try:
            MD108 = struct.unpack(
                '>f', self.__client.read_area(Areas.MK, 0, 108, 4))[0]
            return round(MD108, 4)
        except RuntimeError:
            self.reconnect()
            return -1

    def get_compare_period(self) -> int:
        try:
            MD112 = struct.unpack(
                '>i', self.__client.read_area(Areas.MK, 0, 112, 4))[0]  # unit is ms
            return MD112
        except RuntimeError:
            self.reconnect()
            return -1

    def get_manual_or_auto(self) -> int:
        try:
            M3 = struct.unpack(
                'b', self.__client.read_area(Areas.MK, 0, 3, 1))[0]
            return 1 if M3 == 5 else 0
        except RuntimeError:
            self.reconnect()
            return -1

    def set_sv1(self, val: int) -> None:
        M2 = struct.unpack('b', self.__client.read_area(Areas.MK, 0, 2, 1))[0]
        if val == 1:
            M2 = M2 | 1
        elif val == 0:
            M2 = M2 & ~1
        self.__client.write_area(
            Areas.MK, 0, 2, bytearray(struct.pack('b', M2)))

    def set_sv2(self, val: int) -> None:
        M2 = struct.unpack('b', self.__client.read_area(Areas.MK, 0, 2, 1))[0]
        if val == 1:
            M2 = M2 | (1 << 1)
        elif val == 0:
            M2 = M2 & ~(1 << 1)
        self.__client.write_area(
            Areas.MK, 0, 2, bytearray(struct.pack('b', M2)))

    def set_setpoint_a(self, val: float) -> None:
        if 0 <= val <= P_MAX:
            self.__client.write_area(
                Areas.MK, 0, 100, bytearray(struct.pack('>f', val)))

    def set_setpoint_b(self, val: float) -> None:
        if 0 <= val <= P_MAX:
            self.__client.write_area(
                Areas.MK, 0, 104, bytearray(struct.pack('>f', val)))

    def set_setpoint_c(self, val: float) -> None:
        if 0 <= val <= P_MAX:
            self.__client.write_area(
                Areas.MK, 0, 108, bytearray(struct.pack('>f', val)))

    def set_compare_period(self, val: int) -> None:
        if val >= 0:
            self.__client.write_area(
                Areas.MK, 0, 112, bytearray(struct.pack('>i', val)))

    def set_manual_or_auto(self, val: int) -> None:
        M3 = struct.unpack('b', self.__client.read_area(Areas.MK, 0, 3, 1))[0]
        if val == 1:
            M3 = 5
        elif val == 0:
            M3 = 2
        self.__client.write_area(
            Areas.MK, 0, 3, bytearray(struct.pack('b', M3)))


if __name__ == '__main__':
    instrument_ip = '192.168.30.130'
    hs = HeliumStabilizer(instrument_ip)
    print(hs.get_pressure_1())
    print(hs.get_sv1())
    print(hs.get_sv2())

    # hs.set_manual_or_auto(1)  # Auto
    # hs.set_manual_or_auto(0)  # Manual
