import numpy as np
import pandas as pd
import requests
import requests_cache
from tqdm import tqdm

# 启用请求缓存
requests_cache.install_cache('api_cache', expire_after=3600)


def fetch_parking_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request failed for URL {url}: {e}")
        return None


def fetch_parking_lots_concurrently(city, api_key, weighted_requests):
    parking_lots = []
    urls = [
        f"https://restapi.amap.com/v3/place/text?key={api_key}&city={city}&types={code}&offset=20&page=1&extensions=base"
        for _, codes in weighted_requests for code in codes
    ]

    for url in tqdm(urls, desc="Fetching parking data"):
        data = fetch_parking_data(url)
        if data and data.get('status') == '1':
            for poi in data.get('pois', []):
                parking_lots.append({
                    'name': poi.get('name', '未知停车场'),
                    'location': poi.get('location', '0,0')
                })
    return parking_lots


def generate_parking_data(num_parking_spots):
    """生成具有随机属性的停车位数据"""
    parking_data = {
        'ID': np.arange(1, num_parking_spots + 1),
        'Driving Distance (meters)': np.random.randint(50, 2000, num_parking_spots),
        'Walking Distance (meters)': np.random.randint(10, 1000, num_parking_spots),
        'Time to Find Parking (minutes)': np.random.randint(1, 20, num_parking_spots),
        'Parking Space Size (0-10)': np.random.randint(4, 10, num_parking_spots),
        'Parking Fee (CNY/hour)': np.round(np.random.uniform(2, 20, num_parking_spots), 0),
        'Near Elevator': np.random.choice(['是', '否'], size=num_parking_spots, p=[0.4, 0.6]),
        'Has Surveillance': np.random.choice(['是', '否'], size=num_parking_spots, p=[0.6, 0.4])
    }
    return pd.DataFrame(parking_data)


if __name__ == '__main__':
    ##################################################################
    city = '福州'
    api_key = 'e56fa4a559bd7aab379f8d50bd5818f7'
    fixed_num_parking_spots = 185973  # 定义你想生成的固定停车位数量
    ##################################################################
    type_codes = {
        '商场': (['060101', '060102'], 3),
        '火车站': (['150202'], 1),
        '机场': (['150101'], 1),
        '停车场': (['150900'], 5),
    }

    weighted_requests = []
    for parking_type, (codes, weight) in type_codes.items():
        for _ in range(weight):
            weighted_requests.append((parking_type, codes))

    parking_lots = fetch_parking_lots_concurrently(city, api_key, weighted_requests)

    parking_spots_df = generate_parking_data(fixed_num_parking_spots)  # 使用固定数量
    parking_spots_df.to_csv('data/parking_spots_with_coords.csv', index=False)
    print("Parking spot information:")
    print(parking_spots_df.head())
