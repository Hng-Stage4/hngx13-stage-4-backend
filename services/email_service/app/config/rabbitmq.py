import pika
from app.config.settings import settings

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        settings.rabbitmq_user,
        settings.rabbitmq_password
    )
    parameters = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        virtual_host=settings.rabbitmq_vhost,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def get_rabbitmq_channel():
    connection = get_rabbitmq_connection()
    return connection.channel()
