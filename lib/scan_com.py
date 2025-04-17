from serial.tools import list_ports


comports_dict = {comport.name:comport.serial_number for comport in list_ports.comports()}
for k,v in comports_dict.items():
    print(k, v)

print('-'*16)
for comport in list_ports.comports():
    print(comport.__dict__)
