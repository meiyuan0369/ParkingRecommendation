import pickle
import json
import os

"""
功能说明：

本脚本提供了一个功能，用于将Pickle格式的文件转换为JSON格式。这通常用于数据交换或使数据更容易在不同的编程环境间共享和阅读。
Pickle文件通常用于Python内部的对象序列化，而JSON格式则提供了一种轻量且标准的方式，让数据在不同的编程语言和平台间传输。

函数 `convert_pkl_to_json` 接收一个Pickle文件作为输入，并生成对应的JSON文件。这个过程包括读取Pickle文件、解析数据，
然后将数据以JSON格式写入到新文件中。

参数:
- input_pkl_file (str): 需要转换的Pickle文件的路径。

"""


def convert_pkl_to_json(input_pkl_file):
    # 检查文件扩展名
    if not input_pkl_file.endswith('.pkl'):
        raise ValueError("输入文件必须是 .pkl 格式")

    # 生成输出 JSON 文件名
    output_json_file = os.path.splitext(input_pkl_file)[0] + '.json'

    # 用 'rb' 模式打开 .pkl 文件
    with open(input_pkl_file, 'rb') as file:
        data = pickle.load(file)

    # 转换并保存为 JSON 格式
    with open(output_json_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"数据已保存为 JSON 文件：{output_json_file}")


if __name__ == '__main__':
    # 示例调用
    convert_pkl_to_json('feature_dict.pkl')
