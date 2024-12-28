import pika
import numpy as np
import json
from datetime import datetime
from sklearn.datasets import load_diabetes
import time

# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)

while True:
    try:
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0])

        # Генерируем уникальный идентификатор
        message_id = datetime.timestamp(datetime.now())

        # Создаём подключение к RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаём очереди
        channel.queue_declare(queue='y_true')
        channel.queue_declare(queue='features')

        # Формируем и отправляем сообщение с правильным ответом
        message_y_true = {
            'id': message_id,
            'body': y[random_row]
        }
        channel.basic_publish(exchange='', routing_key='y_true', body=json.dumps(message_y_true))
        print(f"[{message_id}] Сообщение с правильным ответом отправлено в очередь y_true")

        # Формируем и отправляем сообщение с признаками
        message_features = {
            'id': message_id,
            'body': list(X[random_row])
        }
        channel.basic_publish(exchange='', routing_key='features', body=json.dumps(message_features))
        print(f"[{message_id}] Сообщение с признаками отправлено в очередь features")

        # Закрываем подключение
        connection.close()

        # Задержка перед следующей итерацией
        time.sleep(2)

    except Exception as e:
        print(f"Ошибка: {e}")
