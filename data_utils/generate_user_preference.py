import pandas as pd
from sklearn.linear_model import LinearRegression

# 读取CSV文件
ratings_df = pd.read_csv('../data/original_ratings.csv', names=['UserID', 'ParkingID', 'Rating'])
parkings_df = pd.read_csv('../data/parking_spots_with_coords.csv')

# 合并数据
merged_df = pd.merge(ratings_df, parkings_df, on="ParkingID")

# 数据预处理
# 转换“是”和“否”为数值1和0
merged_df['Near Elevator'] = merged_df['Near Elevator'].map({'是': 1, '否': 0})
merged_df['Has Surveillance'] = merged_df['Has Surveillance'].map({'是': 1, '否': 0})

# 模型训练
user_weights = pd.DataFrame()

for user_id in merged_df['UserID'].unique():
    user_data = merged_df[merged_df['UserID'] == user_id]

    # 选取相关的特征进行学习
    X = user_data[['Parking Fee (CNY/hour)', 'Driving Distance (meters)', 'Near Elevator', 'Has Surveillance']]
    y = user_data['Rating']

    model = LinearRegression()
    model.fit(X, y)

    # 提取权重并存储
    weights = pd.DataFrame({
        'UserID': [user_id],
        'parking_fee_weight': [model.coef_[0]],
        'driving_distance_weight': [model.coef_[1]],
        'near_elevator_weight': [model.coef_[2]],
        'has_surveillance_weight': [model.coef_[3]]
    })

    user_weights = pd.concat([user_weights, weights], ignore_index=True)

# 保存用户偏好
user_weights.to_csv('user_preferences.csv', index=False)
