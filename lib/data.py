import os
import pandas as pd
from datetime import datetime


def save(path: str, task: str, name: str, columns: list, new_data: list) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(os.path.join(path, 'temp')):
        os.makedirs(os.path.join(path, 'temp'))
    file_name = f'{task}__{datetime.now().year}__{name}.csv.gz'
    full_path_temp = os.path.join(path, 'temp', file_name)
    if not os.path.exists(full_path_temp):
        pd.DataFrame(None, columns=columns).to_csv(
            full_path_temp, compression='gzip', header=True, index=False)
    pd.DataFrame([new_data]).to_csv(full_path_temp,
                                    compression='gzip', mode='a', header=False, index=False)


def recompress(path: str, task: str, name: str) -> None:
    file_name = f'{task}__{datetime.now().year}__{name}.csv.gz'
    full_path_temp = os.path.join(path, 'temp', file_name)
    full_path = os.path.join(path, file_name)
    pd.read_csv(full_path_temp, dtype=str).to_csv(
        full_path, compression='gzip', header=True, index=False)
