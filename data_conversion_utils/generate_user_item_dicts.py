"""
功能说明：

本脚本主要用于处理用户偏好与停车位数据，将这些数据与预先生成的编码字典（feature_dict.pkl）结合，生成新的编码字典
(user_dict.pkl 和 item_dict.pkl)。这些字典针对每个用户和停车位的唯一标识符存储编码后的属性值。这一步骤是为了
便于后续的数据处理和分析工作，特别是在需要以编码形式处理分类数据的机器学习模型中。

代码流程：
1. 从 'feature_dict.pkl' 文件中读取预先存储的编码字典。
2. 读取 'user_preferences.csv' 文件，生成用户编码字典user_dict，其中包含用户ID及其其他属性的编码。
3. 读取 'parking_spots_with_coords.csv' 文件，生成停车位编码字典item_dict，其中包含停车位ID及其其他属性的编码。
4. 保存 user_dict 和 item_dict 为Pickle文件，以供后续使用。

注意：
- 本脚本在处理时会排除某些列（如经纬度和特定的ID列），因为这些列可能不需要转换为编码形式。
- 本脚本假设所有需要的库和数据文件都已经正确安装和存放在相应位置。

如何使用本脚本：
- 运行脚本前，请确保相关的CSV文件和Pickle文件位于正确的路径。
- 确保 'feature_dict.pkl' 文件已经存在，它包含了从另一个预处理步骤生成的编码映射。

输出：
- user_dict.pkl：序列化的字典，包含用户ID及其属性的编码。
- item_dict.pkl：序列化的字典，包含停车位ID及其属性的编码。

"""
import pandas as pd
import pickle

# 读取编码字典
with open('feature_dict.pkl', 'rb') as f:
    encoding_dict = pickle.load(f)

# 生成和处理用户字典
user_dict = {}
user_preferences_df = pd.read_csv('user_preferences.csv')
print("User Preferences Columns:", user_preferences_df.columns)
for index, row in user_preferences_df.iterrows():
    user_id = str(row['user_ID'])
    user_dict[user_id] = {
        'name': encoding_dict.get(f'user_ID_{row["user_ID"]}', 'Unknown'),
        'attribute': []
    }
    for column in user_preferences_df.columns:
        if column != 'user_ID':
            encoded_value = encoding_dict.get(f'{column}_{row[column]}', None)
            if encoded_value:
                user_dict[user_id]['attribute'].append(encoded_value)
            else:
                print(f"Warning: Key '{column}_{row[column]}' not found in encoding_dict.")

# 生成和处理停车位字典
item_dict = {}
parking_spots_df = pd.read_csv('parking_spots_with_coords.csv')
print("Parking Spots Columns:", parking_spots_df.columns)
exclude_columns = ['Longitude', 'Latitude', 'ParkingID']
for index, row in parking_spots_df.iterrows():
    spot_id = str(row['ParkingID'])
    item_dict[spot_id] = {
        'title': encoding_dict.get(f'ParkingID_{row["ParkingID"]}', 'Unknown'),
        'attribute': []
    }
    for column in parking_spots_df.columns:
        if column not in exclude_columns:
            encoded_value = encoding_dict.get(f'{column}_{row[column]}', None)
            if encoded_value:
                item_dict[spot_id]['attribute'].append(encoded_value)
            else:
                print(f"Warning: Key '{column}_{row[column]}' not found in encoding_dict.")

# 保存生成的字典为Pickle文件
with open('user_dict.pkl', 'wb') as f:
    pickle.dump(user_dict, f)
with open('item_dict.pkl', 'wb') as f:
    pickle.dump(item_dict, f)

print("user_dict.pkl 和 item_dict.pkl 已生成并保存")
