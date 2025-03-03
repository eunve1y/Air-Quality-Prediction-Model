import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, explained_variance_score
from scipy.stats import pearsonr
from tensorflow.keras.models import load_model

# 경로 설정
data_dir = "C:/Users/User/Desktop/final_project/datasets/prepared_data/"
model_path = "C:/Users/User/Desktop/final_project/models/saved_model/vit_model"
results_dir = "C:/Users/User/Desktop/final_project/results/"
os.makedirs(results_dir, exist_ok=True)

# 데이터 로드
def load_data():
    X_test = np.load(os.path.join(data_dir, "X_test.npy"))
    y_test = np.load(os.path.join(data_dir, "y_test.npy"))
    return X_test, y_test

# 평가 및 시각화
def evaluate_model():
    # 데이터 로드
    X_test, y_test = load_data()
    
    # 모델 로드
    model = load_model(model_path)
    
    # 예측 수행
    y_pred = model.predict(X_test)
    
    # 성능 평가 지표 계산
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    explained_variance = explained_variance_score(y_test, y_pred)
    pearson_corr, _ = pearsonr(y_test.flatten(), y_pred.flatten())
    
    # 결과 출력
    print(f"Evaluation Results:")
    print(f"MAE: {mae:.4f}")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R² Score: {r2:.4f}")
    print(f"Explained Variance: {explained_variance:.4f}")
    print(f"Pearson Correlation: {pearson_corr:.4f}")
    
    # 결과 저장
    results = {
        "Metric": ["MAE", "MSE", "RMSE", "R² Score", "Explained Variance", "Pearson Correlation"],
        "Value": [mae, mse, rmse, r2, explained_variance, pearson_corr]
    }
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(results_dir, "evaluation_results.csv"), index=False)
    
    # 시각화
    visualize_results(y_test, y_pred)

# 시각화 함수
def visualize_results(y_test, y_pred):
    # Actual vs Predicted
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred, alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2, label="Ideal Prediction")
    plt.xlabel("Actual AQI")
    plt.ylabel("Predicted AQI")
    plt.title("Actual vs Predicted AQI")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(results_dir, "actual_vs_predicted.png"))
    plt.show()

    # Residuals Analysis
    residuals = y_test.flatten() - y_pred.flatten()
    plt.figure(figsize=(8, 6))
    plt.hist(residuals, bins=30, color="blue", alpha=0.7)
    plt.axvline(x=0, color="r", linestyle="--", label="Zero Residual Line")
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.title("Residuals Analysis")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(results_dir, "residuals_analysis.png"))
    plt.show()

# 실행
if __name__ == "__main__":
    evaluate_model()
