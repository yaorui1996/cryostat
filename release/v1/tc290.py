import os
import csv
import time
import serial
import serial.tools.list_ports
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


def find_com_name(serial_number:str) -> str:
    comports_dict = {comport.name:comport.serial_number for comport in serial.tools.list_ports.comports()}
    names = [k for k,v in comports_dict.items() if v == serial_number]
    if names:
        return names[0]
    else:
        raise


class TC290:
    """
    output_channel: 1|2
    mode: 0-5 corresponds to OFF|PID|ZONE|MANU|MONITOR|WARMUP
    input_channel: 1-10 corresponds to A-D4
    start_at_boot: 0|1
    output_range: 0-3 corresponds to OFF|LOW|MED|HIGH
    P: 0.1-1000
    I: 0.1-1000
    D: 0-200
    temperature_control_channel: 1|2
    ch2_output_mode: 0-1 corresponds to Current|Voltage
    heating_resistance_value: 1-2 corresponds to 25|50Ω
    maximum_current: 0-4 corresponds to custom|0.707|1|1.414|2
    maximum_custom_setting_current
    display_mode: 1-2 corresponds to Current|Power
    """
    def __init__(self, serial_number:str=None, com:str=None, baudrate=115200) -> None:
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
        
    def query_control_loop_setpoint(self, output_channel:int) -> str:
        set_value = self.query(f'SETP? {output_channel}')
        return set_value
    
    def set_control_loop_setpoint(self, output_channel:int, set_value:int) -> None:
        self.query(f'SETP {output_channel},{set_value}')
        
    def query_output_parameters(self, output_channel:int) -> [str]: # type: ignore
        mode, input_channel, start_at_boot, _  = self.query(f'OUTMODE? {output_channel}').split(',')
        return mode, input_channel, start_at_boot
    
    def configure_output_parameters(self, output_channel:int, mode:int, input_channel:int, start_at_boot:int) -> None:
        self.query(f'OUTMODE {output_channel},{mode},{input_channel},{start_at_boot}')
        
    def query_output_range(self, output_channel:int) -> str:
        output_range  = self.query(f'RANGE? {output_channel}')
        return output_range
    
    def configure_output_range(self, output_channel:int, output_range:int) -> None:
        self.query(f'RANGE {output_channel},{output_range}')
        
    def query_temperature_control_pid_parameters(self, output_channel:int) -> [str]: # type: ignore
        P, I, D  = self.query(f'PID? {output_channel}').split(',')
        return P, I, D
    
    def configure_temperature_control_pid_parameters(self, output_channel:int, P:int, I:int, D:int) -> None:
        self.query(f'PID? {output_channel},{P},{I},{D}')

    def query_heating_output(self, temperature_control_channel:int) -> str:
        percentage  = self.query(f'HTR? {temperature_control_channel}')
        return percentage
        
    def query_heating_output_parameters(self, temperature_control_channel:int) -> [str]: # type: ignore
        ch2_output_mode, heating_resistance_value, maximum_current, maximum_custom_setting_current, display_mode = self.query(f'HTRSET? {temperature_control_channel}').split(',')
        return ch2_output_mode, heating_resistance_value, maximum_current, maximum_custom_setting_current, display_mode
    
    def configure_heating_output_parameters(self, temperature_control_channel:int, ch2_output_mode:int, heating_resistance_value:int, maximum_current:int, maximum_custom_setting_current:int, display_mode:int) -> None:
        self.query(f'HTRSET {temperature_control_channel},{ch2_output_mode},{heating_resistance_value},{maximum_current},{maximum_custom_setting_current},{display_mode}')


def query(inst:TC290, data_file:str) -> None:
    new_row = [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')]
    new_row += inst.query_kelvin_temperature_value()
    for ch in [1, 2]:
        new_row += [inst.query_control_loop_setpoint(output_channel=ch)]
        new_row += inst.query_output_parameters(output_channel=ch)
        new_row += [inst.query_output_range(output_channel=ch)]
        new_row += inst.query_temperature_control_pid_parameters(output_channel=ch)
        new_row += [inst.query_heating_output(temperature_control_channel=ch)]
        new_row += inst.query_heating_output_parameters(temperature_control_channel=ch)
    print(new_row)
    with open(data_file, 'a', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(new_row)
    

if __name__ == '__main__':
    data_file = '_data_tc290.csv'
    
    columns = [
        'Time',
        'A', 'B', 'C1', 'D1', 'C2', 'D2', 'C3', 'D3', 'C4', 'D4',
        'LP1_SET_VALUE',
        'MODE', 'INPUT_CHANNEL', 'START_AT_BOOT',
        'OUTPUT_RANGE',
        'P', 'I', 'D',
        'PERCENTAGE',
        'CH2_OUTPUT_MODE', 'HEATING_RESISTANCE_VALUE', 'MAXIMUM_CURRENT', 'MAXIMUM_CUSTOM_SETTING_CURRENT', 'DISPLAY_MODE',
        'LP2_SET_VALUE',
        'MODE', 'INPUT_CHANNEL', 'START_AT_BOOT',
        'OUTPUT_RANGE',
        'P', 'I', 'D',
        'PERCENTAGE',
        'CH2_OUTPUT_MODE', 'HEATING_RESISTANCE_VALUE', 'MAXIMUM_CURRENT', 'MAXIMUM_CUSTOM_SETTING_CURRENT', 'DISPLAY_MODE',
    ]

    if not os.path.exists(data_file):
        with open(data_file, 'w', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow(columns)
    
    inst = TC290(com='COM6')
    time.sleep(1)
    # inst.configure_output_parameters(output_channel=1, mode=1, input_channel=1, start_at_boot=1)
    # inst.configure_output_range(output_channel=1, output_range=0)
    # inst.set_control_loop_setpoint(output_channel=1, set_value=300)
    
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
