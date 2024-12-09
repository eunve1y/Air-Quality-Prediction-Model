import os
import cv2
import numpy as np
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# 경로 설정
input_folder = "C:/Users/User/Desktop/final_project/datasets/images/"  # 다운로드된 이미지 폴더
output_folder = "C:/Users/User/Desktop/final_project/datasets/filtered_images/"  # 필터링된 이미지 폴더
os.makedirs(output_folder, exist_ok=True)

def is_sky_image(image, blue_threshold=0.3, cloud_threshold=0.1):
    """
    하늘 이미지인지 판별 (파란색과 흰색 비율 기준)
    :param image: 입력 이미지
    :param blue_threshold: 파란색 비율 임계값 (0~1)
    :param cloud_threshold: 흰색 비율 임계값 (0~1)
    :return: 하늘 이미지 여부 (True/False)
    """
    # 이미지 크기와 색상 공간 변환
    height, width = image.shape[:2]
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 파란색 계열 범위
    lower_blue = np.array([90, 50, 50])  # HSV에서 파란색 하한
    upper_blue = np.array([130, 255, 255])  # HSV에서 파란색 상한

    # 흰색 계열 범위
    lower_white = np.array([0, 0, 200])  # HSV에서 흰색 하한
    upper_white = np.array([180, 30, 255])  # HSV에서 흰색 상한

    # 파란색 및 흰색 픽셀 마스크 계산
    blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
    white_mask = cv2.inRange(hsv_image, lower_white, upper_white)

    blue_pixels = cv2.countNonZero(blue_mask)
    white_pixels = cv2.countNonZero(white_mask)

    # 비율 계산
    blue_ratio = blue_pixels / (height * width)
    white_ratio = white_pixels / (height * width)

    return blue_ratio >= blue_threshold or white_ratio >= cloud_threshold

def filter_sky_images():
    """
    폴더에서 하늘 이미지를 필터링하여 저장.
    """
    for file_name in os.listdir(input_folder):
        image_path = os.path.join(input_folder, file_name)

        # 파일 형식 확인 (이미지 파일만 처리)
        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            logging.warning(f"Skipped non-image file: {file_name}")
            continue

        try:
            # 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                logging.error(f"Failed to load image: {image_path}")
                continue

            # 하늘 이미지 판별
            if is_sky_image(image):
                # 하늘 이미지일 경우 출력 폴더로 복사
                output_path = os.path.join(output_folder, file_name)
                cv2.imwrite(output_path, image)
                logging.info(f"Sky image retained: {file_name}")
            else:
                logging.info(f"Non-sky image removed: {file_name}")
        except Exception as e:
            logging.error(f"Error processing file {file_name}: {e}")

# 실행
if __name__ == "__main__":
    logging.info("Starting sky image filtering...")
    filter_sky_images()
    logging.info("Sky image filtering completed.")
