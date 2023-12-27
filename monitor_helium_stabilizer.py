import ctypes
import logging
import numpy as np
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from lib.data import recompress, save
from lib.helium_stabilizer import HeliumStabilizer


instrument_ip = '192.168.30.130'
task = 'Cryostat'
name = 'Helium Stabilizer'
interval = 2  # unit is s
plot_interval = 5  # unit is s
cache_num = 600
path = '.'
plot_data = True
columns = [
    'Time', 'SV1', 'SV2', 'MANUAL_OR_AUTO', 'P1(bar)',
    'SETPOINT_A(bar)', 'SETPOINT_B(bar)', 'SETPOINT_C(bar)', 'COMPARE_PERIOD(ms)'
]
timestamp_fmt = '%Y-%m-%d %H:%M:%S.%f'


def query():
    t_now = datetime.now()
    sv1 = inst.get_sv1()
    sv2 = inst.get_sv2()
    manual_or_auto = inst.get_manual_or_auto()
    p1 = inst.get_pressure_1()
    setpoint_a = inst.get_setpoint_a()
    setpoint_b = inst.get_setpoint_b()
    setpoint_c = inst.get_setpoint_c()
    compare_period = inst.get_compare_period()

    new_data = [
        t_now.strftime(timestamp_fmt),
        sv1, sv2, manual_or_auto, p1,
        setpoint_a, setpoint_b, setpoint_c,
        compare_period
    ]
    data_cache.append(new_data)
    if len(data_cache) > cache_num:
        data_cache.pop(0)
    save(path, task, name, columns, new_data)
    print(new_data)


def plot():
    fig, ax1 = plt.subplots(figsize=(12/2.54, 9/2.54))
    fig.canvas.manager.set_window_title(name)
    if plot_data:
        axs = [ax1]
        xlabel = 't(s)'
        ylabels = ['P1(bar)']
        styles = ['.-']
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
                y = [np.array([data[4] for data in data_cache])]
                title = f'{data_cache[-1][0]}\n{data_cache[-1][1:4]}\n{data_cache[-1][5:9]}'
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
logging.getLogger('snap7').setLevel(logging.ERROR)
data_cache = []
inst = HeliumStabilizer(instrument_ip)
inst.set_setpoint_a(1.03)
inst.set_setpoint_b(1.04)
inst.set_setpoint_c(1.05)
inst.set_compare_period(1000)
inst.set_manual_or_auto(1)
sched = BackgroundScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
sched.add_job(query, 'interval', seconds=interval, id='query')
sched.start()
logging.info(f'{name}, Start')
plot()
sched.shutdown()
inst.close()
logging.info(f'{name}, Stop')
recompress(path, task, name)
