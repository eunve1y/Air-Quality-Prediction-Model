import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 경로 설정
data_folder = "C:/Users/User/Desktop/final_project/datasets/prepared_data/"
model_path = "C:/Users/User/Desktop/final_project/models/saved_model/sky_aqi_model.keras"

# 데이터 로드
def load_data():
    X_test = np.load(os.path.join(data_folder, "X_test.npy"))
    y_test = np.load(os.path.join(data_folder, "y_test.npy"))
    return X_test, y_test

# 모델 평가 및 시각화
def evaluate_model():
    # 테스트 데이터 로드
    X_test, y_test = load_data()

    # 저장된 모델 로드
    model = load_model(model_path)

    # 예측 수행
    y_pred = model.predict(X_test)

    # 평가 지표 계산
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    print(f"Evaluation Results:")
    print(f"MAE: {mae}")
    print(f"MSE: {mse}")
    print(f"RMSE: {rmse}")
    print(f"R² Score: {r2}")

    # 예측 vs 실제 값 시각화
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred, alpha=0.5, edgecolor='k')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel("Actual AQI")
    plt.ylabel("Predicted AQI")
    plt.title("Actual vs Predicted AQI")
    plt.grid(True)
    plt.show()

# 실행
if __name__ == "__main__":
    evaluate_model()
