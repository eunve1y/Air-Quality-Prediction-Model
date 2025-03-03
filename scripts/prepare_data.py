import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import cv2
from multiprocessing import Pool, Manager
import logging
import h5py

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 경로 설정
mapping_file = "C:/Users/User/Desktop/final_project/datasets/mappings/filtered_sky_aqi_mapping.csv"
image_folders = [
    "C:/Users/User/Desktop/final_project/datasets/filtered_images/",
    "C:/Users/User/Desktop/final_project/datasets/augmented_images/"
]
output_folder = "C:/Users/User/Desktop/final_project/datasets/prepared_data/"
os.makedirs(output_folder, exist_ok=True)

# HDF5 파일 경로
h5_file_path = os.path.join(output_folder, "prepared_data.h5")

# 이미지 처리 함수
def process_image(args):
    row, image_folders = args
    image_name = row["Image Name"]
    pm25 = row["PM2.5"]

    # 여러 폴더에서 이미지 검색
    image_path = None
    for folder in image_folders:
        potential_path = os.path.join(folder, image_name)
        if os.path.exists(potential_path):
            image_path = potential_path
            break

    if not image_path:
        return None, None

    # 이미지 로드 및 전처리
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None, None

        # 이미지 크기 조정 (128x128)
        image = cv2.resize(image, (128, 128))
        return image, pm25
    except Exception as e:
        logging.error(f"[ERROR] Error processing image {image_path}: {e}")
        return None, None

# 데이터 준비 함수
def prepare_data():
    # 매핑 데이터 불러오기
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"[ERROR] Mapping file not found: {mapping_file}")

    mapping_data = pd.read_csv(mapping_file)

    # 매핑 파일 검증
    required_columns = ["Image Name", "PM2.5"]
    for col in required_columns:
        if col not in mapping_data.columns:
            raise ValueError(f"[ERROR] Required column '{col}' not found in mapping file.")

    logging.info(f"[INFO] Mapping file loaded with {len(mapping_data)} rows.")

    # 병렬 처리 설정
    with Manager() as manager:
        results = []
        with Pool(processes=os.cpu_count()) as pool:
            for idx, (image, label) in enumerate(
                pool.imap(process_image, [(row, image_folders) for _, row in mapping_data.iterrows()], chunksize=100)
            ):
                if image is not None:
                    results.append((image, label))
                if idx % 1000 == 0:
                    logging.info(f"[INFO] Processed {idx} images so far...")

        # 유효한 데이터 필터링
        images, labels = zip(*[(img, lbl) for img, lbl in results if img is not None])
        logging.info(f"[INFO] Number of valid images: {len(images)}")

        if len(images) < 3:  # 최소 샘플 수 확인
            logging.error("[ERROR] Not enough data to split into train/val/test. Please check your data.")
            return

        # 데이터 저장 (HDF5 포맷 사용)
        try:
            with h5py.File(h5_file_path, "w") as hf:
                hf.create_dataset("images", data=np.array(images, dtype="uint8"), compression="gzip")
                hf.create_dataset("labels", data=np.array(labels, dtype="float32"), compression="gzip")
            logging.info(f"[INFO] Data saved to HDF5 file: {h5_file_path}")
        except Exception as e:
            logging.error(f"[ERROR] Failed to save data to HDF5 file: {e}")
            return

        # 데이터 분리 및 저장 (Train: 70%, Validation: 15%, Test: 15%)
        try:
            X_train, X_temp, y_train, y_temp = train_test_split(images, labels, test_size=0.3, random_state=42)
            X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

            np.save(os.path.join(output_folder, "X_train.npy"), X_train)
            np.save(os.path.join(output_folder, "X_val.npy"), X_val)
            np.save(os.path.join(output_folder, "X_test.npy"), X_test)
            np.save(os.path.join(output_folder, "y_train.npy"), y_train)
            np.save(os.path.join(output_folder, "y_val.npy"), y_val)
            np.save(os.path.join(output_folder, "y_test.npy"), y_test)
        except Exception as e:
            logging.error(f"[ERROR] Failed to save prepared data: {e}")
            return

        logging.info("[INFO] Data preparation completed!")
        logging.info(f"[INFO] Train: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")

# 실행
if __name__ == "__main__":
    prepare_data()
