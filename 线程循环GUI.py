#coding = utf-8
import os
import time
import queue
import shutil
import pyforms
import traceback
import threading
from pyforms import BaseWidget
from pyforms.controls import ControlText
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo
from pyforms.controls import ControlTextArea
from pyforms.controls import ControlLabel
from pyforms.controls import ControlTextArea
q = queue.Queue()
lock = threading.Lock()


class GoldMonitorGUI(BaseWidget):

    def __init__(self):
        super(GoldMonitorGUI, self).__init__('GoldMonitorGUI')

        self.beginning_price = ControlText('Beginning Price:')

        self.high_limit = ControlText('Email If Higher Than:')
        self.low_limit = ControlText('Email If Lower Than:')

        self.current_price = ControlLabel()

        self.sender_address = ControlText('Sender Address:')
        self.sender_password = ControlText('Sender Password:')

        self.receiver_address = ControlText('Receiver Address:')

        self.current_status_label = ControlLabel('Current Status:')
        self.current_status = ControlLabel(time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())) + ' Program is not running...' + ' ' * 10)

        self.button = ControlButton('OK')
        self.button.value = self.button_action

        self.set_margin(15)
        self.formset = [{
            'Current Price': ['current_price'],
            'Settings':['beginning_price', ('high_limit', 'low_limit'), ('sender_address', 'sender_password'), 'receiver_address', ('current_status_label', 'current_status'), ('button')]
        }]

        self.current_price_value = '正在获取...'
        self.price_value_string = ''
        self.counter = 0
        self.mail_flag = 1

    def button_action(self):
        try:
            self.current_status.value = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())) + '  Program is running...' + ' ' * 10
            self.init_mail_var()
            self.get_price()
            result = list()
            result.append(q.get())
            if self.counter > 14:
                self.price_value_string = ''
                self.price_value_string = result[0]
                self.counter = 0
            else:
                self.price_value_string = self.price_value_string + '\n' + result[0]
            lock.acquire()
            self.current_price.value = self.price_value_string
            lock.release()
            self.counter += 1
            self.t = threading.Timer(1, self.button_action)
            self.t.setDaemon(True)
            self.t.start()
            # self.t.join()
        except Exception as e:
            traceback.print_exc()

    def init_mail_var(self):
        self.my_sender = self.sender_address.value
        self.my_pass = self.sender_password.value
        self.addr = self.receiver_address.value
        try:
            self.receiver_addr = self.addr.split(';')
        except:
            self.receiver_addr = []
            self.receiver_addr.append(self.addr)
        finally:
            self.sender_name = 'GoldMonitor'
            self.sender_password.value = ('*' * 10)  # 将密码隐藏

    def get_price(self):
        price = 270
        beginning_price = self.beginning_price.value
        percent = ((float(price) - float(beginning_price)) / float(beginning_price)) * 100
        self.current_price_value = (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' 数据获取成功:' +
                                    str(price) + ',涨跌幅为' + str(round(percent, 3)) + '%' + '盈亏为' + str((round(percent, 3) * 75)))
        if self.mail_flag == 1:
            self.func_1(price)
        else:
            pass
        q.put(self.current_price_value)

    def func_1(self, price):
        print("hello" + str(price))
        self.mail_flag = 0
        timer = threading.Timer(5, self.func_2)
        timer.start()

    def func_2(self):
        self.mail_flag = 1

    def send_mail(self, price):
        if price < float(self.low_limit.value):  # 黄金价格一旦低于self.low_limit.value
            subject = 'Goldprice'
            content = '黄金的价格目前为%s,价格较低，可以买入' % (price)
            MS = MailSender(self.my_sender, self.my_pass, self.sender_name, self.receiver_addr, subject, content)
            MS.send_it()
        if price > float(self.high_limit.value):  # 黄金价格一旦高于self.high_limit.value
            subject = 'Goldprice'
            content = '黄金的价格目前为%s,价格较高，可以卖出' % (price)
            MS = MailSender(self.my_sender, self.my_pass, self.sender_name, self.receiver_addr, subject, content)
            MS.send_it()


if __name__ == "__main__":
    pyforms.start_app(GoldMonitorGUI)
