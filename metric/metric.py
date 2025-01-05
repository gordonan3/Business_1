import time
import pika
import json
import os

log_file = './logs/metric_log.csv'

# Инициализация файла
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write('id,y_true,y_pred,absolute_error\n')

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

# Очереди
channel.queue_declare(queue='y_true')
channel.queue_declare(queue='y_pred')

data_buffer = {}

def callback_y_true(ch, method, properties, body):
    message = json.loads(body)
    message_id = message['id']
    y_true = message['body']
    data_buffer.setdefault(message_id, {})['y_true'] = y_true
    process_data(message_id)

def callback_y_pred(ch, method, properties, body):
    message = json.loads(body)
    message_id = message['id']
    y_pred = message['body']
    data_buffer.setdefault(message_id, {})['y_pred'] = y_pred
    process_data(message_id)

def process_data(message_id):
    if 'y_true' in data_buffer[message_id] and 'y_pred' in data_buffer[message_id]:
        y_true = data_buffer[message_id]['y_true']
        y_pred = data_buffer[message_id]['y_pred']
        absolute_error = abs(y_true - y_pred)

        with open(log_file, 'a') as f:
            f.write(f"{message_id},{y_true},{y_pred},{absolute_error}\n")

        print(f"[{message_id}] Лог записан: y_true={y_true}, y_pred={y_pred}, abs_error={absolute_error}")
        del data_buffer[message_id]

channel.basic_consume(queue='y_true', on_message_callback=callback_y_true, auto_ack=True)
channel.basic_consume(queue='y_pred', on_message_callback=callback_y_pred, auto_ack=True)

print("Сервис metric запущен...")
channel.start_consuming()
