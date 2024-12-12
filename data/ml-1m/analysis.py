import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 设置Seaborn样式
sns.set(style="whitegrid")

# 1. 读取数据
# 假设文件名为 'ratings.dat' 和 'movies.dat'，如果文件路径不同，请相应调整。
# 读取数据时，显式指定编码
ratings = pd.read_csv('ratings.dat', delimiter='::', names=['userId', 'movieId', 'rating', 'timestamp'], engine='python', encoding='latin-1')
movies = pd.read_csv('movies.dat', delimiter='::', names=['movieId', 'title', 'genres'], engine='python', encoding='latin-1')

# 查看数据前几行
print(ratings.head())
print(movies.head())

# 2. 数据清洗
# 检查缺失值
print("缺失值情况：")
print(ratings.isnull().sum())
print(movies.isnull().sum())

# 删除缺失值
ratings.dropna(inplace=True)
movies.dropna(inplace=True)

# 检查重复数据
print("重复数据数量：")
print(ratings.duplicated().sum())
print(movies.duplicated().sum())

# 删除重复数据
ratings.drop_duplicates(inplace=True)
movies.drop_duplicates(inplace=True)

# 3. 数据基本统计
# 评分数据的基本统计
print("\n评分数据基本统计：")
print(ratings['rating'].describe())

# 用户数量、电影数量以及评分数量
num_users = ratings['userId'].nunique()
num_movies = ratings['movieId'].nunique()
num_ratings = ratings.shape[0]

print(f"\nNumber of users: {num_users}")
print(f"Number of movies: {num_movies}")
print(f"Number of ratings: {num_ratings}")

# 4. 评分分布
plt.figure(figsize=(10, 6))
sns.countplot(x='rating', data=ratings, palette='viridis')
plt.title('Distribution of Ratings')
plt.xlabel('Rating')
plt.ylabel('Count')
plt.show()

# 5. 用户评分分布
# 每个用户的评分数量
user_ratings = ratings.groupby('userId').size()

# 绘制用户评分数量分布
plt.figure(figsize=(10, 6))
sns.histplot(user_ratings, bins=50, kde=True, color='blue')
plt.title('Distribution of Number of Ratings per User')
plt.xlabel('Number of Ratings')
plt.ylabel('Count')
plt.show()

# 用户评分数量的基本统计
print("\n用户评分数量的基本统计：")
print(user_ratings.describe())

# 6. 电影评分分布
# 每部电影的评分数量
movie_ratings = ratings.groupby('movieId').size()

# 绘制电影评分数量分布
plt.figure(figsize=(10, 6))
sns.histplot(movie_ratings, bins=50, kde=True, color='green')
plt.title('Distribution of Number of Ratings per Movie')
plt.xlabel('Number of Ratings')
plt.ylabel('Count')
plt.show()

# 电影评分数量的基本统计
print("\n电影评分数量的基本统计：")
print(movie_ratings.describe())

# 7. 评分的热图（用户-电影评分矩阵）
# 创建用户-电影评分矩阵
rating_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating')

# 由于评分矩阵可能非常稀疏，这里仅绘制前1000个用户和前1000部电影的热图
ratings_sample = ratings[ratings['userId'].isin(ratings['userId'].unique()[:1000])]
ratings_sample = ratings_sample[ratings_sample['movieId'].isin(ratings['movieId'].unique()[:1000])]

# 创建用户-电影评分矩阵
rating_matrix_sample = ratings_sample.pivot_table(index='userId', columns='movieId', values='rating')

# 绘制评分热图
plt.figure(figsize=(12, 10))
sns.heatmap(rating_matrix_sample, cmap='YlGnBu', cbar_kws={'label': 'Rating'}, xticklabels=False, yticklabels=False)
plt.title('Rating Heatmap (Users vs. Movies)')
plt.show()

# 8. 最受欢迎的电影
# 统计每部电影的评分数量
movie_popularity = ratings.groupby('movieId').size()

# 获取评分最多的前10部电影
top_movies = movie_popularity.sort_values(ascending=False).head(10)

# 绘制最受欢迎电影的柱状图
plt.figure(figsize=(12, 6))
top_movies.plot(kind='bar', color='orange')
plt.title('Top 10 Most Rated Movies')
plt.xlabel('Movie ID')
plt.ylabel('Number of Ratings')
plt.xticks(rotation=90)
plt.show()

# 9. 用户评分数量分布（每个用户评分数量的直方图）
plt.figure(figsize=(10, 6))
sns.histplot(user_ratings, bins=50, kde=True, color='purple')
plt.title('Distribution of Number of Ratings per User')
plt.xlabel('Number of Ratings')
plt.ylabel('Count')
plt.show()

# 10. 电影的评分趋势（按时间分布）
# 转换时间戳为日期
ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s')

# 提取年份
ratings['year'] = ratings['timestamp'].dt.year

# 按年份统计评分数量
ratings_by_year = ratings.groupby('year').size()

# 绘制评分数量随时间变化的趋势
plt.figure(figsize=(10, 6))
ratings_by_year.plot(kind='line', marker='o', color='purple')
plt.title('Number of Ratings per Year')
plt.xlabel('Year')
plt.ylabel('Number of Ratings')
plt.grid(True)
plt.show()
