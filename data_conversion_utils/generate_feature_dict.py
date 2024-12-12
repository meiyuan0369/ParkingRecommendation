"""
功能说明：

本脚本的主要目的是从两个CSV文件（'user_preferences.csv'和'parking_spots_with_coords.csv'）
中提取数据，并为其中的每个独特的 '列名_值' 组合分配一个唯一的整数编码。这种编码对于后续的数据处理和
机器学习模型训练非常有用，因为它将分类变量转换为模型可以使用的数值型格式。

所得到的编码会被保存在一个名为 'feature_dict.pkl' 的Pickle文件中，以便于在其他数据处理步骤或者模型预测中重新使用。
脚本还会排除经纬度数据的编码，因为它们已是数值形式，不需要转换。

如何使用本脚本：
1. 确保 'user_preferences.csv' 和 'parking_spots_with_coords.csv' 文件位于脚本同一目录下或者修改代码中的文件路径。
2. 运行脚本，生成的 'feature_dict.pkl' 文件将包含所有唯一 '列名_值' 对的编码。

输出：
- 'feature_dict.pkl'：包含 '列名_值' 的编码字典的Pickle文件。

注意：本脚本使用 pandas 库来读取CSV文件和 pickle 库来保存编码字典。
"""

import pandas as pd
import pickle

# 初始化用于存储每个唯一 "列名_值" 对的编码的字典
encoding_dict = {}
# 初始化编码索引，用于为新的 "列名_值" 对分配新的编码值
next_code = 0


def encode_value(column, value):
    """
    如果给定的列名和值组合尚未被编码，则为其分配一个新的编码，并存入字典。
    已存在的组合将返回其对应的编码值。

    Args:
    column (str): 列名
    value (str): 列中的值

    Returns:
    int: 分配给该 "列名_值" 对的编码
    """
    global next_code
    # 构建唯一键来代表 "列名_值" 对
    key = f'{column}_{value}'
    # 如果键不在字典中，则添加到字典并更新编码索引
    if key not in encoding_dict:
        encoding_dict[key] = next_code
        next_code += 1
    return encoding_dict[key]


# 读取用户偏好数据文件
user_preferences_df = pd.read_csv('user_preferences.csv')
# 对数据框中的每个值应用编码函数
for index, row in user_preferences_df.iterrows():
    for column in user_preferences_df.columns:
        value = row[column]
        encode_value(column, value)  # 编码 "列名_值" 对

# 读取停车位坐标数据文件
parking_spots_df = pd.read_csv('parking_spots_with_coords.csv')
# 定义需要排除的列名列表
exclude_columns = ['Longitude', 'Latitude']

# 对除了经纬度之外的列进行编码
for index, row in parking_spots_df.iterrows():
    for column in parking_spots_df.columns:
        if column not in exclude_columns:
            value = row[column]
            encode_value(column, value)  # 编码 "列名_值" 对

# 将编码字典存储到Pickle文件中
with open('feature_dict.pkl', 'wb') as f:
    pickle.dump(encoding_dict, f)

# 确认编码过程完成并且字典已保存
print("编码完成并保存为feature_dict.pkl")
