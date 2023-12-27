import ctypes
import logging
import numpy as np
from lakeshore import Model336
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from lib.data import recompress, save


instrument_ip = '192.168.30.128'
task = 'Cryostat'
name = 'Temprature Controller'
interval = 1  # unit is s
plot_interval = 5  # unit is s
cache_num = 600
path = '.'
plot_data = True
columns = [
    'Time',
    'T_A(K)', 'T_B(K)', 'T_C(K)', 'T_D1(K)', 'T_D2(K)', 'T_D3(K)',
    'OUTPUT 1 INPUT CHANNEL', 'OUTPUT 1 SETPOINT(K)',
    'OUTPUT 1 P', 'OUTPUT 1 I', 'OUTPUT 1 D',
    'OUTPUT 1 HEATER RANGE', 'OUTPUT 1 HEATER OUTPUT 1(%)',
    'OUTPUT 1 RESISTANCE', 'OUTPUT 1 MAX CURRENT(A)', 'OUTPUT 1 DISPLAY MODE',
    'OUTPUT 2 INPUT CHANNEL', 'OUTPUT 2 SETPOINT(K)',
    'OUTPUT 2 P', 'OUTPUT 2 I', 'OUTPUT 2 D',
    'OUTPUT 2 HEATER RANGE', 'OUTPUT 2 HEATER OUTPUT 1(%)',
    'OUTPUT 2 RESISTANCE', 'OUTPUT 2 MAX CURRENT(A)', 'OUTPUT 2 DISPLAY MODE'
]
timestamp_fmt = '%Y-%m-%d %H:%M:%S.%f'


def query():
    t_now = datetime.now()
    t1, t2, t3, t4, t5, t6, _, _ = inst.get_all_kelvin_reading()
    output_mode_1 = inst.get_heater_output_mode(1)
    setpoint_1 = inst.get_control_setpoint(1)
    heater_pid_1 = inst.get_heater_pid(1)
    heater_range_1 = inst.get_heater_range(1).name
    heater_output_1 = inst.get_heater_output(1)
    heater_setup_1 = inst.get_heater_setup(1)
    output_mode_2 = inst.get_heater_output_mode(2)
    setpoint_2 = inst.get_control_setpoint(2)
    heater_pid_2 = inst.get_heater_pid(2)
    heater_range_2 = inst.get_heater_range(2).name
    heater_output_2 = inst.get_heater_output(2)
    heater_setup_2 = inst.get_heater_setup(2)

    new_data = [
        t_now.strftime(timestamp_fmt),
        t1, t2, t3, t4, t5, t6,
        output_mode_1['channel'].name, setpoint_1,
        heater_pid_1['gain'], heater_pid_1['integral'], heater_pid_1['ramp_rate'],
        heater_range_1, heater_output_1,
        heater_setup_1['heater_resistance'].name, heater_setup_1['max_current'], heater_setup_1['output_display_mode'].name,
        output_mode_2['channel'].name, setpoint_2,
        heater_pid_2['gain'], heater_pid_2['integral'], heater_pid_2['ramp_rate'],
        heater_range_2, heater_output_2,
        heater_setup_2['heater_resistance'].name, heater_setup_2['max_current'], heater_setup_2['output_display_mode'].name
    ]
    data_cache.append(new_data)
    if len(data_cache) > cache_num:
        data_cache.pop(0)
    save(path, task, name, columns, new_data)
    print(new_data)


def plot():
    fig, ax1 = plt.subplots(figsize=(30/2.54, 15/2.54))
    fig.canvas.manager.set_window_title(name)
    if plot_data:
        ax2 = ax1.twinx()
        ax3 = ax1.twinx()
        ax4 = ax1.twinx()
        ax5 = ax1.twinx()
        ax6 = ax1.twinx()
        ax7 = ax1.twinx()
        ax8 = ax1.twinx()
        axs = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
        xlabel = 't(s)'
        ylabels = ['T1(K)', 'T2(K)', 'T3(K)', 'T4(K)', 'T5(K)',
                   'T6(K)', 'OUTPUT1(%)', 'OUTPUT2(%)']
        styles = ['.-', '.-', '.-', '.-', '.-',
                  '.-', 'v', 's']
        ax_gap = 55

        colors = list(mcolors.TABLEAU_COLORS)
        for i in range(len(axs)):
            axs[i].spines['left'].set_color(colors[0])
            axs[i].spines['right'].set_color(colors[i])
            axs[i].tick_params(axis='y', color=colors[i], labelcolor=colors[i])
            axs[i].spines['right'].set_position(
                ('outward', ax_gap*(i-1) if i > 1 else 0))
        plt.ion()
        while plt.fignum_exists(1):
            if len(data_cache) > 0:
                x = np.array([datetime.strptime(data[0], timestamp_fmt).timestamp()
                              for data in data_cache])
                x -= x[-1]
                y = [np.array([data[i] for data in data_cache])
                     for i in list(range(1, 7))+[13, 23]]
                title = f'{data_cache[-1][0]}\n{data_cache[-1][7:13]}\n{data_cache[-1][17:23]}'
                for i in range(len(axs)):
                    axs[i].cla()
                    axs[i].plot(x, y[i], styles[i],
                                c=colors[i], label=ylabels[i])
                    axs[i].ticklabel_format(useOffset=False)
                    axs[i].spines['right'].set_position(
                        ('outward', ax_gap*(i-1) if i > 1 else 0))
                ax1.set_xlabel(xlabel)
                ax1.set_title(title)
                fig.legend(loc=2, bbox_to_anchor=(0, 1),
                           bbox_transform=ax1.transAxes, framealpha=0.1)
                plt.tight_layout()
            plt.pause(plot_interval)
    else:
        plt.axis('off')
        plt.show()


ctypes.WinDLL('winmm').timeBeginPeriod(1)  # ms
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=f'{task}.log',
                    level=logging.INFO, format=LOG_FORMAT)
logging.getLogger('apscheduler').setLevel(logging.ERROR)
logging.getLogger('lakeshore').setLevel(logging.ERROR)
data_cache = []
inst = Model336(ip_address=instrument_ip)
sched = BackgroundScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
sched.add_job(query, 'interval', seconds=interval, id='query')
sched.start()
logging.info(f'{name}, Start')
plot()
sched.shutdown()
inst.disconnect_tcp()
logging.info(f'{name}, Stop')
recompress(path, task, name)
