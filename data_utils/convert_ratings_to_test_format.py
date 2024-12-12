import os


class ParkingTestDataGenerator:
    """
    ParkingTestDataGenerator类用于从训练集和原始交互数据中生成测试集数据。
    """

    def __init__(self, train_file):
        """
        初始化ParkingTestDataGenerator类。

        :param train_file: 包含训练数据的train.txt文件路径
        """
        self.train_file = train_file

    def load_train_data(self):
        """
        从train.txt文件中加载用户的训练集交互数据。

        :return: 一个字典，键为用户ID，值为用户在训练集的itemID列表
        """
        train_data = {}
        try:
            with open(self.train_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # 按空格分割，第一项为用户ID，后续项为物品ID
                    parts = line.strip().split(' ')
                    user = parts[0]
                    items = parts[1:]
                    train_data[user] = set(items)  # 使用集合来方便后续的差集操作
        except Exception as e:
            raise Exception(f"读取训练集文件失败: {str(e)}")

        return train_data

    def split_test_data(self, all_interactions, train_data):
        """
        根据训练集数据划分测试集数据。

        :param all_interactions: 原始用户交互数据（所有正向交互）
        :param train_data: 用户的训练集交互数据
        :return: 测试集数据，字典格式，键为用户ID，值为测试集中的itemID列表
        """
        test_data = {}

        for user, items in all_interactions.items():
            if user in train_data:
                # 将用户的所有正向交互与训练集做差集运算，得到未用于训练的交互
                testable_items = list(set(items) - train_data[user])
            else:
                # 如果用户不在训练集中，则所有正向交互可以用于测试
                testable_items = items

            # 如果存在可用于测试的数据，存入 test_data
            if testable_items:
                test_data[user] = testable_items

        return test_data

    def save_test_data(self, test_data, output_file):
        """
        将生成的测试集数据保存到文件中。

        :param test_data: 测试集数据，字典格式，键为用户ID，值为测试集中的itemID列表
        :param output_file: 保存测试集数据的文件路径
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                for user, items in test_data.items():
                    # 将用户ID和物品ID用空格分隔
                    items_str = ' '.join(items)
                    f.write(f"{user} {items_str}\n")

            print(f"测试集数据已保存到: {output_file}")

        except Exception as e:
            raise Exception(f"保存测试集文件失败: {str(e)}")

    def generate_test_data(self, all_interactions_file, output_file):
        """
        从原始交互数据和train.txt中生成test.txt文件。

        :param all_interactions_file: 包含所有用户交互数据的文件路径
        :param output_file: 保存生成的测试集数据的文件路径
        """
        # 加载训练集数据
        print("加载训练集数据...")
        train_data = self.load_train_data()

        # 加载原始交互数据
        print("加载原始用户交互数据...")
        all_interactions = {}
        try:
            with open(all_interactions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # 按空格分割，第一项为用户ID，后续项为物品ID
                    parts = line.strip().split(' ')
                    user = parts[0]
                    items = parts[1:]
                    all_interactions[user] = items
        except Exception as e:
            raise Exception(f"读取原始交互数据文件失败: {str(e)}")

        # 生成测试集数据
        print("生成测试集数据...")
        test_data = self.split_test_data(all_interactions, train_data)

        # 保存测试集数据
        print("保存测试集数据...")
        self.save_test_data(test_data, output_file)


if __name__ == "__main__":
    # 文件路径
    train_file = '../data/train.txt'  # 训练集文件路径
    all_interactions_file = '../data/all_interactions.txt'  # 所有用户正向交互数据的文件路径
    test_output_file = '../data/test.txt'  # 输出的测试集文件路径

    # 初始化并生成测试数据
    generator = ParkingTestDataGenerator(train_file)
    generator.generate_test_data(all_interactions_file, test_output_file)
