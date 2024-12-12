import os
from py2neo import Graph


class ParkingDataConverter:
    """
    ParkingDataConverter类用于从Neo4j数据库或文件中读取用户的停车场评分数据，
    并根据给定的评分阈值将其转换为训练数据集格式。
    """

    def __init__(self, uri=None, username=None, password=None, rating_threshold=3.5):
        """
        初始化ParkingDataConverter类，连接Neo4j数据库，并设置评分阈值。如果未提供数据库凭据，则标记为不使用数据库模式。

        :param uri: Neo4j数据库URI
        :param username: 数据库用户名
        :param password: 数据库密码
        :param rating_threshold: 用于定义正向互动的评分阈值，默认为3.5
        """
        self.rating_threshold = rating_threshold

        # 如果提供了数据库连接信息，则初始化数据库连接
        if uri and username and password:
            try:
                self.graph = Graph(uri, auth=(username, password))
                self.use_database = True
                print(f"成功连接至Neo4j数据库: {uri}")
            except Exception as e:
                raise ConnectionError(f"数据库连接失败: {str(e)}")
        else:
            self.use_database = False
            print("未提供数据库凭据，将使用文件读取模式。")

    def fetch_user_interactions_from_db(self):
        """
        从Neo4j数据库中查询用户-停车场的评分互动关系。

        :return: 字典，键为用户ID，值为用户正向互动的停车场ID列表
        """
        try:
            user_interactions = {}

            # 定义在Neo4j中的Cypher查询
            query = """
            MATCH (u:User)-[r:RATED]->(p:ParkingSpot)
            RETURN u.id AS user_id, p.id AS parking_spot_id, r.grading AS rating
            """

            # 执行查询并获取结果
            result = self.graph.run(query)

            # 遍历查询结果，构建用户与正向评分的停车场ID列表
            for record in result:
                user_id = record["user_id"]
                parking_spot_id = record["parking_spot_id"]
                rating = record["rating"]

                # 如果评分大于等于阈值，记录此互动
                if rating >= self.rating_threshold:
                    if user_id not in user_interactions:
                        user_interactions[user_id] = []
                    user_interactions[user_id].append(parking_spot_id)

            return user_interactions

        except Exception as e:
            raise Exception(f"查询用户-停车场互动数据失败: {str(e)}")

    def fetch_user_interactions_from_file(self, input_file):
        """
        从文件中读取用户-停车场的评分互动数据。

        :param input_file: 文件路径，文件格式：停车位ID,用户ID,评分
        :return: 字典，键为用户ID，值为用户正向互动的停车场ID列表
        """
        user_interactions = {}
        try:
            with open(input_file, 'r', encoding='utf-8') as infile:
                for line in infile:
                    # 跳过文件中的标题行（如果有的话）
                    if line.startswith("停车位ID"):
                        continue

                    # 拆分每行数据，格式：停车位ID, 用户ID, 评分
                    parking_spot_id, user_id, rating = line.strip().split(',')

                    # 将评分转换为浮点数
                    rating = float(rating)

                    # 如果评分大于等于阈值，记录该互动
                    if rating >= self.rating_threshold:
                        if user_id not in user_interactions:
                            user_interactions[user_id] = []
                        user_interactions[user_id].append(parking_spot_id)

            print(f"成功从文件 {input_file} 读取数据")
            return user_interactions

        except Exception as e:
            raise Exception(f"读取文件失败: {str(e)}")

    def save_to_file(self, user_interactions, output_file):
        """
        将用户与停车场的正向互动数据保存为训练格式的文件。

        :param user_interactions: 字典，键为用户ID，值为用户正向互动的停车场ID列表
        :param output_file: 保存的文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # 将结果写入文件
            with open(output_file, 'w') as outfile:
                for user_id, parking_spots in user_interactions.items():
                    parking_spots_str = ' '.join(map(str, parking_spots))
                    outfile.write(f"{user_id} {parking_spots_str}\n")

            print(f"转换完成，数据已写入: {output_file}")

        except Exception as e:
            raise Exception(f"保存文件时出错: {str(e)}")

    def load_and_save(self, output_file, input_file=None):
        """
        从Neo4j数据库或文件中读取评分数据并保存为训练格式的文件。

        :param output_file: 保存的文件路径
        :param input_file: 从文件读取数据的路径（可选）
        """
        if input_file:
            print("正在从文件中读取用户互动数据...")
            user_interactions = self.fetch_user_interactions_from_file(input_file)
        else:
            print("正在从数据库获取用户互动数据...")
            user_interactions = self.fetch_user_interactions_from_db()

        print("正在保存数据到文件...")
        self.save_to_file(user_interactions, output_file)


if __name__ == "__main__":
    # 数据库连接配置，如果不需要数据库，可以留空
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "your_password"

    # 输出文件路径
    output_file = '../data/all_interactions.txt'

    # 输入文件路径（如果选择从文件加载数据）
    input_file = '../data/original_ratings_old.csv'  # 评分文件的路径

    # 初始化并执行转换，选择是否从文件读取数据
    converter = ParkingDataConverter(uri, username, password, rating_threshold=3.6)

    # 如果有input_file，则从文件读取；否则从数据库读取
    converter.load_and_save(output_file, input_file=input_file)
