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
        
    def query_output_parameters(self, output_channel:int) -> [str]: # type: ignore
        mode, input_channel, start_at_boot  = self.query(f'OUTMODE? {output_channel}').split(',')
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
        self.query(f'PID {output_channel},{P},{I},{D}')

    def query_heating_output(self, temperature_control_channel:int) -> str:
        percentage  = self.query(f'HTR? {temperature_control_channel}')
        return percentage
        
    def query_heating_output_parameters(self, temperature_control_channel:int) -> [str]: # type: ignore
        ch2_output_mode, heating_resistance_value, maximum_current, maximum_custom_setting_current, display_mode = self.query(f'HTRSET? {temperature_control_channel}').split(',')
        return ch2_output_mode, heating_resistance_value, maximum_current, maximum_custom_setting_current, display_mode
    
    def configure_heating_output_parameters(self, temperature_control_channel:int, ch2_output_mode:int, heating_resistance_value:int, maximum_current:int, maximum_custom_setting_current:int, display_mode:int) -> None:
        self.query(f'HTRSET {temperature_control_channel},{ch2_output_mode},{heating_resistance_value},{maximum_current},{maximum_custom_setting_current},{display_mode}')
        
    def query_control_loop_setpoint(self, output_channel:int) -> str:
        set_value = self.query(f'SETP? {output_channel}')
        return set_value
    
    def set_control_loop_setpoint(self, output_channel:int, set_value:int) -> None:
        self.query(f'SETP {output_channel},{set_value}')


if __name__ == '__main__':
    inst = TC290(com='COM9')
    time.sleep(1)
    for i in range(1):
        t0 = time.time()
        # print(inst.query_idn())
        # t1, t6, t2, _, t3, _, t4, _, t5, _ = inst.query_kelvin_temperature_value()
        # print(t1, t2, t3, t4, t5, t6)
        # inst.configure_output_parameters(output_channel=1, mode=1, input_channel=1, start_at_boot=1)
        # inst.configure_output_parameters(output_channel=2, mode=1, input_channel=5, start_at_boot=1)
        # mode, input_channel, start_at_boot = inst.query_output_parameters(output_channel=1)
        # print(1, mode, input_channel, start_at_boot)
        # mode, input_channel, start_at_boot = inst.query_output_parameters(output_channel=2)
        # print(2, mode, input_channel, start_at_boot)
        # inst.configure_output_range(output_channel=1, output_range=0)
        # output_range = inst.query_output_range(output_channel=1)
        # print(1, output_range)
        # inst.configure_output_range(output_channel=2, output_range=0)
        # output_range = inst.query_output_range(output_channel=2)
        # print(2, output_range)
        # inst.configure_temperature_control_pid_parameters(output_channel=1, P=50, I=20, D=0)
        # inst.configure_temperature_control_pid_parameters(output_channel=2, P=50, I=20, D=0)
        # P, I, D = inst.query_temperature_control_pid_parameters(output_channel=1)
        # print(1, P, I, D)
        # P, I, D = inst.query_temperature_control_pid_parameters(output_channel=2)
        # print(2, P, I, D)
        # percentage = inst.query_heating_output(temperature_control_channel=1)
        # print(percentage)
        # inst.configure_heating_output_parameters(temperature_control_channel=1, ch2_output_mode=0, heating_resistance_value=2, maximum_current=2, maximum_custom_setting_current=1, display_mode=2)
        # inst.configure_heating_output_parameters(temperature_control_channel=2, ch2_output_mode=0, heating_resistance_value=2, maximum_current=2, maximum_custom_setting_current=1, display_mode=2)
        # ch2_output_mode, heating_resistance_value, maximum_current, maximum_custom_setting_current, display_mode = inst.query_heating_output_parameters(temperature_control_channel=2)
        # print(ch2_output_mode, heating_resistance_value, maximum_current, maximum_custom_setting_current, display_mode)
        # inst.set_control_loop_setpoint(output_channel=1, set_value=300)
        # set_value = inst.query_control_loop_setpoint(output_channel=1)
        # print(set_value)
        print(time.time() - t0)
    inst.close()
    
