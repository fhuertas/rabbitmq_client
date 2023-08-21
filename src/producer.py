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
    parser.add_argument("-u", "--user", help="User for rabbitmq", default="")
    parser.add_argument("-P", "--password", help="Password for rabbitmq", default="")
    parser.add_argument("-e", "--exchange", help="The exchange to publish.", required=True)
    parser.add_argument("-c", "--content", help="content to publish")
    parser.add_argument("-f", "--file", help="file content to publish")
    parser.add_argument("-r", "--routing-key", help="Routing key for the message (default: #)", default="#")
    args = parser.parse_args()
    if args.content and args.file:
        print("ERROR: Content and file content cannot be defined at same time.")
        exit(1)
    print(args)

    return args


def main(args):
    program_args = fparser()

    main2(program_args)


def main2(args):
    # queue = args.queue
    # exchange = args.exchange
    # if queue and exchange:
    #     print(f"error ")

    user = args.user
    password = args.password
    port = args.port
    host = args.host
    exchange = args.exchange
    routing_key = args.routing_key

    print("Configuration: ")
    print(f"\tHost: {host}")
    print(f"\tPort: {port}")
    print(f"\tUser: {user}")
    print(f"\tPassword: {password}")
    print(f"\tExchange: {exchange}")
    print(f"\tRouting Key: {routing_key}")

    content = ""
    readed = ""
    if args.file:
        with open(args.file, "r") as stream:
            content += stream.read()
        print(f"Content:\n{content}")
        loop = False
    elif args.content:
        content = args.content
        print(f"Content:\n{content}")
        loop = False
    else:
        print(" [*] To exit press CTRL+C")
        content = input("Content to publish: ")
        loop = True

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(user, password)
        )
    )
    channel = connection.channel()

    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=content)

    while (loop):
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=content)
        content = input("Content to publish: ")
        loop = True

    # channel.basic_consume(queue=queue, auto_ack=auto_ack, on_message_callback=callback)
    # print(" [*] Waiting for messages. To exit press CTRL+C")
    # channel.start_consuming()
    return


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
