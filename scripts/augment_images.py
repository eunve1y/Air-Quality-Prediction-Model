import os
import cv2
import numpy as np
from pathlib import Path
import random

input_folder = "C:/Users/User/Desktop/final_project/datasets/images/"
output_folder = "C:/Users/User/Desktop/final_project/datasets/augmented_images/"
os.makedirs(output_folder, exist_ok=True)

def apply_cutmix(image1, image2, image_name, output_path, existing_files):
    height, width, _ = image1.shape
    cut_x = np.random.randint(width // 4, 3 * width // 4)
    cut_y = np.random.randint(height // 4, 3 * height // 4)

    cutmix_image = image1.copy()
    cutmix_image[cut_y:, cut_x:] = image2[cut_y:, cut_x:]

    output_file_name = f"{image_name}_cutmix.jpg"
    output_file_path = os.path.join(output_path, output_file_name)
    if output_file_name not in existing_files:
        cv2.imwrite(output_file_path, cutmix_image)
        print(f"Saved CutMix image: {output_file_path}")
        existing_files.add(output_file_name)

def apply_mixup(image1, image2, image_name, output_path, existing_files, alpha=0.2):
    mixup_image = cv2.addWeighted(image1, alpha, image2, 1 - alpha, 0)
    
    output_file_name = f"{image_name}_mixup.jpg"
    output_file_path = os.path.join(output_path, output_file_name)
    if output_file_name not in existing_files:
        cv2.imwrite(output_file_path, mixup_image)
        print(f"Saved MixUp image: {output_file_path}")
        existing_files.add(output_file_name)

def augment_image(image, image_name, output_path, other_images, existing_files):
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

    # 5. 증강된 이미지 저장 (중복 방지)
    for aug_image, aug_name in augmented_images:
        output_file_path = os.path.join(output_path, aug_name)
        if aug_name not in existing_files:
            cv2.imwrite(output_file_path, aug_image)
            print(f"Saved augmented image: {output_file_path}")
            existing_files.add(aug_name)

    # 6. CutMix 및 MixUp
    if other_images:
        random_image_path = random.choice(other_images)
        random_image = cv2.imread(random_image_path)
        if random_image is not None and random_image.shape == image.shape:
            apply_cutmix(image, random_image, image_name, output_path, existing_files)
            apply_mixup(image, random_image, image_name, output_path, existing_files)

def augment_images():
    existing_files = set(os.listdir(output_folder))  # 이미 존재하는 파일 확인
    image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".jpg")]

    for image_file in image_files:
        image_name = Path(image_file).stem
        image = cv2.imread(image_file)

        if image is None:
            print(f"Failed to load image: {image_file}")
            continue

        augment_image(image, image_name, output_folder, image_files, existing_files)

if __name__ == "__main__":
    augment_images()
