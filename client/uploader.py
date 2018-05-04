import wx
import s3action
import socket
import client
import time
import signup
import threading
import uuid
import datetime
from math import log
import os
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

SERVER_IP = "localhost"
SERVER_PORT = "50001"

class Upload(wx.Frame):
    def __init__(self, *args, **kwds):

        # Config:
        self.access = ""
        self.key = ""
        self.check_login_flag = False
        self.check_upload_flag = False
        self.s3_bucket_for_upload = ""
        self.file_paths = []
        self.file_names = []
        #thread_active_counter = threading.Thread(target=self.thread_counter, args=(), daemon=True)
        #thread_active_counter.start()

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((650, 700))
        self.text_ctrl_username = wx.TextCtrl(self, wx.ID_ANY, "")
        self.text_ctrl_password = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PASSWORD)
        self.Login = wx.Button(self, wx.ID_ANY, "Login")
        self.button_signup = wx.Button(self, wx.ID_ANY, "Sign up")
        self.ser_ip = wx.TextCtrl(self, wx.ID_ANY, SERVER_IP)
        self.ser_port = wx.TextCtrl(self, wx.ID_ANY, SERVER_PORT)
        self.aws_accesskey = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PASSWORD)
        self.aws_secretkey = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PASSWORD)
        self.aws_buckets_list = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        #self.aws_bucket_folders_list = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.button_4 = wx.Button(self, wx.ID_ANY, "Server Test")
        self.button_5 = wx.Button(self, wx.ID_ANY, "AWS Test")
        self.button_6 = wx.Button(self, wx.ID_ANY, "Save")
        self.bitmap_button_broswer = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("./images/broswer.png", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_cloud_upload = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("./images/upload.png", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_clean = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("./images/clean.png", wx.BITMAP_TYPE_ANY))
        self.upload_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.BORDER_DEFAULT | wx.BORDER_STATIC | wx.FULL_REPAINT_ON_RESIZE | wx.LC_ALIGN_LEFT | wx.LC_ALIGN_TOP | wx.LC_AUTOARRANGE | wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES )
        self.upload_current_status = wx.StaticText(self, wx.ID_ANY, "None")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.login_btn, self.Login)
        self.Bind(wx.EVT_BUTTON, self.signup_btn, self.button_signup)
        #self.Bind(wx.EVT_COMBOBOX, self.aws_bucket_folders_list_evt, self.aws_bucket_folders_list)
        self.Bind(wx.EVT_COMBOBOX, self.aws_buckets_list_evt, self.aws_buckets_list)
        self.Bind(wx.EVT_BUTTON, self.ser_test_evt, self.button_4)
        self.Bind(wx.EVT_BUTTON, self.aws_test_evt, self.button_5)
        self.Bind(wx.EVT_BUTTON, self.save_evt, self.button_6)
        self.Bind(wx.EVT_BUTTON, self.broswer_files_evt, self.bitmap_button_broswer)
        self.Bind(wx.EVT_BUTTON, self.cloud_upload_evt, self.bitmap_button_cloud_upload)
        self.Bind(wx.EVT_BUTTON, self.clean_evt, self.bitmap_button_clean)


    def __set_properties(self):
        self.SetTitle("Python - Cloud Storage Uploader")
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.text_ctrl_username.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.text_ctrl_password.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.Login.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.ser_ip.SetMinSize((200, 22))
        self.ser_port.SetMinSize((200, 22))
        self.aws_accesskey.SetMinSize((200, 22))
        self.aws_secretkey.SetMinSize((200, 22))
        self.aws_buckets_list.SetMinSize((200, 26))
        #self.aws_bucket_folders_list.SetMinSize((200, 26))
        self.bitmap_button_broswer.SetSize(self.bitmap_button_broswer.GetBestSize())
        self.bitmap_button_cloud_upload.SetSize(self.bitmap_button_cloud_upload.GetBestSize())
        self.bitmap_button_clean.SetSize(self.bitmap_button_clean.GetBestSize())
        self.upload_list.InsertColumn(0, "Index", format=wx.LIST_FORMAT_CENTER, width=50)
        self.upload_list.InsertColumn(1, "Name", format=wx.LIST_FORMAT_CENTER, width=150)
        self.upload_list.InsertColumn(2, "Path", format=wx.LIST_FORMAT_LEFT, width=330)
        self.upload_list.InsertColumn(3, "Status", format=wx.LIST_FORMAT_CENTER, width=100)
        self.upload_list.Refresh()
        self.upload_current_status.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))


    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_setting_btns = wx.BoxSizer(wx.HORIZONTAL)
        sizer_aws_bucket = wx.BoxSizer(wx.HORIZONTAL)
        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        #sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_aws_access = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_server = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_login = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Login"), wx.VERTICAL)
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        label_1 = wx.StaticText(self, wx.ID_ANY, "Python Project")
        label_1.SetFont(wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        sizer_2.Add(label_1, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 10)
        label_21 = wx.StaticText(self, wx.ID_ANY, "Username")
        sizer_12.Add(label_21, 0, wx.RIGHT, 10)
        sizer_12.Add(self.text_ctrl_username, 0, wx.RIGHT, 10)
        label_22 = wx.StaticText(self, wx.ID_ANY, "Password")
        sizer_12.Add(label_22, 0, wx.RIGHT, 10)
        sizer_12.Add(self.text_ctrl_password, 0, wx.RIGHT, 10)
        sizer_12.Add(self.Login, 0, wx.RIGHT, 10)
        sizer_12.Add(self.button_signup, 0, 0, 0)
        sizer_login.Add(sizer_12, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_login, 1, wx.ALL | wx.EXPAND, 10)
        label_13 = wx.StaticText(self, wx.ID_ANY, "Server IP", style=wx.ALIGN_RIGHT)
        label_13.SetMinSize((100, 15))
        sizer_10.Add(label_13, 0, wx.RIGHT, 5)
        sizer_10.Add(self.ser_ip, 0, 0, 0)
        sizer_server.Add(sizer_10, 1, wx.EXPAND, 0)
        label_16 = wx.StaticText(self, wx.ID_ANY, "Server Port", style=wx.ALIGN_RIGHT)
        label_16.SetMinSize((100, 15))
        sizer_11.Add(label_16, 0, wx.RIGHT, 5)
        sizer_11.Add(self.ser_port, 0, 0, 0)
        sizer_server.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_server, 1, wx.EXPAND | wx.TOP, 5)
        label_12 = wx.StaticText(self, wx.ID_ANY, "AWS Access", style=wx.ALIGN_RIGHT)
        label_12.SetMinSize((100, 15))
        sizer_7.Add(label_12, 0, wx.RIGHT, 5)
        sizer_7.Add(self.aws_accesskey, 0, 0, 0)
        sizer_6.Add(sizer_7, 1, wx.EXPAND, 0)
        label_15 = wx.StaticText(self, wx.ID_ANY, "AWS Secret", style=wx.ALIGN_RIGHT)
        label_15.SetMinSize((100, 15))
        sizer_8.Add(label_15, 0, wx.RIGHT, 5)
        sizer_8.Add(self.aws_secretkey, 0, 0, 0)
        sizer_6.Add(sizer_8, 1, wx.EXPAND, 0)
        sizer_aws_access.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_aws_access, 0, wx.EXPAND | wx.TOP, 5)
        label_14 = wx.StaticText(self, wx.ID_ANY, "AWS Bucket", style=wx.ALIGN_RIGHT)
        label_14.SetMinSize((100, 15))
        sizer_14.Add(label_14, 0, wx.RIGHT, 5)
        sizer_14.Add(self.aws_buckets_list, 0, 0, 0)
        sizer_13.Add(sizer_14, 1, wx.EXPAND, 0)
        #label_17 = wx.StaticText(self, wx.ID_ANY, "Bucket Folder", style=wx.ALIGN_RIGHT)
        #label_17.SetMinSize((100, 15))
        #sizer_15.Add(label_17, 0, wx.RIGHT, 5)
        #sizer_15.Add(self.aws_bucket_folders_list, 0, 0, 0)
        #sizer_13.Add(sizer_15, 1, wx.EXPAND, 0)
        sizer_aws_bucket.Add(sizer_13, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_aws_bucket, 25, wx.EXPAND | wx.TOP, 5)
        sizer_setting_btns.Add(self.button_4, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.RIGHT, 10)
        sizer_setting_btns.Add(self.button_5, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.RIGHT, 10)
        sizer_setting_btns.Add(self.button_6, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.RIGHT, 10)
        sizer_2.Add(sizer_setting_btns, 1, wx.ALIGN_RIGHT | wx.ALL, 10)
        sizer_4.Add(self.bitmap_button_broswer, 0, 0, 0)
        sizer_4.Add(self.bitmap_button_cloud_upload, 0, 0, 0)
        sizer_4.Add(self.bitmap_button_clean, 0, 0, 0)
        sizer_2.Add(sizer_4, 150, wx.ALIGN_CENTER, 0)
        sizer_2.Add(self.upload_list, 200, wx.ALL | wx.EXPAND, 10)
        upload_status_title = wx.StaticText(self, wx.ID_ANY, "Upload status: ")
        upload_status_title.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_9.Add(upload_status_title, 0, 0, 0)
        sizer_9.Add(self.upload_current_status, 0, 0, 0)
        sizer_2.Add(sizer_9, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT, 10)
        sizer_1.Add(sizer_2, 1, wx.ALIGN_CENTER | wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()


    def return_buckets_list(self):
        amazons3 = s3action.amazons3(self.access, self.key)
        self.amazons3_buckets_list = amazons3.buckets_list()
        return self.amazons3_buckets_list


    #def return_bucket_folders_list(self):
    #    pass


    def login_btn(self, event):
        payload_dict = { 'user_name':self.text_ctrl_username.GetValue(),
                         'password': self.text_ctrl_password.GetValue()
                        }

        ready_to_send = {'action': 'login_btn', 'payload': payload_dict}

        try:
            server_host = self.ser_ip.GetValue()
            server_port = int(self.ser_port.GetValue())
            soc = client.Client(server_host, server_port)
            error_flag_retrieve_user_setting = soc.socket_send(ready_to_send)
            error_flag = error_flag_retrieve_user_setting[0]
            retrieve_user_setting = error_flag_retrieve_user_setting[1]
            if not error_flag:
                if not self.check_login_flag:
                    self.check_login_flag = True
                    self.Login.SetLabel("Log out")
                    self.Login.SetBackgroundColour(wx.Colour(65,105,225))
                    self.text_ctrl_username.SetEditable(False)
                    self.text_ctrl_password.SetEditable(False)
                    self.ser_ip.SetValue(retrieve_user_setting['payload']['ser_ip'])
                    self.ser_port.SetValue(str(retrieve_user_setting['payload']['ser_port']))
                    self.aws_accesskey.SetValue(retrieve_user_setting['payload']['aws_accesskey'])
                    self.aws_secretkey.SetValue(retrieve_user_setting['payload']['aws_secretkey'])
                    self.access = self.aws_accesskey.GetValue()
                    self.key = self.aws_secretkey.GetValue()
                    self.aws_buckets_list.Append(self.return_buckets_list())
                    self.aws_buckets_list.SetSelection(0)
                    self.s3_bucket_for_upload = self.aws_buckets_list.GetValue()
                    return wx.MessageDialog(None, u'Successfully logged in.', u"Login",
                                            wx.OK | wx.ICON_INFORMATION).ShowModal()
                else:
                    self.check_login_flag = False
                    self.Login.SetLabel("Login")
                    self.Login.SetBackgroundColour(wx.Colour(255, 255, 255))
                    self.text_ctrl_username.SetEditable(True)
                    self.text_ctrl_password.SetEditable(True)
                    self.text_ctrl_username.Clear()
                    self.text_ctrl_password.Clear()
                    self.aws_buckets_list.Clear()
                    self.aws_accesskey.Clear()
                    self.aws_secretkey.Clear()
                    self.s3_bucket_for_upload = None
                    return wx.MessageDialog(None, u'Successfully logged out.', u"Login",
                                            wx.OK | wx.ICON_INFORMATION).ShowModal()

            else:
                self.check_login_flag = False
                return wx.MessageDialog(None, u'Wrong username or password or error.', u"Login",
                                        wx.OK | wx.ICON_ERROR).ShowModal()
        except Exception as err:
            logger.info("{}".format(err))
            self.check_login_flag = False
            self.Login.SetLabel("Login")
            self.Login.SetBackgroundColour(wx.Colour(255, 255, 255))
            self.text_ctrl_username.SetEditable(True)
            self.text_ctrl_password.SetEditable(True)
            self.text_ctrl_username.Clear()
            self.text_ctrl_password.Clear()
            self.aws_buckets_list.Clear()
            self.aws_accesskey.Clear()
            self.aws_secretkey.Clear()
            self.s3_bucket_for_upload = None
            return wx.MessageDialog(None, u'Connection Error.', u"Login",
                                    wx.OK | wx.ICON_ERROR).ShowModal()

        finally:
            event.Skip()


    def signup_btn(self, event):
        signup_window = signup.Sign_up(None)
        signup_window.Show()
        event.Skip()


    def aws_buckets_list_evt(self, event):
        self.s3_bucket_for_upload = self.aws_buckets_list.GetValue()
        event.Skip()


    #def aws_bucket_folders_list_evt(self, event):
    #    print("Event handler 'aws_bucket_folders_list_evt' not implemented!")
    #    event.Skip()


    def ser_test_evt(self, event):
        server_host = self.ser_ip.GetValue()
        server_port = int(self.ser_port.GetValue())
        self.ser_ok_flag = False #True is OK, False is NOT OK
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            soc.connect((server_host, server_port))
            self.ser_ok_flag = True
            return wx.MessageDialog(None, u'Connection OK', u"Server Connection",
                                    wx.OK | wx.ICON_INFORMATION).ShowModal()
        except:
            logger.info("Server test connection error.")
            soc.close()
            self.ser_ok_flag = False
            return wx.MessageDialog(None, u'Connection NOT OK', u"Server Connection",
                                    wx.OK | wx.ICON_ERROR).ShowModal()
        finally:
            soc.close()
            event.Skip()
            #return self.ser_ok_flag


    def aws_test_evt(self, event):
        amazons3 = s3action.amazons3(self.access, self.key)
        client = amazons3.check_client_connection()
        try:
            if client:
                return wx.MessageDialog(None, u'Connection OK', u"AWS Connection",
                                        wx.OK | wx.ICON_INFORMATION).ShowModal()
            else:
                return wx.MessageDialog(None, u'Connection NOT OK', u"AWS Connection",
                                        wx.OK | wx.ICON_ERROR).ShowModal()
        except:
            logger.info("Amazon S3 connection error.")
        finally:
            event.Skip()


    def save_evt(self, event):
        setting_dict = {'ser_ip': self.ser_ip.GetValue(),
                        'ser_port': self.ser_port.GetValue(),
                        'user_name': self.text_ctrl_username.GetValue(),
                        'aws_accesskey': self.aws_accesskey.GetValue(),
                        'aws_secretkey': self.aws_secretkey.GetValue(),
                        'aws_bucket_for_upload': self.aws_buckets_list.GetValue(),
                        }

        ready_to_send = {'action': 'save_evt', 'payload': setting_dict}

        server_host = self.ser_ip.GetValue()
        server_port = int(self.ser_port.GetValue())
        try:
            if self.check_login_flag:
                soc = client.Client(server_host, server_port)
                success_flag = soc.socket_send(ready_to_send)
                if success_flag:
                    return wx.MessageDialog(None, u'Setting saved', u"Saved",
                                            wx.OK | wx.ICON_INFORMATION).ShowModal()
                else:
                    return wx.MessageDialog(None, u'Connection NOT OK', u"Server Connection",
                                            wx.OK | wx.ICON_ERROR).ShowModal()
            else:
                return wx.MessageDialog(None, u'Please login.', u"Login",
                                        wx.OK | wx.ICON_ERROR).ShowModal()
        except:
            return wx.MessageDialog(None, u'Error during login.', u"ERROR",
                                    wx.OK | wx.ICON_ERROR).ShowModal()
        finally:
            event.Skip()


    def broswer_files_evt(self, event):

        #self.file_paths = []
        #self.file_names = []
        self.upload_list.DeleteAllItems()
        try:
            with wx.FileDialog(self, "Choose a file", "", "", "*.*", wx.FD_MULTIPLE) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return  # the user changed their mind

                list_paths = fileDialog.GetPaths()
                list_names = fileDialog.GetFilenames()
                # Proceed loading the file chosen by the user
                self.file_paths = self.file_paths + list_paths
                self.file_names = self.file_names + list_names
                fileDialog.Destroy()
        except:
            return wx.MessageDialog(None, u'Error during loging wx.FileDialog.', u"ERROR",
                                    wx.OK | wx.ICON_ERROR).ShowModal()


        for index in range(len(self.file_paths)):
            try:
                self.upload_list.Append((index + 1, self.file_names[index], self.file_paths[index]))
            except Exception as err:
                return wx.MessageDialog(None, u'Error during loading wx.ListClrt.', u"ERROR",
                                        wx.OK | wx.ICON_ERROR).ShowModal()
        event.Skip()


    def uploading_counter(self):
        while True:
            try :
                if self.uploadcounter < self.len_upload_files:
                    self.upload_current_status.SetLabel(
                        "Uploading... [{} / {}]".format(self.uploadcounter, self.len_upload_files))
                    time.sleep(.1)
                else:
                    if self.uploadcounter == self.len_upload_files:
                        self.upload_current_status.SetLabel(
                            "All files uploaded. [{} / {}]".format(self.len_upload_files, self.len_upload_files))
                    break
            except:
                break


    def get_file_size(self, n, pow=0, b=1024, u='B', pre=[''] + [p for p in 'KMGTPEZY']):
        r, f = min(int(log(max(n * b ** pow, 1), b)), len(pre) - 1), '{:,.%if} %s%s'
        return (f % (abs(r % (-r - 1)), pre[r], u)).format(n * b ** pow / b ** float(r))


    def upload_to_s3(self, instance, path, key, index):
        file_size = self.get_file_size(os.path.getsize(path))
        org_key = key
        prefix = "."+org_key.split(".")[-1]
        unique_key = uuid.uuid4()
        unique_key = hex(int(unique_key.time_low))[2:]
        #unique_org_key = unique_key + "_" + org_key
        unique_org_key = unique_key + prefix
        #print(unique_org_key)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.upload_list.SetItem(index, 3, "Uploading")
        success_flag = instance.upload_single_file(path, unique_org_key, self.s3_bucket_for_upload)
        time.sleep(.2)
        if success_flag:
            amazons3 = s3action.amazons3(self.access, self.key)
            download_url = amazons3.get_key_url(self.aws_buckets_list.GetValue(), unique_org_key)
            self.upload_list.SetItem(index, 3, "Uploaded")
            payload_dict = {'user_name': self.text_ctrl_username.GetValue(),
                            'upload_bucket': self.aws_buckets_list.GetValue(),
                            'unique_key':unique_key,
                            'org_key':org_key,
                            'unique_org_key':unique_org_key,
                            'timestamp': timestamp,
                            'download_url': download_url,
                            'file_size':file_size
                            }
            ready_to_send = {'action': 'success_upload', 'payload': payload_dict}
            server_host = self.ser_ip.GetValue()
            server_port = int(self.ser_port.GetValue())
            soc = client.Client(server_host, server_port)
            soc.socket_send(ready_to_send)

        else:
            self.upload_list.SetItem(index, 3, "Upload Failed")

        self.counterlock.acquire()
        try:
            self.uploadcounter +=1
        finally:
            self.counterlock.release()


    def check_ser_ok(self):
        self.check_ser_ok_flag = True #True is  OK.
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            soc.connect((self.ser_ip.GetValue(), int(self.ser_port.GetValue())))
        except:
            self.check_ser_ok_flag = False
        finally:
            soc.close()
            return self.check_ser_ok_flag


    def cloud_upload_evt(self, event):

        check_ser_ok = self.check_ser_ok()

        if self.check_login_flag and check_ser_ok and len(self.file_paths) !=0:

            self.len_upload_files = len(self.file_paths)
            self.uploadcounter = 0
            s3 = s3action.amazons3(self.access, self.key)
            self.counterlock = threading.Lock()
            for index, element in enumerate(zip(self.file_paths, self.file_names)):
                # element[0] is path, element[1] is name
                th = threading.Thread(target=self.upload_to_s3, args=(s3, element[0], element[1], index), daemon=True)
                th.start()
                time.sleep(.1)

            counter_th = threading.Thread(target=self.uploading_counter, args=(), daemon=True)
            counter_th.start()
        elif not self.check_login_flag:
            return wx.MessageDialog(None, u'Please login.', u"Cloud Upload Services",
                                    wx.OK | wx.ICON_ERROR).ShowModal()
        elif not len(self.file_paths) != 0:
            return wx.MessageDialog(None, u'Please add file(s) into upload list.', u"Cloud Upload Services",
                                    wx.OK | wx.ICON_ERROR).ShowModal()
        elif not self.check_ser_ok_flag:
            return wx.MessageDialog(None, u'The server connection unavailable.', u"Cloud Upload Services",
                                    wx.OK | wx.ICON_ERROR).ShowModal()
        else:
            return wx.MessageDialog(None, u'Error', u"Cloud Upload Services",
                                    wx.OK | wx.ICON_ERROR).ShowModal()

        event.Skip()


    def clean_evt(self, event):
        self.upload_list.DeleteAllItems()
        self.file_paths = []
        self.file_names = []
        self.upload_current_status.SetLabel("All upload waiting list clear.")
        event.Skip()


    def thread_counter(self):
        while 1:
            print("Current active threading number: ", threading.active_count())
            time.sleep(1)



class MyApp(wx.App):
    def OnInit(self):
        self.frame = Upload(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
