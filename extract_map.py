# 地图提取脚本,在config.json中配置地图的起始坐标和结束坐标,
# 修改此文件中save_path,指向你想要提取的存档,然后运行extract_map.py即可
# 提取后的文件保存在自动创建的日期文件夹中
# 将提取后的所有文件复制到新存档,所选取的地块和地块中的物品都会转移到新存档中

from pathlib import Path
import json
from datetime import datetime
import shutil

def in_boundary_vehicle(x, y, start_x, start_y, end_x, end_y):
    return (x >= int(start_x) and x <= int(end_x)) and (y >= int(start_y) and y <= int(end_y))

def in_boundary_map(map_x, map_y, start_x, start_y, end_x, end_y):
    """判断map数据是否在范围内"""
    x = int(map_x) * 10
    y = int(map_y) * 10
    return (x >= int(start_x) and x <= int(end_x)) and (y >= int(start_y) and y <= int(end_y))

def in_boundary_chunk(chunk_x, chunk_y, start_x, start_y, end_x, end_y):
    """判断chunk数据是否在范围内"""
    x = int(chunk_x) * 300
    y = int(chunk_y) * 300
    return (x >= int(start_x) and x <= int(end_x)) and (y >= int(start_y) and y <= int(end_y))

def extract_map(save_path, backup_path, start_x, start_y, end_x, end_y):
    """备份地图和物品数据"""
    # 兼容b42存档目录
    files = Path.iterdir(save_path)
    for file in files:
        if file.name == 'WorldDictionary.bin':
            # print(file.name)
            shutil.copy(file, backup_path)

    if save_path.joinpath('map').exists():
        map_files = Path.iterdir(save_path.joinpath('map'))
        chunk_files = Path.iterdir(save_path.joinpath('chunkdata'))
    else:
        map_files = Path.iterdir(save_path)
        chunk_files = Path.iterdir(save_path)

    backup_map_path = backup_path.joinpath('map') if backup_path.joinpath('map').exists() else backup_path
    backup_chunk_path = backup_path.joinpath('chunkdata') if backup_path.joinpath('chunkdata').exists() else backup_path
    backup_map_path.mkdir(parents=True, exist_ok=True)
    backup_chunk_path.mkdir(parents=True, exist_ok=True)

    for file in map_files:
        item = file.stem.split('_')
        if len(item) == 3 and item[0] == 'map':
            if in_boundary_map(item[1], item[2], start_x, start_y, end_x, end_y):
                # print(file.name)
                shutil.copy(file, backup_map_path)

    for file in chunk_files:
        item = file.stem.split('_')
        if len(item) == 3 and item[0] == 'chunkdata':
            if in_boundary_chunk(item[1], item[2], start_x, start_y, end_x, end_y):
                # print(file.name)
                shutil.copy(file, backup_chunk_path)

def trans_save(config, save_path, backup_path):
    for region in config['regions']:
        print(f'正在复制地点:{region["name"]}')
        start_x = region['start'][0]
        start_y = region['start'][1]
        end_x = region['end'][0]
        end_y = region['end'][1]
        extract_map(save_path, backup_path, start_x, start_y, end_x, end_y)

def filter_vehicles(config, old_vehicles_data):
    filtered_ids = []

    for data in old_vehicles_data:
        for region in config['regions']:
            start_x = region['start'][0]
            start_y = region['start'][1]
            end_x = region['end'][0]
            end_y = region['end'][1]
            if in_boundary_vehicle(data[1], data[2], start_x, start_y, end_x, end_y):
                filtered_ids.append(data[0])
                break
    return filtered_ids

if __name__ == '__main__':
    CWD = Path(__file__).parent.absolute()
    CONFIG = CWD.joinpath('config.json')

    with open(CONFIG, 'r', encoding='utf-8') as file:
        config = json.load(file)

    # 加载存档
    save_path = Path(r'C:\Users\scream\Zomboid\Saves\Sandbox\2024-12-20_17-21-51')
    # 获取当前日期和时间
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CWD.joinpath(current_datetime)
    # 创建备份文件夹
    if not backup_path.exists():
        Path.mkdir(backup_path)
        print(f"文件夹 '{backup_path}' 创建成功！")
    else:
        print(f"文件夹 '{backup_path}' 已存在。")

    trans_save(config, save_path, backup_path)
