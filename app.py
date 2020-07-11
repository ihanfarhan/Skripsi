import os
import json
import time
import socket
import base64
import random
import telepot
import logging
import requests
import threading
import logging.config

from queue import Queue
from telepot.loop import MessageLoop

logging.config.fileConfig('public/config/logging.config.ini')
IMG_PATH = 'public/picture/'


def load_data(soc):
    header = soc.recv(6).decode('utf-8')
    if '\n' not in header:
        logging.error('saw no newline in the first 6 bytes')
    len_str, json_str = header.split('\n', 1)
    to_read = int(len_str) - len(json_str)
    if to_read > 0:
        json_str += soc.recv(to_read, socket.MSG_WAITALL).decode('utf-8')
    return json_str


def get_filename(chat_id):
    time_stamp = time.strftime('%Y%m%d%H%M%S') + str(random.randint(1, 100))
    return str(chat_id) + '_' + time_stamp + '.png'


def serialize(file_path, chat_id, image_name):
    with open(file_path, "rb") as image_file:
        encoded_img = base64.b64encode(image_file.read())
    json_str = {
        'chat_id': chat_id,
        'image_name': 'public/picture/{}'.format(image_name)
    }
    json_str = json.dumps(json_str)
    wrapped_msg = '{}\n{}'.format(len(json_str), json_str)
    return wrapped_msg


#  Thread 1 ­ Receiving Messages
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    logging.info('----------Got Connection From User [{}]-------'.format(chat_id))
    file_name = get_filename(str(chat_id))
    img_path = IMG_PATH + file_name
    logging.debug('content_type is: {}'.format(content_type))
    logging.debug('chat_id is: {}'.format(chat_id))

    if content_type == 'photo':
        logging.info('----------Download Image From Telegram----------')
        bot.download_file(msg['photo'][-1]['file_id'], img_path)
        wrapped_msg = serialize(img_path, chat_id, file_name)
        queue_1.put(wrapped_msg)
        # logging.debug('Queue 1 has been put')


# #  Thread 2 ­ Client Thread
def send_recv_img(in_queue_1, out_queue_2):
    while True:
        # logging.debug('thread %s is running...' % threading.current_thread().name)
        wrapped_msg = in_queue_1.get()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('farhan-backend-thesis', 20000))
        logging.info('The connection to the Server has been established')
        client_socket.sendall(wrapped_msg.encode('utf-8'))
        logging.info('Image has been sent to Server')
        # receive the response from server and put it into queue_2
        out_queue_2.put(load_data(client_socket))
        logging.info('Prediction result from the server has been received')
        # logging.debug('Queue 2 has been put')


# Thread 3 ­ Sending Messages
def send_response(in_queue_2):
    while True:
        # logging.debug('thread %s is running...' % threading.current_thread().name)
        logging.info('damn')
        json_response_rec = in_queue_2.get()
        logging.info(json_response_rec)
        json_response = json.loads(json_response_rec)
        chat_id = json_response.get('chat_id')
        bot.sendMessage(chat_id, json_response.get('response'))
        logging.info('----------END----------')


if __name__ == "__main__":
    bot = telepot.Bot('1018451310:AAEpfheow1c0e38YpTGCRAevdaAWePV8vjU')
    queue_1 = Queue()
    queue_2 = Queue()
    MessageLoop(bot, handle).run_as_thread()
    # logging.debug('thread %s is running...' % threading.current_thread().name)
    t2 = threading.Thread(target=send_recv_img, args=(queue_1, queue_2,), name='Thread 2')
    t3 = threading.Thread(target=send_response, args=(queue_2,), name='Thread 3')
    t2.start()
    t3.start()