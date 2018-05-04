import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import socket
import json
import time
import monogo
import logging
logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] : %(message)s',
    )
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fh = logging.FileHandler("log.txt")
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s, %(name)s, [%(levelname)s] : %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)


def handle_save_evt(payload_dict):
    success_flag = False #True is success
    if payload_dict['action'] == 'save_evt':
        user_name = payload_dict['payload']['user_name']
        db = monogo.Database(user_name)
        success_flag = db.user_setting_update(payload_dict) #if no error, return true.

    return success_flag


def handle_login_btn(payload_dict):
    if payload_dict['action'] == 'login_btn':
        user_name = payload_dict['payload']['user_name']
        password = payload_dict['payload']['password']
        db = monogo.Database(user_name, password)
        (error_flag, retrieve_user_setting) = db.user_login()

        return (error_flag, retrieve_user_setting)


def signup_btn(payload_dict):
    success = False
    if payload_dict['action'] == 'signup_btn':
        user_name = payload_dict['payload']['user_name']
        password = payload_dict['payload']['password']
        ser_ip = payload_dict['payload']['ser_ip']
        ser_port = payload_dict['payload']['ser_port']
        aws_accesskey = payload_dict['payload']['aws_accesskey']
        aws_secretkey = payload_dict['payload']['aws_secretkey']
        aws_bucket_for_upload = payload_dict['payload']['aws_bucket_for_upload']
        db = monogo.Database(user_name=user_name)
        success = db.add_user(user_name, password, ser_ip, ser_port, aws_accesskey, aws_secretkey, aws_bucket_for_upload)

    return success


def handle_success_upload(payload_dict):
    #print(payload_dict)
    if payload_dict['action'] == 'success_upload':
        user_name = payload_dict['payload']['user_name']
        db = monogo.Database(user_name)
        db.success_upload(payload_dict)

    return None


def thread_worker(client_socket, client_address):
    while 1:
        print("Received from: ", client_address)
        buf = client_socket.recv(9999)

        if not buf:
            client_socket.close()
            break
        else:
            buf_data = buf.decode()
            jsoned_buf_data = json.loads(buf_data)

            if jsoned_buf_data['action'] == 'save_evt':
                success_flag = handle_save_evt(jsoned_buf_data)
                jsoned = json.dumps(success_flag)

            if jsoned_buf_data['action'] == 'login_btn':
                error_flag_retrieve_user_setting = handle_login_btn(jsoned_buf_data)
                jsoned = json.dumps(error_flag_retrieve_user_setting)

            if jsoned_buf_data['action'] == 'signup_btn':
                user_name_is_none = signup_btn(jsoned_buf_data)
                jsoned = json.dumps(user_name_is_none)

            if jsoned_buf_data['action'] == 'success_upload':
                handle_success_upload(jsoned_buf_data)

            client_socket.sendall(jsoned.encode())
            client_socket.close()
            break


def child_process(queue):
    with ThreadPoolExecutor(max_workers=5) as executor:
        while 1:
            client_socket, client_address = queue.get()
            executor.submit(thread_worker, client_socket, client_address)
            time.sleep(.1)


def run_server():
    server_port = 50001
    num_processes = multiprocessing.cpu_count()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', server_port))
    server_socket.listen(20)

    socket_queue = multiprocessing.Queue()
    #lock = multiprocessing.Lock()
    processes = []

    for _ in range(num_processes):
        p = multiprocessing.Process(target=child_process, args=(socket_queue, ))
        processes.append(p)

    [p.start() for p in processes]

    while 1:
        logger.info("Receiving new socket...")
        try:
            new_socket = server_socket.accept()
        except:
            logger.info("Connection Error.")
            break
        socket_queue.put(new_socket)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    run_server()