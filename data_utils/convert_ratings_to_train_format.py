import os
import random


class TrainDataGenerator:
    """
    TrainDataGenerator类用于从原始交互数据中生成训练集数据。
    """

    def __init__(self, rating_threshold=3.5, train_ratio=0.8):
        """
        初始化TrainDataGenerator类。

        :param rating_threshold: 用于定义正向互动的评分阈值，默认为3.5
        :param train_ratio: 训练集的比例，默认为80%
        """
        self.rating_threshold = rating_threshold
        self.train_ratio = train_ratio

    def split_train_data(self, all_interactions):
        """
        根据给定的划分比例，将正向交互数据划分为训练集。

        :param all_interactions: 原始用户交互数据，字典格式，键为userID，值为itemID列表
        :return: 训练集数据，字典格式，键为用户ID，值为训练集中的itemID列表
        """
        train_data = {}

        for user, items in all_interactions.items():
            # 随机打乱用户的交互项，然后根据train_ratio划分
            random.shuffle(items)
            num_train_samples = int(len(items) * self.train_ratio)

            if num_train_samples > 0:
                train_data[user] = items[:num_train_samples]

        return train_data

    def save_train_data(self, train_data, output_file):
        """
        将生成的训练集数据保存到文件中。

        :param train_data: 训练集数据，字典格式，键为用户ID，值为训练集中的itemID列表
        :param output_file: 保存训练集数据的文件路径
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                for user, items in train_data.items():
                    items_str = ' '.join(items)  # 使用空格分隔物品ID
                    f.write(f"{user} {items_str}\n")  # 用户ID与物品ID之间也用空格

            print(f"训练集数据已保存至: {output_file}")

        except Exception as e:
            raise Exception(f"保存训练集文件失败: {str(e)}")

    def generate_train_data(self, all_interactions_file, output_file):
        """
        从原始交互数据中生成train.txt文件。

        :param all_interactions_file: 包含所有用户交互数据的文件路径
        :param output_file: 保存生成的训练集数据的文件路径
        """
        # 加载原始交互数据
        print("加载原始用户交互数据...")
        all_interactions = {}
        try:
            with open(all_interactions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # 按照空格分割，第一部分为用户ID，后面为物品ID
                    parts = line.strip().split(' ')
                    user = parts[0]  # 用户ID
                    items = parts[1:]  # 物品ID列表
                    all_interactions[user] = items
        except Exception as e:
            raise Exception(f"读取原始交互数据文件失败: {str(e)}")

        # 生成训练集数据
        print("生成训练集数据...")
        train_data = self.split_train_data(all_interactions)

        # 保存训练集数据
        print("保存训练集数据...")
        self.save_train_data(train_data, output_file)


if __name__ == "__main__":
    # 文件路径
    all_interactions_file = '../data/all_interactions.txt'  # 所有用户正向交互数据的文件路径
    train_output_file = '../data/train.txt'  # 输出的训练集文件路径

    # 初始化并生成训练数据
    generator = TrainDataGenerator(rating_threshold=3.6, train_ratio=0.8)
    generator.generate_train_data(all_interactions_file, train_output_file)
