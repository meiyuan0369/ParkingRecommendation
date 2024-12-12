import pandas as pd


def analyze_data(input_file_path):
    # 读取文件，指定正确的分隔符和编码
    try:
        df = pd.read_csv(input_file_path, sep=';', encoding='ISO-8859-1')
    except Exception as e:
        print("Error reading the file:", e)
        return

    # 输出原始数据的一部分
    print("原始数据预览:")
    print(df.head())

    # 数据集信息分析
    print("\n数据集信息：")

    # 总评分数
    total_ratings = len(df)
    print("总评分数:", total_ratings)

    # 用户数
    unique_users = df['User-ID'].nunique()
    print("用户数:", unique_users)

    # 物品数
    unique_items = df['Items'].nunique()
    print("物品数(书籍):", unique_items)

    # 稀疏值计算
    sparsity = 1 - (total_ratings / (unique_users * unique_items))
    print("数据稀疏度:", sparsity)

    # 检查是否有空值
    missing_values = df.isnull().sum()
    print("\n缺失值情况:")
    print(missing_values)


analyze_data('filtered_ratings.csv')
