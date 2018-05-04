import wx
import client
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


class Sign_up(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((400, 300))
        self.text_ctrl_username = wx.TextCtrl(self, wx.ID_ANY, "")
        self.text_ctrl_password = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PASSWORD)
        self.text_ctrl_confirm_password = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PASSWORD)
        self.submit = wx.Button(self, wx.ID_ANY, "Submit")
        self.button_cancel = wx.Button(self, wx.ID_ANY, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.submit_btn, self.submit)
        self.Bind(wx.EVT_BUTTON, self.cancel_btn, self.button_cancel)

        self.ser_ip = 'localhost'
        self.ser_port = 50001
        self.aws_accesskey = ""
        self.aws_secretkey = ""
        self.aws_bucket_for_upload = "iems5703asiatokyo"

    def __set_properties(self):
        self.SetTitle("Sign up")
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.text_ctrl_username.SetMinSize((150, 22))
        self.text_ctrl_password.SetMinSize((150, 22))
        self.text_ctrl_confirm_password.SetMinSize((150, 22))

    def __do_layout(self):
        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_18 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.GridSizer(0, 2, 0, 0)
        label_title = wx.StaticText(self, wx.ID_ANY, "Sign Up")
        label_title.SetFont(wx.Font(30, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_18.Add(label_title, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 20)
        label_username = wx.StaticText(self, wx.ID_ANY, "Username")
        grid_sizer_1.Add(label_username, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.text_ctrl_username, 0, wx.ALIGN_CENTER, 0)
        label_password = wx.StaticText(self, wx.ID_ANY, "Password")
        grid_sizer_1.Add(label_password, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.text_ctrl_password, 0, wx.ALIGN_CENTER, 0)
        label_confirm_password = wx.StaticText(self, wx.ID_ANY, "Confirm passowrd")
        grid_sizer_1.Add(label_confirm_password, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.text_ctrl_confirm_password, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.submit, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_1.Add(self.button_cancel, 0, wx.ALIGN_CENTER, 0)
        sizer_18.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_17.Add(sizer_18, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_17)
        self.Layout()

    def submit_btn(self, event):

        if not len(self.text_ctrl_username.GetValue()) > 0 and not len(self.text_ctrl_password.GetValue()) > 0:
            return wx.MessageDialog(None, u'Invalid username or password', u"Error",
                                    wx.OK | wx.ICON_ERROR).ShowModal()

        if not self.text_ctrl_password.GetValue() == self.text_ctrl_confirm_password.GetValue():
            return wx.MessageDialog(None, u'Password and Confirm password are not same.', u"Sign Up",
                                    wx.OK | wx.ICON_ERROR).ShowModal()

        payload_dict = { 'user_name':self.text_ctrl_username.GetValue(),
                         'password': self.text_ctrl_password.GetValue(),
                         'ser_ip': self.ser_ip,
                         'ser_port': str(self.ser_port),
                         'aws_accesskey':self.aws_accesskey,
                         'aws_secretkey': self.aws_secretkey,
                         'aws_bucket_for_upload':self.aws_bucket_for_upload
                        }
        ready_to_send = {'action': 'signup_btn', 'payload': payload_dict}

        try:
            soc = client.Client(self.ser_ip, int(self.ser_port))
            response = soc.socket_send(ready_to_send)
            print(response)
        except:
            print("signup submit_btn/ Error")
            return wx.MessageDialog(None, u'Connection NOT OK', u"Server Connection",
                                    wx.OK | wx.ICON_ERROR).ShowModal()

        if response: #if false, may be user name already exisit.
            self.Close()
            event.Skip()
            return wx.MessageDialog(None, u'You are successfully registered.', u"Sign Up",
                                    wx.OK | wx.ICON_INFORMATION).ShowModal()
        else:
            return wx.MessageDialog(None, u'You are not successfully registered.', u"Sign Up",
                                    wx.OK | wx.ICON_ERROR).ShowModal()

        event.Skip()


    def cancel_btn(self, event):
        self.Close()
        event.Skip()


class Signup(wx.App):
    def OnInit(self):
        self.signup = Signup(None, wx.ID_ANY, "")
        self.SetTopWindow(self.signup)
        self.signup.Show()
        return True


if __name__ == "__main__":
    app = Signup(0)
    app.MainLoop()
