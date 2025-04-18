import re
import serial
import serial.tools.list_ports


def find_com_name(serial_number:str) -> str:
    comports_dict = {comport.name:comport.serial_number for comport in serial.tools.list_ports.comports()}
    names = [k for k,v in comports_dict.items() if v == serial_number]
    if names:
        return names[0]
    else:
        raise


class IonGauge:
    
    def __init__(self, serial_number:str=None, com:str=None, baudrate=9600) -> None:
        if serial_number:
            port = find_com_name(serial_number)
        elif com:
            port = com
        else:
            raise
        self.__ser = serial.Serial(port=port, baudrate=baudrate)
        self.__ser.timeout = 0.5

    def close(self) -> None:
        self.__ser.close()
    
    def query(self, cmd:str) -> str:
        self.__ser.write(f'{cmd}\r'.encode())
        recv = self.__ser.readline().decode()
        res = re.compile(r'>(\S+)\r').findall(recv)
        return res[0] if res else ''
        
    def read_emission_status(self) -> int:
        return 1 if self.query('#0032UHFIG1') == '01' else 0
        
    def read_pressure(self) -> str:
        return self.query('#0002UHFIG1')
        
    def set_emission_off(self) -> None:
        self.query('#0030UHFIG1')
        
    def set_fil_1_emission_on(self) -> None:
        self.query('#0031UHFIG1')
        
    def set_fil_2_emission_on(self) -> None:
        self.query('#0033UHFIG1')
    

if __name__ == '__main__':
    
    inst = IonGauge(serial_number='AYDPE11BS13')
    print(inst.read_emission_status())
    print(inst.read_pressure())
