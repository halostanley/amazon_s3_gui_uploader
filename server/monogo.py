from pymongo import MongoClient
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

MONGODB_SERVER_HOST = 'localhost'
MONGODB_SERVER_PORT = ''

class Database:

    def __init__(self, user_name='', user_password=''):
        self.mongo_ip = MONGODB_SERVER_HOST
        self.mongo_port = ''
        self.mongo_password = ''
        self.user_name = user_name
        self.user_password = user_password
        #self.inital()


    def inital(self):
        pass


    def recall_user_record(self, user_name):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client['proj_db']
        collection = db['success_upload_collection']
        query = {'user_name':user_name}
        response = collection.find(query).limit(1000).sort([('_id', -1)])
        client.close()
        return response


    def recall_success_upload_record(self):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client['proj_db']
        collection = db['success_upload_collection']
        response = collection.find().limit(1000).sort([('_id', -1)])
        client.close()
        return response


    def success_upload(self, payload_dict):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client['proj_db']
        #collection = db.create_collection('success_upload_collection')
        collection = db['success_upload_collection']
        success_upload_dict = {'user_name': payload_dict['payload']['user_name'],
                               'upload_bucket': payload_dict['payload']['upload_bucket'],
                               'unique_key':payload_dict['payload']['unique_key'],
                               'org_key':payload_dict['payload']['org_key'],
                               'unique_org_key':payload_dict['payload']['unique_org_key'],
                               'timestamp': payload_dict['payload']['timestamp'],
                               'download_url':payload_dict['payload']['download_url'],
                               'file_size':payload_dict['payload']['file_size']
                               }
        try:
            collection.insert_one(success_upload_dict)
        except:
            pass
        finally:
            client.close()


    def user_setting_update(self, payload_dict):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client['proj_db']
        collection = db['users_collection']
        query = {'user_name': self.user_name}
        update = {'$set':
                      {'ser_ip':payload_dict['payload']['ser_ip'],
                       'ser_port':payload_dict['payload']['ser_port'],
                       'aws_accesskey': payload_dict['payload']['aws_accesskey'],
                       'aws_secretkey': payload_dict['payload']['aws_secretkey'],
                       'aws_bucket_for_upload': payload_dict['payload']['aws_bucket_for_upload']
                       }
                  }

        try:
            collection.update_one(query, update)
            success_flag = True #False is no error
            return success_flag
        except:
            success_flag = False #False is error
            return success_flag
        finally:
            client.close()


    def check_user_exists(self, user_name):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client['proj_db']
        collection = db['users_collection']
        query = {'user_name': user_name}
        results = collection.find_one(query)
        client.close()
        return results


    def hash_pass(self, password):
        import bcrypt
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        return hash_password


    def add_user(self, user_name, password, ser_ip, ser_port, aws_accesskey, aws_secretkey, aws_bucket_for_upload):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client["proj_db"]
        collection = db['users_collection']

        #usesr_name = input("Please enter your desired username: ")
        signup_sucess = False
        if not self.check_user_exists(user_name):
            password_hashed = self.hash_pass(password.encode())
            user_data = {'user_id': collection.count() + 1,
                         'user_name': user_name,
                         'password': password_hashed,
                         'ser_ip':ser_ip,
                         'ser_port':ser_port,
                         'aws_accesskey':aws_accesskey,
                         'aws_secretkey':aws_secretkey,
                         'aws_bucket_for_upload': aws_bucket_for_upload
                         }
            collection.insert_one(user_data)
            signup_sucess =  True
        client.close()
        return signup_sucess


    def get_password(self, user_name):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client["proj_db"]
        collection = db['users_collection']
        query = {'user_name': user_name}
        result = collection.find_one(query)
        client.close()
        return result['password']


    def user_login(self):
        client = MongoClient(MONGODB_SERVER_HOST)
        db = client["proj_db"]
        collection = db['users_collection']
        error_flag = True
        retrieve_user_setting = {}
        if self.check_user_exists(self.user_name):
            hashed_pw = self.get_password(self.user_name)
            import bcrypt
            if bcrypt.hashpw(self.user_password.encode(), hashed_pw) == hashed_pw:
                error_flag = False
                #retrieve user setting
                query = {'user_name': self.user_name}
                result = collection.find_one(query)
                retrieve_user_setting = {
                    'action': 'retrieve_user_setting',
                    'payload': {'ser_ip': result['ser_ip'],
                                'ser_port': result['ser_port'],
                                'aws_accesskey': result['aws_accesskey'],
                                'aws_secretkey': result['aws_secretkey'],
                                'aws_bucket_for_upload': result['aws_bucket_for_upload']
                                }
                }
        else:
            error_flag = True

        client.close()
        return (error_flag, retrieve_user_setting)