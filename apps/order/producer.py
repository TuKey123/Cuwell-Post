import pika
import json

params = pika.URLParameters('amqps://iifhdhrs:GdvmlF6_j-t_pp1vQa00rxk7NHKEKkdY@mustang.rmq.cloudamqp.com/iifhdhrs')

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='order', body=body, properties=properties)
