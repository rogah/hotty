from multiprocessing import Pool, cpu_count

import os
import sys

from multiprocessing import Pool, cpu_count
from functools import partial
from pathlib import Path

base_directory = sys.argv[1]

list = []
for root, dirs, files in os.walk(base_directory):
    if '108_.m3u8' in files:
        m3u8_file = os.path.join(root, '108_.m3u8')
        directory_name = Path(m3u8_file).relative_to(base_directory).parts[0]
        filename = f"{directory_name}.mp4"
        mp4_file = os.path.join(base_directory, filename)
        list.append((m3u8_file, mp4_file))


def convert_to_mp4(files):
    source_file, destination_file = files
    print(source_file, destination_file)
    os.system(
        f'ffmpeg -allowed_extensions ALL -i {source_file} -c copy {destination_file}')
    return (source_file, destination_file)


if __name__ == '__main__':
    with Pool(cpu_count()) as p:
        p.map(convert_to_mp4, list)
