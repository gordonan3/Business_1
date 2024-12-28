import os
import pandas as pd
import matplotlib.pyplot as plt
import time

log_file = './logs/metric_log.csv'
plot_file = './logs/error_distribution.png'

while True:
    try:
        if os.path.exists(log_file):
            df = pd.read_csv(log_file)
            if 'absolute_error' in df.columns:
                plt.figure(figsize=(10, 6))
                plt.hist(df['absolute_error'], bins=30, alpha=0.7, edgecolor='black')
                plt.title('Распределение абсолютных ошибок')
                plt.xlabel('Абсолютная ошибка')
                plt.ylabel('Частота')
                plt.savefig(plot_file)
                plt.close()
                print("Гистограмма обновлена.")
        time.sleep(10)
    except Exception as e:
        print(f"Ошибка: {e}")
