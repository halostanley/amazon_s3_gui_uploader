import socket
import json
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

class Client:

    def __init__(self, server_ip, server_port):

        self.server_ip = server_ip
        self.server_port = int(server_port)


    def socket_send(self, wait_to_send_data):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            soc.connect((self.server_ip, self.server_port))
            jsoned_send = json.dumps(wait_to_send_data)
            soc.sendall(jsoned_send.encode())

            if wait_to_send_data['action'] == 'login_btn':
                buf = soc.recv(2048).decode()
                jsonloads = json.loads(buf)
                return jsonloads #return [bool, retrieve_user_setting]

            if wait_to_send_data['action'] == 'signup_btn':
                buf = soc.recv(2048).decode()
                jsonloads = json.loads(buf)
                flag = jsonloads
                return flag #bool user_name_is_none

            if wait_to_send_data['action'] == 'save_evt':
                buf = soc.recv(2048).decode()
                jsonloads = json.loads(buf)
                success_flag = jsonloads
                return success_flag #bool True is no error

            if wait_to_send_data['action'] == 'success_upload':
                # Only sent to server, no response need.
                pass

        except:
            soc.close()

        finally:
            soc.close()