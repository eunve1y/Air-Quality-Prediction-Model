import os
import pandas as pd
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 경로 설정
filtered_images_folder = "C:/Users/User/Desktop/final_project/datasets/filtered_images/"
aqi_data_path = "C:/Users/User/Desktop/final_project/datasets/mappings/aqi_data.csv"
output_mapping_path = "C:/Users/User/Desktop/final_project/datasets/mappings/filtered_sky_aqi_mapping.csv"

# 대기질 데이터 로드 함수
def load_aqi_data():
    """
    대기질 데이터를 로드합니다.
    :return: AQI 데이터를 포함한 Pandas DataFrame
    """
    if not os.path.exists(aqi_data_path):
        raise FileNotFoundError(f"AQI data file not found at {aqi_data_path}")
    aqi_data = pd.read_csv(aqi_data_path)
    logging.info(f"AQI data loaded: {aqi_data.shape[0]} rows")
    return aqi_data

# 이미지와 AQI 데이터를 매핑
def map_images_to_aqi():
    """
    필터링된 이미지와 AQI 데이터를 매핑합니다.
    """
    # 이미지 파일 리스트 로드
    image_files = os.listdir(filtered_images_folder)
    if not image_files:
        logging.warning("No filtered images found for mapping.")
        return

    # AQI 데이터 로드
    aqi_data = load_aqi_data()

    # 매핑 결과 저장
    mappings = []
    for image_file in image_files:
        # 이미지 파일명에서 구 이름 추출
        district_name = "_".join(image_file.split("_")[1:2])  # 예: "flickr_Gangnam-gu_sky_0.jpg" -> "Gangnam-gu"

        # AQI 데이터에서 매칭된 구 이름 찾기
        matching_aqi = aqi_data[aqi_data["district"].str.contains(district_name, case=False, na=False)]

        if not matching_aqi.empty:
            aqi = matching_aqi.iloc[0]["aqi"]
            dominant_pollutant = matching_aqi.iloc[0]["dominant_pollutant"]
            timestamp = matching_aqi.iloc[0]["timestamp"]

            mappings.append({
                "Image Name": image_file,
                "District": district_name,
                "AQI": aqi,
                "Dominant Pollutant": dominant_pollutant,
                "Timestamp": timestamp
            })
            logging.info(f"Mapped {image_file} to AQI={aqi}, Pollutant={dominant_pollutant}")
        else:
            logging.warning(f"No AQI data found for district: {district_name}")

    # 매핑 결과 저장
    mapping_df = pd.DataFrame(mappings)
    mapping_df.to_csv(output_mapping_path, index=False)
    logging.info(f"Mapping file created at {output_mapping_path}")


# 실행
if __name__ == "__main__":
    map_images_to_aqi()
