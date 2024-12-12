import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import csr_matrix
import warnings

warnings.filterwarnings('ignore')


# 定义处理每个数据块的函数
def process_chunk(chunk, user_rating_counts, item_rating_counts):
    # 将 '评分' 转换为 float32
    chunk['评分'] = chunk['评分'].astype(np.float32)

    # 更新评分统计
    user_rating_counts = user_rating_counts.add(chunk.groupby('用户ID')['评分'].count(), fill_value=0)
    item_rating_counts = item_rating_counts.add(chunk.groupby('停车位ID')['评分'].count(), fill_value=0)

    return chunk, user_rating_counts, item_rating_counts


# 初始化空的 DataFrame 和统计字典
ratings_df = pd.DataFrame(columns=['停车位ID', '用户ID', '评分'])
user_rating_counts = pd.Series(dtype=np.int32)
item_rating_counts = pd.Series(dtype=np.int32)

# 存储所有数据块，后续统一拼接
chunks_list = []

# 分块读取数据并处理
chunk_size = 100000  # 每次读取的行数，根据内存情况调整
file_path = 'original_ratings.csv'

for chunk in pd.read_csv(file_path, skiprows=1, header=None, usecols=[0, 1, 2],
                         dtype={0: 'int32', 1: 'int32', 2: 'float32'}, chunksize=chunk_size):
    chunk.columns = ['停车位ID', '用户ID', '评分']
    chunk, user_rating_counts, item_rating_counts = process_chunk(chunk, user_rating_counts, item_rating_counts)
    chunks_list.append(chunk)  # 将每个数据块保存到列表中

# 合并所有数据块
ratings_df = pd.concat(chunks_list, ignore_index=True)

# 对合并后的数据进行类别编码
ratings_df['用户ID'] = ratings_df['用户ID'].astype('category')
ratings_df['停车位ID'] = ratings_df['停车位ID'].astype('category')

# 获取所有用户和停车位的编码
ratings_df['用户ID'] = ratings_df['用户ID'].cat.codes
ratings_df['停车位ID'] = ratings_df['停车位ID'].cat.codes

# 进行数据分析
# 用户评分分布
plt.figure(figsize=(8, 6))
sns.histplot(user_rating_counts, kde=True, color='green', bins=20)
plt.title('Distribution of Ratings per User', fontsize=14)
plt.xlabel('Number of Ratings per User', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.show()

# 停车位评分分布
plt.figure(figsize=(8, 6))
sns.histplot(item_rating_counts, kde=True, color='purple', bins=20)
plt.title('Distribution of Ratings per Item', fontsize=14)
plt.xlabel('Number of Ratings per Item', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.show()

# 用户评分分布
plt.figure(figsize=(8, 6))
sns.histplot(ratings_df['评分'], kde=True, color='blue', bins=10)
plt.title('User Rating Distribution', fontsize=14)
plt.xlabel('Rating', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.show()

# 停车位平均评分分布
item_avg_ratings = ratings_df.groupby('停车位ID')['评分'].mean()
plt.figure(figsize=(8, 6))
sns.histplot(item_avg_ratings, kde=True, color='orange', bins=20)
plt.title('Distribution of Average Ratings per Item', fontsize=14)
plt.xlabel('Average Rating per Item', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.show()

# 创建稀疏用户-停车位评分矩阵
rating_matrix_sparse = csr_matrix((ratings_df['评分'],
                                   (ratings_df['用户ID'], ratings_df['停车位ID'])))

# 输出文本分析结果
num_ratings = len(ratings_df)
num_users = ratings_df['用户ID'].nunique()  # 重新计算用户数
num_items = ratings_df['停车位ID'].nunique()
num_nonzero_ratings = rating_matrix_sparse.count_nonzero()
sparsity = 1 - num_nonzero_ratings / (num_users * num_items)

ratings_df['评分_float'] = ratings_df['评分']
print("新的 '评分_float' 数据类型:", ratings_df['评分_float'].dtype)

avg_ratings_per_user = user_rating_counts.mean()
max_ratings_per_user = user_rating_counts.max()
min_ratings_per_user = user_rating_counts.min()

avg_ratings_per_item = item_avg_ratings.mean()
max_ratings_per_item = item_avg_ratings.max()
min_ratings_per_item = item_avg_ratings.min()

print("\nTextual Analysis Results:")
print(f"Matrix Sparsity: {sparsity:.4f}")
print(f"Number of Ratings: {num_ratings}")
print(f"Number of Users: {num_users}")  # 输出用户数量
print(f"Number of Items: {num_items}")
print(f"\nAverage Ratings per User: {avg_ratings_per_user:.2f}")
print(f"Max Ratings per User: {max_ratings_per_user}")
print(f"Min Ratings per User: {min_ratings_per_user}")
print(f"\nAverage Ratings per Item: {avg_ratings_per_item:.2f}")
print(f"Max Ratings per Item: {max_ratings_per_item}")
print(f"Min Ratings per Item: {min_ratings_per_item}")
print(
    f"\nUser Rating Distribution: Mean={ratings_df['评分_float'].mean():.2f}, Max={ratings_df['评分_float'].max()}, Min={ratings_df['评分_float'].min()}")
