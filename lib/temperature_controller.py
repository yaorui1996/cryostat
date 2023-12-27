import datetime
import logging
import time
from lakeshore import Model336, Model336HeaterRange, Model336InputChannel, Model336HeaterOutputMode, \
    Model336HeaterResistance, Model336HeaterOutputUnits
from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Queue


inst = Model336(ip_address='192.168.30.128')
# print(inst.query('*IDN?'))


# # Output 1
# inst.set_heater_setup(1, heater_resistance=Model336HeaterResistance.HEATER_50_OHM, max_current=1, heater_output=Model336HeaterOutputUnits.POWER)
# inst.set_heater_output_mode(1, mode=Model336HeaterOutputMode.CLOSED_LOOP, channel=Model336InputChannel.CHANNEL_A, powerup_enable=False)
# inst.set_control_setpoint(1, 7)
# inst.set_heater_pid(1, 300, 100, 0)
# inst.set_heater_range(1, Model336HeaterRange.MEDIUM)
# inst.set_heater_range(1, Model336HeaterRange.OFF)


# # Output 2
# inst.set_heater_setup(2, heater_resistance=Model336HeaterResistance.HEATER_50_OHM, max_current=1, heater_output=Model336HeaterOutputUnits.POWER)
# inst.set_heater_output_mode(2, mode=Model336HeaterOutputMode.CLOSED_LOOP, channel=Model336InputChannel.CHANNEL_D, powerup_enable=False)
# inst.set_control_setpoint(2, 8)
# inst.set_heater_pid(2, 300, 100, 0)
# inst.set_heater_range(2, Model336HeaterRange.MEDIUM)
# inst.set_heater_range(2, Model336HeaterRange.OFF)


# # Auto Measure Cooling Capacity
# LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
# logging.basicConfig(filename=f'Cryostat.log', level=logging.INFO, format=LOG_FORMAT)
# logging.getLogger('apscheduler').setLevel(logging.ERROR)
# logging.getLogger('lakeshore').setLevel(logging.ERROR)
# logging.info(f'Temprature Controller Auto Measure Cooling Capacity, Start')
# for i in range(8, 4, -1):
#     inst.set_control_setpoint(2, i)
#     print(datetime.datetime.now(), i)
#     time.sleep(10 * 60)
# logging.info(f'Temprature Controller Auto Measure Cooling Capacity, Stop')
