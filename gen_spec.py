import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

directory = "./audio"

os.makedirs('./spec', exist_ok=True)
# 遍历目录下所有文件
for filename in os.listdir(directory):
    # 检查文件名是否包含 "_isolation.mp3"
    if "_isolation.mp3" in filename:
        file_path = os.path.join(directory, filename)
        fb = filename.split('_')[0]
        
        # 使用 librosa 读取音频文件为单声道
        y, sr = librosa.load(file_path, sr=8000, mono=True)
        
         # 计算频谱
        n_fft = 256  # 频谱分辨率为512
        hop_length = 64  # 调整 hop length 以匹配时间分辨率
        window = np.blackman(n_fft)  # 使用布莱克曼-哈里斯窗
        S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length, window=window)
        S_db = librosa.amplitude_to_db(abs(S))
        
        # 绘制频谱图
        plt.figure(figsize=(12, 8))
        librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz', 
                                 hop_length=hop_length)
        plt.title(fb)
        plt.savefig(f"./spec/{fb}.png")
        plt.close()
