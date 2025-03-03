import os
import requests
import logging
from multiprocessing import Pool
from itertools import cycle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import hashlib
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# API 키 설정
FLICKR_API_KEYS = ["6089d969a2439e29bfac42c161e969e0", "59dd2d251d722f95987a2ade01e6bc72"]
UNSPLASH_API_KEYS = ["9By842VvJH9-3c-QP_e3xjUrOzSexFOwDSp4kakZiQ4", "Kp5Pu44ePTqwKOQc-G3cJ8L-FhfnRSNjwdza_hUlhho"]

# API 키 순환
flickr_key_cycle = cycle(FLICKR_API_KEYS)
unsplash_key_cycle = cycle(UNSPLASH_API_KEYS)

# 저장 경로 설정
output_folder = "C:/Users/User/Desktop/final_project/datasets/images/"
progress_file_path = os.path.join(output_folder, "downloaded_progress.txt")
os.makedirs(output_folder, exist_ok=True)

# 중복 파일 확인을 위한 파일 해시 저장
downloaded_hashes = set()

# 기존 진행 파일 불러오기
if os.path.exists(progress_file_path):
    with open(progress_file_path, "r") as progress_file:
        downloaded_hashes = set(progress_file.read().splitlines())

# 서울시 전역구 리스트
seoul_districts = [
    "Gangnam-gu", "Songpa-gu", "Jongno-gu", "Seocho-gu", "Mapo-gu",
    "Yongsan-gu", "Nowon-gu", "Gwangjin-gu", "Dongjak-gu", "Geumcheon-gu",
    "Guro-gu", "Yangcheon-gu", "Gangseo-gu", "Seodaemun-gu", "Eunpyeong-gu",
    "Jungnang-gu", "Seongdong-gu", "Dongdaemun-gu", "Gangbuk-gu", "Dobong-gu",
    "Jung-gu", "Gwanak-gu", "Gangdong-gu", "Yeongdeungpo-gu", "Seongbuk-gu"
]

# 파일의 해시 값을 계산
def calculate_file_hash(content):
    return hashlib.md5(content).hexdigest()

# Flickr 이미지 다운로드
def fetch_flickr_images(args):
    district, num_images = args
    api_key = next(flickr_key_cycle)
    image_count, page = 0, 1

    while image_count < num_images:
        url = f"https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={api_key}&tags=sky,{district}&format=json&nojsoncallback=1&per_page=500&page={page}"
        response = requests.get(url)
        data = response.json()
        if "photos" not in data or "photo" not in data["photos"]:
            logging.error(f"Flickr API error for {district}: {data}")
            break

        for photo in data["photos"]["photo"]:
            photo_url = f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}.jpg"
            try:
                image_response = requests.get(photo_url)
                if image_response.status_code == 200:
                    file_hash = calculate_file_hash(image_response.content)
                    if file_hash in downloaded_hashes:
                        logging.info(f"Duplicate image skipped for {district}: {photo_url}")
                        continue

                    downloaded_hashes.add(file_hash)
                    image_name = f"flickr_{district}_sky_{image_count:05d}.jpg"
                    with open(os.path.join(output_folder, image_name), "wb") as f:
                        f.write(image_response.content)
                    logging.info(f"Downloaded Flickr image for {district}: {image_name}")
                    image_count += 1
                    if image_count >= num_images:
                        break
            except Exception as e:
                logging.error(f"Error downloading Flickr image: {e}")
        page += 1

# Unsplash 이미지 다운로드
def fetch_unsplash_images(args):
    district, num_images = args
    api_key = next(unsplash_key_cycle)
    image_count, page = 0, 1

    while image_count < num_images:
        url = f"https://api.unsplash.com/search/photos?query=sky,{district}&per_page=30&page={page}"
        headers = {"Authorization": f"Client-ID {api_key}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                logging.error(f"Unsplash API limit exceeded for {district}. Skipping...")
                break
            elif response.status_code != 200:
                logging.error(f"Unsplash API error for {district}: {response.status_code}")
                break

            data = response.json()
            if "results" not in data:
                logging.error(f"Unexpected Unsplash response for {district}: {data}")
                break

            for result in data["results"]:
                image_url = result["urls"]["regular"]
                try:
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        file_hash = calculate_file_hash(image_response.content)
                        if file_hash in downloaded_hashes:
                            logging.info(f"Duplicate image skipped for {district}: {image_url}")
                            continue

                        downloaded_hashes.add(file_hash)
                        image_name = f"unsplash_{district}_sky_{image_count:05d}.jpg"
                        with open(os.path.join(output_folder, image_name), "wb") as f:
                            f.write(image_response.content)
                        logging.info(f"Downloaded Unsplash image for {district}: {image_name}")
                        image_count += 1
                        if image_count >= num_images:
                            break
                except Exception as e:
                    logging.error(f"Error downloading Unsplash image: {e}")
            page += 1
        except Exception as e:
            logging.error(f"Error fetching Unsplash data for {district}: {e}")
            break

# Google 이미지 크롤링
def fetch_google_images(args):
    district, num_images = args
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    image_count, page = 0, 0

    try:
        while image_count < num_images:
            search_url = f"https://www.google.com/search?tbm=isch&q=sky+{district}&start={page*30}"
            driver.get(search_url)
            image_elements = driver.find_elements(By.CSS_SELECTOR, "img")

            for img_elem in image_elements:
                if image_count >= num_images:
                    break

                try:
                    img_url = img_elem.get_attribute("src")
                    
                    # URL 필터링: 잘못된 URL 건너뛰기
                    if not img_url or "google.com" in img_url or "data:" in img_url:
                        logging.info(f"Skipped invalid URL: {img_url}")
                        continue

                    image_response = requests.get(img_url)
                    if image_response.status_code == 200:
                        file_hash = calculate_file_hash(image_response.content)
                        if file_hash in downloaded_hashes:
                            logging.info(f"Duplicate image skipped for {district}: {img_url}")
                            continue

                        downloaded_hashes.add(file_hash)
                        image_name = f"google_{district}_sky_{image_count:05d}.jpg"
                        with open(os.path.join(output_folder, image_name), "wb") as f:
                            f.write(image_response.content)
                        logging.info(f"Downloaded Google image for {district}: {image_name}")
                        image_count += 1
                except Exception as e:
                    logging.error(f"Error downloading Google image for {district}: {e}")
            page += 1
    except Exception as e:
        logging.error(f"Error fetching Google images for {district}: {e}")
    finally:
        driver.quit()

# 병렬 다운로드 실행
def download_images():
    flickr_args = [(district, 1000) for district in seoul_districts]
    unsplash_args = [(district, 1000) for district in seoul_districts]
    google_args = [(district, 1000) for district in seoul_districts]

    with Pool(processes=4) as pool:
        pool.map(fetch_flickr_images, flickr_args)
        pool.map(fetch_unsplash_images, unsplash_args)
        pool.map(fetch_google_images, google_args)

    # 진행 상태 파일 저장
    with open(progress_file_path, "w") as progress_file:
        progress_file.write("\n".join(downloaded_hashes))

# 실행
if __name__ == "__main__":
    logging.info("Starting image download...")
    download_images()
    logging.info("Image download completed.")
