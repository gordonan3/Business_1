import pika
import json
import numpy as np
import pickle
import sklearn
from sklearn.linear_model import LinearRegression

# Загружаем обученную модель
with open('./model.pkl', 'rb') as f:
    model = pickle.load(f)
print("Модель успешно загружена.")

# Подключение к RabbitMQ
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        print("Соединение с RabbitMQ установлено.")
        break
    except pika.exceptions.AMQPConnectionError:
        print("RabbitMQ недоступен, повторная попытка через 5 секунд...")
        time.sleep(5)

# Очередь для признаков
channel.queue_declare(queue='features')

def callback(ch, method, properties, body):
    message = json.loads(body)
    message_id = message['id']
    features = np.array(message['body']).reshape(1, -1)

    # Генерируем предсказание
    y_pred = model.predict(features)[0]

    # Отправляем предсказание в очередь `y_pred`
    message_y_pred = {'id': message_id, 'body': y_pred}
    channel.basic_publish(exchange='', routing_key='y_pred', body=json.dumps(message_y_pred))
    print(f"[{message_id}] Предсказание отправлено: y_pred={y_pred}")

channel.basic_consume(queue='features', on_message_callback=callback, auto_ack=True)

print("Сервис predictor запущен...")
channel.start_consuming()
