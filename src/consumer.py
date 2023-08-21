import pika
import sys
import os
import yaml
import argparse
import random
import string
import time


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def fparser():
    parser = argparse.ArgumentParser(description="RabbitMQ client.")
    parser.add_argument("-H", "--host", help="Rabbitmq host(default 'localhost')", default="localhost")
    parser.add_argument("-p", "--port", help="Rabbitmq port(default '5672')", default="5672")
    parser.add_argument("-a", "--auto-ack", help="Enable auto ack", action="store_true", default=False)
    parser.add_argument("-u", "--user", help="User for rabbitmq")
    parser.add_argument("-P", "--password", help="Password for rabbitmq")
    parser.add_argument("-q", "--queue", help="The name of the queue")
    parser.add_argument("-e", "--exchange", help="The exchange to connect. This option will create an ephimeral queue",)

    args = parser.parse_args()
    print(args)

    if args.queue is None and args.exchange is None:
        print("ERROR: A queue or Exchange must be defined")
        exit(1)
    elif args.queue and args.exchange:
        print("ERROR: Queue and Exchange must not be defined at the same time")
        exit(1)
    return args


def main(args):
    program_args = fparser()

    user = program_args.user
    password = program_args.password
    port = program_args.port
    host = program_args.host
    auto_ack = program_args.auto_ack
    # autoack = program_args.
    exchange = program_args.exchange
    if program_args.queue:
        queue = program_args.queue
    else:
        queue = f"tmp-{program_args.exchange}-{get_random_string(8)}"
        print(f"Temporal queue name: {queue}")

    print("Configuration: ")
    print(f"\tHost: {host}")
    print(f"\tPort: {port}")
    print(f"\tUser: {user}")
    print(f"\tPassword: {password}")
    print(f"\tQueue: {queue}")
    print(f"\tAuto Ack: {auto_ack}")
    if exchange:
        print(f"\tExchange: {exchange}")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host, port=port, credentials=pika.PlainCredentials(
                user, password)
        )
    )

    channel = connection.channel()
    if exchange:
        print("Creating temporal queue")
        channel.queue_declare(queue, auto_delete=True)
        channel.queue_bind(queue, exchange, routing_key='#')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    while (True):
        try:         
            channel.basic_consume(queue=queue, auto_ack=auto_ack, on_message_callback=callback)
            channel.start_consuming()
        except pika.exceptions.ChannelClosedByBroker: 
            print("Reconnecting")
            pass



if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
