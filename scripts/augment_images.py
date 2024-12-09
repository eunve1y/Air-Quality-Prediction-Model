import os
import cv2
import numpy as np
from pathlib import Path

input_folder = "C:/Users/User/Desktop/final_project/datasets/images/"
output_folder = "C:/Users/User/Desktop/final_project/datasets/augmented_images/"
os.makedirs(output_folder, exist_ok=True)

def augment_image(image, image_name, output_path):
    augmented_images = []

    # 1. 원본 이미지
    augmented_images.append((image, f"{image_name}_original.jpg"))

    # 2. 좌우 반전
    flipped_lr = cv2.flip(image, 1)
    augmented_images.append((flipped_lr, f"{image_name}_flipped_lr.jpg"))

    # 3. 상하 반전
    flipped_ud = cv2.flip(image, 0)
    augmented_images.append((flipped_ud, f"{image_name}_flipped_ud.jpg"))

    # 4. 회전
    for angle in [15, -15, 30, -30]:
        height, width = image.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D((width // 2, height // 2), angle, 1)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
        augmented_images.append((rotated, f"{image_name}_rotated_{angle}.jpg"))

    # 증강된 이미지 저장
    for aug_image, aug_name in augmented_images:
        output_file_path = os.path.join(output_path, aug_name)
        cv2.imwrite(output_file_path, aug_image)
        print(f"Saved augmented image: {output_file_path}")

def augment_images():
    for image_file in os.listdir(input_folder):
        if not image_file.endswith(".jpg"):
            continue
        image_path = os.path.join(input_folder, image_file)
        image_name = Path(image_file).stem
        image = cv2.imread(image_path)

        if image is None:
            print(f"Failed to load image: {image_path}")
            continue

        augment_image(image, image_name, output_folder)

if __name__ == "__main__":
    augment_images()
