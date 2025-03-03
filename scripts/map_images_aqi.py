import os
import pandas as pd
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 경로 설정
image_folders = [
    "C:/Users/User/Desktop/final_project/datasets/filtered_images/",
    "C:/Users/User/Desktop/final_project/datasets/augmented_images/"
]
aqi_data_file = "C:/Users/User/Desktop/final_project/datasets/mappings/aqi_data.csv"
output_file = "C:/Users/User/Desktop/final_project/datasets/mappings/filtered_sky_aqi_mapping.csv"

def extract_district_from_filename(filename):
    """
    이미지 파일명에서 지역명 추출.
    파일명 예: unsplash_Gangbuk-gu_sky_25.jpg
    반환값: Gangbuk-gu 또는 None
    """
    parts = filename.split("_")
    for part in parts:
        if "-gu" in part:  # "-gu" 포함된 부분이 지역명
            return part
    return None  # 지역명을 찾지 못하면 None 반환

def map_images_to_aqi():
    # AQI 데이터 로드
    aqi_data = pd.read_csv(aqi_data_file)
    logging.info(f"AQI data loaded: {len(aqi_data)} rows")

    # 결과 저장을 위한 리스트
    mappings = []

    # 각 이미지 폴더 처리
    for image_folder in image_folders:
        if not os.path.exists(image_folder):
            logging.warning(f"Folder does not exist: {image_folder}")
            continue

        for image_file in os.listdir(image_folder):
            if not image_file.endswith((".jpg", ".png")):
                continue

            # 파일명에서 지역명 추출
            district_name = extract_district_from_filename(image_file)
            if district_name is None:
                logging.warning(f"Skipping file with no district information: {image_file}")
                continue  # 지역명을 찾지 못하면 건너뜀

            # AQI 데이터와 매핑
            matching_aqi = aqi_data[aqi_data["Station"].str.contains(district_name, case=False, na=False)]
            if matching_aqi.empty:
                logging.warning(f"No AQI data found for district: {district_name}")
                continue

            # 첫 번째 매칭된 데이터 사용
            aqi_info = matching_aqi.iloc[0]
            mappings.append({
                "Image Name": image_file,
                "District": aqi_info["Station"],
                "PM2.5": aqi_info["PM2.5"],
                "PM10": aqi_info["PM10"],
                "Dominant Pollutant": aqi_info["Dominant Pollutant"],
                "Timestamp": aqi_info["Timestamp"],
                "Temperature": aqi_info["Temperature"],
                "Humidity": aqi_info["Humidity"]
            })

    # 결과 저장
    output_df = pd.DataFrame(mappings)
    output_df.to_csv(output_file, index=False, encoding="utf-8")
    logging.info(f"Image-to-AQI mapping completed. Saved to {output_file}")

if __name__ == "__main__":
    map_images_to_aqi()
