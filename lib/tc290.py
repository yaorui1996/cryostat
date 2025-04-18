import re
import time
import serial
import serial.tools.list_ports


def find_com_name(serial_number:str) -> str:
    comports_dict = {comport.name:comport.serial_number for comport in serial.tools.list_ports.comports()}
    names = [k for k,v in comports_dict.items() if v == serial_number]
    if names:
        return names[0]
    else:
        raise


class TC290:
    
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
        self.__ser.write(f'{cmd}\r\n'.encode())
        return self.__ser.readline().decode().strip()
    
    def query_idn(self) -> str:
        return self.query('*IDN?')
        
    def query_kelvin_temperature_value(self) -> [str]: # type: ignore
        A, B, C1, D1, C2, D2, C3, D3, C4, D4 = self.query('KRDG?').split(',')
        return A, B, C1, D1, C2, D2, C3, D3, C4, D4
        
    def query_output_parameters(self) -> [str]: # type: ignore
        # output_channel: 1|2
        # mode: 0-5 corresponds to OFF|PID|ZONE|MANU|MONITOR|WARMUP
        # input_channel: 1-10 corresponds to A-D4
        # start_at_boot: 0|1
        output_channel, mode, input_channel, start_at_boot  = self.query('OUTMODE? 1').split(',')
        return output_channel, mode, input_channel, start_at_boot
        
    def query_output_range(self) -> str:
        # output_range: 0-3 corresponds to OFF|LOW|MED|HIGH
        output_range  = self.query('RANGE? 1')
        return output_range
        
    def query_temperature_control_pid_parameters(self) -> [str]: # type: ignore
        p, i, d  = self.query('PID? 1').split(',')
        return p, i, d
    

if __name__ == '__main__':
    
    inst = TC290(com='COM6')
    time.sleep(1)
    for i in range(1):
        t0 = time.time()
        # t1, t6, t2, _, t3, _, t4, _, t5, _ = inst.query_kelvin_temperature_value()
        # print(t1, t2, t3, t4, t5, t6)
        # output_channel, mode, input_channel, start_at_boot = inst.query_output_parameters()
        # print(output_channel, mode, input_channel, start_at_boot)
        # output_range = inst.query_output_range()
        # print(output_range)
        p, i, d = inst.query_temperature_control_pid_parameters()
        print(p, i, d)
        print(time.time() - t0)
    inst.close()
