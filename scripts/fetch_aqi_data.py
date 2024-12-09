import os
import requests
import csv

# AQICN API 키
AQICN_API_KEY = "21ead146041322b2c36e3482a0c646e5402f8c70"

# 대기질 데이터 저장 경로
output_file = "C:/Users/User/Desktop/final_project/datasets/mappings/aqi_data.csv"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# 서울시 전역 구 이름과 좌표
stations_coords = [
    {"name": "Gangnam-gu, Seoul", "lat": 37.517562, "lon": 127.047282},
    {"name": "Songpa-gu, Seoul", "lat": 37.502685, "lon": 127.112315},
    {"name": "Jongno-gu, Seoul", "lat": 37.572025, "lon": 126.979367},
    {"name": "Seocho-gu, Seoul", "lat": 37.483577, "lon": 127.032718},
    {"name": "Mapo-gu, Seoul", "lat": 37.554682, "lon": 126.910072},
    {"name": "Yongsan-gu, Seoul", "lat": 37.531100, "lon": 126.981748},
    {"name": "Nowon-gu, Seoul", "lat": 37.654916, "lon": 127.056622},
    {"name": "Gwangjin-gu, Seoul", "lat": 37.538520, "lon": 127.082124},
    {"name": "Dongjak-gu, Seoul", "lat": 37.512398, "lon": 126.939627},
    {"name": "Geumcheon-gu, Seoul", "lat": 37.456872, "lon": 126.895961},
    {"name": "Guro-gu, Seoul", "lat": 37.495403, "lon": 126.887549},
    {"name": "Yangcheon-gu, Seoul", "lat": 37.517018, "lon": 126.866831},
    {"name": "Gangseo-gu, Seoul", "lat": 37.566283, "lon": 126.849548},
    {"name": "Seodaemun-gu, Seoul", "lat": 37.582577, "lon": 126.935203},
    {"name": "Eunpyeong-gu, Seoul", "lat": 37.617612, "lon": 126.922700},
    {"name": "Jungnang-gu, Seoul", "lat": 37.595658, "lon": 127.093246},
    {"name": "Seongdong-gu, Seoul", "lat": 37.563940, "lon": 127.036667},
    {"name": "Dongdaemun-gu, Seoul", "lat": 37.574495, "lon": 127.040544},
    {"name": "Gangbuk-gu, Seoul", "lat": 37.639723, "lon": 127.011302},
    {"name": "Dobong-gu, Seoul", "lat": 37.665860, "lon": 127.031767},
    {"name": "Jung-gu, Seoul", "lat": 37.557353, "lon": 126.994370},
    {"name": "Gwanak-gu, Seoul", "lat": 37.478396, "lon": 126.951462},
    {"name": "Gangdong-gu, Seoul", "lat": 37.530125, "lon": 127.123760},
]

# AQICN에서 대기질 데이터 가져오기
def fetch_aqi_data():
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["district", "latitude", "longitude", "aqi", "dominant_pollutant", "timestamp"])

        for station in stations_coords:
            url = f"https://api.waqi.info/feed/geo:{station['lat']};{station['lon']}/?token={AQICN_API_KEY}"
            try:
                response = requests.get(url, timeout=10)  # 타임아웃 추가
                response.raise_for_status()
                data = response.json()

                if "data" in data and "aqi" in data["data"]:
                    aqi = data["data"]["aqi"]
                    dominant_pollutant = data["data"].get("dominentpol", "Unknown")
                    timestamp = data["data"]["time"]["iso"]

                    writer.writerow([station["name"], station["lat"], station["lon"], aqi, dominant_pollutant, timestamp])
                    print(f"Fetched AQI for {station['name']}: AQI={aqi}, Pollutant={dominant_pollutant}")
                else:
                    print(f"Failed to fetch AQI for {station['name']} (No data).")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {station['name']}: {e}")
            except KeyError as e:
                print(f"Data format error for {station['name']}: {e}")


# 실행
if __name__ == "__main__":
    fetch_aqi_data()
