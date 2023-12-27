import ctypes
import logging
import numpy as np
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from lib.data import recompress, save
from lib.deepvna import DeepVNA, notch_search


inst_port = 'COM3'
task = 'Cryostat'
name = 'DeepVNA'
center = 41.96e6  # unit is Hz
span = 2e6  # unit is Hz
points = 301
sampling_time = 2  # unit is s
interval = 4  # unit is s
plot_interval = 5  # unit is s
cache_num = 600
path = '.'
save_data = True
save_csv = False
print_data = True
plot_data = True
columns = [
    'Time', 'Center(Hz)', 'S11Center(dB)',
    'CenterLeft3dB(Hz)', 'S11CenterLeft3dB(dB)',
    'CenterRight3dB(Hz)', 'S11CenterRight3dB(dB)',
    'FrqS11Max(Hz)', 'S11Max(dB)',
    'QualityFactor(Unit)', 'Reflect(dB)'
]
timestamp_fmt = '%Y-%m-%d %H:%M:%S.%f'


def query():
    t_now = datetime.now()
    deepvna.sweep_once(sampling_time)
    frq = deepvna.frequencies()
    s11 = [20 * np.log10(np.linalg.norm(x)) for x in deepvna.data0()]
    center, s11_center, center_left_3db, s11_left_3db, center_right_3db, s11_right_3db, frq_s11_max, s11_max = notch_search(
        frq, s11)
    quality = center / (center_right_3db - center_left_3db)
    reflect = s11_center - s11_max

    new_data = [
        t_now.strftime(timestamp_fmt), center, s11_center,
        center_left_3db, s11_left_3db,
        center_right_3db, s11_right_3db,
        frq_s11_max, s11_max,
        quality, reflect
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
        ax2 = ax1.twinx()
        axs = [ax1, ax2]
        xlabel = 't(s)'
        ylabels = ['Quality', 'Reflect(dB)']
        styles = ['.-', '.-']
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
                y = [np.array([data[i] for data in data_cache]) for i in [-2, -1]]
                title = f'{data_cache[-1][0]}\n{float(data_cache[-1][1]) * 1e-6} MHz'
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
data_cache = []
deepvna = DeepVNA(port=inst_port)
deepvna.sweep(center, span, points)
sched = BackgroundScheduler({'apscheduler.timezone': 'Asia/Shanghai'})
sched.add_job(query, 'interval', seconds=interval, id='query')
sched.start()
logging.info(f'{name}, Start')
plot()
sched.shutdown()
deepvna.query('resume')
deepvna.close()
logging.info(f'{name}, Stop')
recompress(path, task, name)