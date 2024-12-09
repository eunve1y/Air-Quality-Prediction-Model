import os
import pandas as pd

# 경로 설정
mapping_file = "C:/Users/User/Desktop/final_project/datasets/mappings/sky_aqi_mapping.csv"
filtered_images_folder = "C:/Users/User/Desktop/final_project/datasets/filtered_images/"
output_mapping_file = "C:/Users/User/Desktop/final_project/datasets/mappings/filtered_sky_aqi_mapping.csv"

def update_mapping():
    # 매핑 데이터 로드
    mapping_data = pd.read_csv(mapping_file)

    # 필터링된 이미지 파일 목록
    filtered_images = set(os.listdir(filtered_images_folder))

    # 필터링된 매핑 데이터
    filtered_mapping = mapping_data[mapping_data["Image Name"].isin(filtered_images)]

    # 업데이트된 매핑 파일 저장
    filtered_mapping.to_csv(output_mapping_file, index=False)
    print(f"Updated mapping file saved to: {output_mapping_file}")

# 실행
if __name__ == "__main__":
    update_mapping()
