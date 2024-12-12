import concurrent
import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import requests_cache
from tqdm import tqdm
import random

# Enable requests caching to avoid repeated API requests
requests_cache.install_cache('api_cache', expire_after=3600)  # Cache for 1 hour


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
        (
            f"https://restapi.amap.com/v3/place/text?key={api_key}&city={city}&types={code}&offset=20&page=1&extensions=base")
        for _, codes in weighted_requests for code in codes
    ]

    for url in tqdm(urls, desc="Fetching parking data"):
        data = fetch_parking_data(url)
        if data and data.get('status') == '1':
            for poi in data.get('pois', []):
                parking_lots.append({
                    'name': poi.get('name', '未知停车场'),
                    'location': poi.get('location', '0,0'),
                    'typecode': poi.get('typecode', '未知代码'),
                    'type': '未知类型'
                })
    return parking_lots


def generate_user_preferences(num_users):
    preferences = {}
    for user_id in range(1, num_users + 1):
        preferences[user_id] = {
            'parking_fee_weight': np.random.randint(1, 6),
            'driving_distance_weight': np.random.randint(1, 6),
            'near_elevator_weight': np.random.randint(1, 6),
            'has_surveillance_weight': np.random.randint(1, 6)
        }
    pref_df = pd.DataFrame.from_dict(preferences, orient='index')
    pref_df.index.name = '用户ID'
    pref_df.to_csv("../data/user_preferences.csv")
    return preferences


def calculate_base_rating(parking_spot):
    base_rating = 5.0
    if parking_spot['Parking Space Size (0-10)'] > 8:
        base_rating += 0.5
    elif parking_spot['Parking Space Size (0-10)'] < 5:
        base_rating -= 0.5

    if parking_spot['Near Elevator'] == '是':
        base_rating += 0.5  # 增加靠近电梯的评分加成
    if parking_spot['Has Surveillance'] == '是':
        base_rating += 0.4  # 增加监控的评分加成
    if parking_spot['Driving Distance (meters)'] > 1000:
        base_rating -= 0.7
    elif parking_spot['Driving Distance (meters)'] < 500:
        base_rating += 0.3

    return base_rating


def calculate_adjusted_rating(base_rating, parking_spot, user_preferences):
    adjusted_rating = base_rating
    adjusted_rating -= user_preferences['parking_fee_weight'] * (parking_spot['Parking Fee (CNY/hour)'] / 10)
    adjusted_rating -= user_preferences['driving_distance_weight'] * (parking_spot['Driving Distance (meters)'] / 1000)
    adjusted_rating += user_preferences['near_elevator_weight'] if parking_spot['Near Elevator'] == '是' else 0
    adjusted_rating += user_preferences['has_surveillance_weight'] if parking_spot['Has Surveillance'] == '是' else 0

    # 使用 Beta 分布生成右偏分布调整
    alpha, beta = 2, 5
    skewed_value = np.random.beta(alpha, beta)
    adjusted_rating += skewed_value

    # 限制评分在 1 到 5 之间
    adjusted_rating = np.clip(adjusted_rating, 1, 5)

    return adjusted_rating


def generate_ratings_for_user(user_id, parking_spots_df, user_preferences, min_ratings_per_user, max_ratings_per_user):
    num_ratings = np.random.randint(min_ratings_per_user, max_ratings_per_user)
    rated_spots = np.random.choice(parking_spots_df['ID'], num_ratings, replace=False)
    user_ratings = []

    for spot_id in rated_spots:
        spot = parking_spots_df.loc[parking_spots_df['ID'] == spot_id].iloc[0]
        base_rating = calculate_base_rating(spot)
        adjusted_rating = calculate_adjusted_rating(base_rating, spot, user_preferences[user_id])
        user_ratings.append([spot_id, user_id, round(adjusted_rating, 1)])

    return user_ratings


def generate_parking_data(num_users, num_parking_spots, min_ratings_per_user, max_ratings_per_user, parking_lots,
                          seed=42):
    np.random.seed(seed)
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
    parking_spots_df = pd.DataFrame(parking_data)
    user_preferences = generate_user_preferences(num_users)
    ratings = []
    with ProcessPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(generate_ratings_for_user, user_id, parking_spots_df, user_preferences,
                                   min_ratings_per_user, max_ratings_per_user)
                   for user_id in range(1, num_users + 1)]

        for future in tqdm(concurrent.futures.as_completed(futures), total=num_users,
                           desc="Generating ratings for all users"):
            ratings.extend(future.result())

    ratings_df = pd.DataFrame(ratings, columns=['停车位ID', '用户ID', '评分'])
    parking_spots_df.to_csv('../data/parking_spots_with_coords.csv', index=False)
    ratings_df.to_csv('../data/original_ratings_old.csv', index=False)

    return parking_spots_df, ratings_df


if __name__ == '__main__':
    num_users = 29800
    num_parking_spots = 49800
    min_ratings_per_user = 20
    max_ratings_per_user = 40
    city = '福州'
    api_key = 'e56fa4a559bd7aab379f8d50bd5818f7'
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

    print("Fetching parking lot data from Amap API...")
    parking_lots = fetch_parking_lots_concurrently(city, api_key, weighted_requests)
    print(f"Fetched {len(parking_lots)} parking lots.")
    print("Generating parking data and user ratings...")
    parking_spots, ratings_df = generate_parking_data(num_users, num_parking_spots, min_ratings_per_user,
                                                      max_ratings_per_user, parking_lots)
    print("Parking spot information:")
    print(parking_spots.head())
    print("\nUser ratings:")
    print(ratings_df.head())
