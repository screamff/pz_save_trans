from pathlib import Path
import json
from math import floor
from datetime import datetime
import shutil

CWD = Path(__file__).parent.absolute()
CONFIG = CWD.joinpath('config_clean.json')
with open(CONFIG, 'r', encoding='utf-8') as file:
    config = json.load(file)
# todo 加载存档
save_path = Path(r'C:\Users\scream\Zomboid\Saves\Sandbox\19-12-2024_02-25-04')


def in_boundary_map(map_x, map_y, start_x, start_y, end_x, end_y):
    """判断map数据是否在范围内"""
    x = int(map_x) * 10
    y = int(map_y) * 10
    return (x >= int(start_x) and x <= int(end_x)) \
    and (y >= int(start_y) and y <= int(end_y))

def in_boundary_chunk(chunk_x, chunk_y, start_x, start_y, end_x, end_y):
    """判断chunk数据是否在范围内"""
    x = int(chunk_x) * 300
    y = int(chunk_y) * 300
    return (x >= int(start_x) and x <= int(end_x)) \
    and (y >= int(start_y) and y <= int(end_y))

def clean_map(save_path, start_x, start_y, end_x, end_y):
    """删除地图"""
    files = Path.iterdir(save_path)
    for file in files:
        item = file.stem.split('_')
        if len(item) == 3 and item[0] == 'map':
            if in_boundary_map(item[1], item[2], start_x, start_y, end_x, end_y):
                print(item)
                file.unlink()
        elif len(item) == 3 and item[0] == 'chunkdata':
            if in_boundary_chunk(item[1], item[2], start_x, start_y, end_x, end_y):
                print(item)
                file.unlink()


for region in config['regions']:
    print(f'正在删除地点:{region["name"]}')
    start_x = region['start'][0]
    start_y = region['start'][1]
    end_x = region['end'][0]
    end_y = region['end'][1]
    clean_map(save_path, start_x, start_y, end_x, end_y)
