import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

# 데이터 경로
data_folder = "C:/Users/User/Desktop/final_project/datasets/prepared_data/"
model_save_path = "C:/Users/User/Desktop/final_project/models/saved_model/sky_aqi_model.keras"

# Vision Transformer 모델 정의
def build_vit_model(input_shape=(128, 128, 3), num_patches=64, projection_dim=64, transformer_layers=8, num_heads=8):
    inputs = layers.Input(shape=input_shape)

    # 패치 분할 및 임베딩
    patch_size = input_shape[0] // int(num_patches**0.5)  # 각 패치의 크기 계산
    patches = layers.Conv2D(filters=projection_dim, kernel_size=(patch_size, patch_size), strides=(patch_size, patch_size))(inputs)
    patches = layers.Reshape((num_patches, projection_dim))(patches)

    # 패치 임베딩
    pos_embedding = layers.Embedding(input_dim=num_patches, output_dim=projection_dim)(tf.range(start=0, limit=num_patches))
    x = patches + pos_embedding

    # Transformer 블록
    for _ in range(transformer_layers):
        # MultiHeadAttention
        attn_output = layers.MultiHeadAttention(num_heads=num_heads, key_dim=projection_dim)(x, x)
        x = layers.Add()([x, attn_output])  # Residual Connection
        x = layers.LayerNormalization()(x)  # Layer Normalization

        # Feed Forward Network (FFN)
        ffn_output = layers.Dense(projection_dim * 2, activation='relu')(x)
        ffn_output = layers.Dense(projection_dim)(ffn_output)
        x = layers.Add()([x, ffn_output])  # Residual Connection
        x = layers.LayerNormalization()(x)

    # Classification Token (평균 풀링)
    representation = layers.GlobalAveragePooling1D()(x)

    # 회귀 출력
    outputs = layers.Dense(1, activation="linear")(representation)

    return Model(inputs, outputs)

# 데이터 로드
def load_data():
    X_train = np.load(os.path.join(data_folder, "X_train.npy"))
    X_val = np.load(os.path.join(data_folder, "X_val.npy"))
    X_test = np.load(os.path.join(data_folder, "X_test.npy"))
    y_train = np.load(os.path.join(data_folder, "y_train.npy"))
    y_val = np.load(os.path.join(data_folder, "y_val.npy"))
    y_test = np.load(os.path.join(data_folder, "y_test.npy"))
    return X_train, X_val, X_test, y_train, y_val, y_test

# 모델 학습
def train_model():
    # 데이터 로드
    X_train, X_val, X_test, y_train, y_val, y_test = load_data()

    # 모델 정의
    model = build_vit_model(input_shape=(128, 128, 3), num_patches=64, projection_dim=64, transformer_layers=8, num_heads=8)
    model.compile(optimizer=Adam(learning_rate=0.001), loss=MeanSquaredError(), metrics=["mae", "mse"])

    # 콜백 설정
    checkpoint = ModelCheckpoint(filepath=model_save_path, monitor='val_loss', save_best_only=True, verbose=1)
    early_stopping = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1)
    reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1)

    # 모델 학습
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=50,
        batch_size=32,
        callbacks=[checkpoint, early_stopping, reduce_lr]
    )

    # 테스트 데이터 평가
    test_loss, test_mae, test_mse = model.evaluate(X_test, y_test, verbose=1)
    print(f"Test Loss: {test_loss}, Test MAE: {test_mae}, Test MSE: {test_mse}")

if __name__ == "__main__":
    train_model()
