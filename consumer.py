import django
import os
import pika

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "post_service.settings")
django.setup()

from apps.post.models import Category

params = pika.URLParameters('amqps://iifhdhrs:GdvmlF6_j-t_pp1vQa00rxk7NHKEKkdY@mustang.rmq.cloudamqp.com/iifhdhrs')

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue='order')


def callback(ch, method, properties, body):
    category = Category.objects.create(name='1')
    category.save()

    print(body)


channel.basic_consume(queue='order', on_message_callback=callback, auto_ack=True)

print('start consuming')
print('start 1')

channel.start_consuming()

# channel.close()
