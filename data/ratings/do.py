import pandas as pd

# 读取CSV文件，指定分隔符为分号
data = pd.read_csv('filtered_ratings.csv', sep=';')

# 重新编码 User-ID
unique_users = data['User-ID'].unique()
user_mapping = {user: idx + 1 for idx, user in enumerate(unique_users)}
data['User-ID'] = data['User-ID'].map(user_mapping)

# 重新编码 Items-ID
unique_items = data['Items-ID'].unique()
item_mapping = {item: idx + 1 for idx, item in enumerate(unique_items)}
data['Items-ID'] = data['Items-ID'].map(item_mapping)

# 将结果保存为新的CSV文件，分隔符使用逗号
data.to_csv('original_ratings.csv', index=False, sep=',')

# 可选：保存映射关系以便后续查阅
# 保存 User-ID 映射
user_mapping_df = pd.DataFrame(list(user_mapping.items()), columns=['Original-User-ID', 'New-User-ID'])
user_mapping_df.to_csv('user_mapping.csv', index=False)

# 保存 Items-ID 映射
item_mapping_df = pd.DataFrame(list(item_mapping.items()), columns=['Original-Items-ID', 'New-Items-ID'])
item_mapping_df.to_csv('item_mapping.csv', index=False)
