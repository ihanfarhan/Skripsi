import json
import base64
import socket
import requests
import threading
import numpy as np
import logging.config
import tensorflow as tf
import efficientnet.tfkeras

from PIL import Image
from io import BytesIO
from queue import Queue
from tensorflow.keras.models import load_model

logging.config.fileConfig('public/config/logging.config.ini')

# Parameters
input_size = (150,150)

#define input shape
channel = (3,)
input_shape = input_size + channel

#define labels
labels = ['fiber', 'lan', 'listrik', 'normal']


# ada 2 cara load model, jika cara pertama berhasil maka bisa lasngusng di lanjutkan ke fungsi prediksi

MODEL_PATH = 'model.h5'
model = load_model(MODEL_PATH,compile=False)


def preprocess(img,input_size):
    nimg = img.convert('RGB').resize(input_size, resample= 0)
    img_arr = (np.array(nimg))/255
    return img_arr

def reshape(imgs_arr):
    return np.stack(imgs_arr, axis=0)


# parse the data
def load_data(soc):
    header = soc.recv(8).decode('utf-8')
    if '\n' not in header:
        logging.error('saw no newline in the first 8 bytes')
    else:
        len_str, json_str = header.split('\n', 1)
        to_read = int(len_str) - len(json_str)
        if to_read > 0:
            json_str += soc.recv(to_read, socket.MSG_WAITALL).decode('utf-8')
        return json_str


#  Main Thread: Listening for incoming connections from clients
def serve(addr, out_q):
    logging.info('Server Starting !')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(addr)
    server_socket.listen(10)
    while True:
        client_socket, client_address = server_socket.accept()
        client_socket.settimeout(10.0)
        out_q.put((client_socket, client_address))
        # logging.debug('thread %s is running...' % threading.current_thread().name)


#  Thread 2
def recv_send_img(in_q):
    while True:
        try:
            client_socket, client_address = in_q.get()
            logging.debug('thread %s is running...' % threading.current_thread().name)
            logging.info('----------Got Connection From {}-------'.format(client_address))
            json_data = json.loads(load_data(client_socket))
            # read image
            im = Image.open(json_data.get('image_name'))
            X = preprocess(im,input_size)
            X = reshape([X])
            y = model.predict(X)

            chat_id = json_data['chat_id']
            json_str = json.dumps({
                'status': 200,
                'chat_id': chat_id,
                'response': labels[np.argmax(y)]
            })
            wrapped_msg = '{}\n{}'.format(len(json_str), json_str)
            client_socket.send(wrapped_msg.encode('utf-8'))
            logging.info('Response has been sent back to bot.py [chat_id] is [{}]'.format(chat_id))
            client_socket.shutdown(socket.SHUT_WR)
            logging.info('----------Closed connection from {}----------'.format(client_address))
        except Exception as e:
            print (e)


if __name__ == '__main__':
    q = Queue()
    t1 = threading.Thread(target=serve, args=(('', 20000), q,), name='Main Thread')
    t2 = threading.Thread(target=recv_send_img, args=(q,), name='Thread 2')
    t1.start()
    t2.start()