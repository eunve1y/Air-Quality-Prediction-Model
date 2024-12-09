import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

input_shape = (128, 128, 3)
num_classes = 1  # Regression task

def build_vit_model(input_shape, num_patches=64, projection_dim=64, transformer_layers=12, num_heads=12):
    inputs = keras.Input(shape=input_shape)

    # 패치 분할 및 임베딩
    patches = layers.Conv2D(projection_dim, kernel_size=(16, 16), strides=(16, 16))(inputs)

    # Transformer 블록
    for _ in range(transformer_layers):
        x = layers.MultiHeadAttention(num_heads=num_heads, key_dim=projection_dim)(patches, patches)
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        x = layers.Dense(projection_dim, activation='relu')(x)

    # Classification Token
    x = layers.GlobalAveragePooling2D()(x)
    outputs = layers.Dense(num_classes, activation='linear')(x)

    return keras.Model(inputs, outputs)

def train_model():
    # 데이터 로드
    X_train = np.load("C:/Users/User/Desktop/final_project/datasets/prepared_data/X_train.npy")
    y_train = np.load("C:/Users/User/Desktop/final_project/datasets/prepared_data/y_train.npy")
    X_val = np.load("C:/Users/User/Desktop/final_project/datasets/prepared_data/X_val.npy")
    y_val = np.load("C:/Users/User/Desktop/final_project/datasets/prepared_data/y_val.npy")

    # 모델 빌드
    model = build_vit_model(input_shape=input_shape)
    model.compile(optimizer='adam', loss='mse', metrics=['mae', 'mse'])

    # 모델 학습
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=30,
        batch_size=32,
        verbose=1,
    )

    # 모델 저장
    model.save("C:/Users/User/Desktop/final_project/models/saved_model/sky_aqi_model_vit.keras")

if __name__ == "__main__":
    train_model()
