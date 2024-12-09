import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import cv2

# 경로 설정
mapping_file = "C:/Users/User/Desktop/final_project/datasets/mappings/filtered_sky_aqi_mapping.csv"
images_folder = "C:/Users/User/Desktop/final_project/datasets/filtered_images/"
output_folder = "C:/Users/User/Desktop/final_project/datasets/prepared_data/"
os.makedirs(output_folder, exist_ok=True)

# 데이터 준비 함수
def prepare_data():
    # 매핑 데이터 불러오기
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"[ERROR] Mapping file not found: {mapping_file}")

    mapping_data = pd.read_csv(mapping_file)

    # 매핑 파일 검증
    required_columns = ["Image Name", "AQI"]
    for col in required_columns:
        if col not in mapping_data.columns:
            raise ValueError(f"[ERROR] Required column '{col}' not found in mapping file.")

    # 이미지와 AQI 데이터 준비
    images = []
    labels = []

    for index, row in mapping_data.iterrows():
        image_name = row["Image Name"]
        aqi = row["AQI"]

        image_path = os.path.join(images_folder, image_name)
        if not os.path.exists(image_path):
            print(f"[WARNING] Image not found: {image_path}")
            continue

        # 이미지 로드 및 전처리
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"[WARNING] Failed to load image: {image_path}")
                continue

            # 이미지 크기 조정 (128x128)
            image = cv2.resize(image, (128, 128))
            images.append(image)
            labels.append(aqi)
        except Exception as e:
            print(f"[ERROR] Error processing image {image_path}: {e}")
            continue

    # 데이터 크기 확인
    print(f"[INFO] Number of valid images: {len(images)}")
    print(f"[INFO] Number of valid labels: {len(labels)}")

    if len(images) < 3:  # 최소 샘플 수 확인
        print("[ERROR] Not enough data to split into train/val/test. Please check your data.")
        return

    # 배열 변환 및 정규화
    try:
        images = np.array(images, dtype="float32") / 255.0  # 픽셀 값 정규화
        labels = np.array(labels)
    except Exception as e:
        print(f"[ERROR] Error converting images or labels to numpy arrays: {e}")
        return

    # 데이터 분리 (Train: 70%, Validation: 15%, Test: 15%)
    try:
        X_train, X_temp, y_train, y_temp = train_test_split(images, labels, test_size=0.3, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    except Exception as e:
        print(f"[ERROR] Data splitting failed: {e}")
        return

    # 데이터 저장
    try:
        np.save(os.path.join(output_folder, "X_train.npy"), X_train)
        np.save(os.path.join(output_folder, "X_val.npy"), X_val)
        np.save(os.path.join(output_folder, "X_test.npy"), X_test)
        np.save(os.path.join(output_folder, "y_train.npy"), y_train)
        np.save(os.path.join(output_folder, "y_val.npy"), y_val)
        np.save(os.path.join(output_folder, "y_test.npy"), y_test)
    except Exception as e:
        print(f"[ERROR] Failed to save prepared data: {e}")
        return

    print("[INFO] Data preparation completed!")
    print(f"[INFO] Train: {X_train.shape}, Validation: {X_val.shape}, Test: {X_test.shape}")

# 실행
if __name__ == "__main__":
    prepare_data()
