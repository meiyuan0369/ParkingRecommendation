import csv

"""
此脚本用于将原始的评分数据从CSV文件中读取，并根据设定的阈值转换评分，
最后将转换后的数据保存到新的CSV文件中。转换规则是：
- 如果原始评分大于或等于阈值，则转换为1；
- 如果小于阈值，则转换为0。
"""

# 原始CSV文件路径
input_file = '../data/original_ratings.csv'
# 输出CSV文件路径
output_file = '../data/implicit_ratings.csv'

# 阈值设定
threshold = 8

# 读取原始CSV文件并进行转换
with open(input_file, mode='r', newline='', encoding='utf-8') as infile, open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # 写入新CSV文件的标题行
    writer.writerow(['User ID', 'Item ID', 'Rating (1 or 0)'])

    next(reader)  # 跳过原始数据的标题行
    for row in reader:
        item_id = row[0]  # 物品ID
        user_id = row[1]  # 用户ID
        rating = float(row[2])  # 评分

        # 根据阈值将评分转换为1或0
        converted_rating = 1 if rating >= threshold else 0

        # 写入转换后的数据
        writer.writerow([user_id, item_id, converted_rating])

print("转换完成！")
