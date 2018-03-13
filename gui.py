# -*- coding: utf-8 -*-
import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, BorderImage
from kivy.uix.image import Image

from kivy.uix.actionbar import ActionBar, ActionView, ActionButton, ActionPrevious

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

from kivy.uix.dropdown import DropDown

from test_server import Server
from database import Users

import threading
import os
import socket

ORIGINAL_DIR = os.getcwd()
users = Users(os.getcwd())


class OptionsButton(Button):
    def __init__(self, **kwargs):
        super(OptionsButton, self).__init__(**kwargs)
        self.dropdown_options = DropDown()
        self.password = kwargs['password']
        self.user = kwargs['user']
        remove_button = Button(text='Remove User', size_hint_y=None, height=44)
        remove_button.bind(on_release=lambda btn: self.dropdown_options.select(btn))
        remove_button.color = (1, 1, 1, 1)
        remove_button.background_color = (1, 0, 0, 1)
        self.dropdown_options.add_widget(remove_button)

        self.dropdown_options.bind(on_select=self.remove_self)

    def remove_self(self, instance, value):
        users.remove_user(self.user, self.password)
        self.parent.remove_widget(self)


class DatabaseUsers(ScrollView):
    def __init__(self, **kwargs):
        super(DatabaseUsers, self).__init__(**kwargs)
        self.users = Users(ORIGINAL_DIR)
        self.user_pass = self.users.get_users_pass()
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        for user, password in self.user_pass:
            self.user_button = OptionsButton(text='user: %s, pass: %s' % (user, password), size_hint_y=None, user=user, password=password)
            self.user_button.bind(on_press=self.user_button.dropdown_options.open)
            self.layout.add_widget(self.user_button)

        self.add_widget(self.layout)


class AddUser(RelativeLayout):
    def __init__(self, user_list, **kwargs):
        super(AddUser, self).__init__(**kwargs)
        self.user_list = user_list
        self.username_input = TextInput(multiline=False, size_hint=(0.25, 0.15), pos_hint={'center_x': 0.8, 'center_y': 0.3})
        self.add_widget(self.username_input)
        self.password_input = TextInput(multiline=False, size_hint=(0.25, 0.15), pos_hint={'center_x': 0.8, 'center_y': 0.1})
        self.password_input.bind(on_text_validate=self.add_to_database)
        self.add_widget(self.password_input)
        self.button_add = Button(text='Add User', pos_hint={'center_x': 0.2, 'center_y': 0.2}, size_hint=(0.25, 0.4))
        self.button_add.bind(on_press=self.add_to_database)
        self.add_widget(self.button_add)

    def add_to_database(self, instance):
        user = self.username_input.text
        password = self.password_input.text
        print self.user_list.users.add_user(self.username_input.text, self.password_input.text)
        new_user = OptionsButton(text='user: %s, pass: %s' % (user, password), size_hint_y=None, user=user, password=password)
        new_user.bind(on_press=new_user.dropdown_options.open)
        self.user_list.layout.add_widget(new_user)


class DatabaseManageContent(RelativeLayout):
    def __init__(self):
        super(DatabaseManageContent, self).__init__()
        self.user_list = DatabaseUsers(size_hint=(1, 0.5), pos_hint={'top': 1})
        self.add_widget(self.user_list)
        self.add_widget(AddUser(self.user_list))


class ServerSetup(Popup):
    def __init__(self, output_log):
        super(ServerSetup, self).__init__()
        self.title = 'Start Server'
        self.content = ServerSetupContent(self, output_log)
        self.size_hint = (0.9, 0.8)


class ServerSetupContent(RelativeLayout):
    def __init__(self, popup, output_log):
        super(ServerSetupContent, self).__init__()
        self.server = None
        self.output_log = output_log

        self.port = TextInput(multiline=False, size_hint=(0.4, 0.2), pos_hint = {'center_x': 0.75, 'center_y': 0.75},
                              font_size=42)
        self.port.bind(on_text_validate=self.start_server)
        self.add_widget(self.port)

        self.port_label = Label(text='Enter port to run on:', font_name='Arial', pos_hint={'center_x': 0.28, 'center_y': 0.75}, font_size=36)
        self.add_widget(self.port_label)

        self.start_button = Button(text='Start', size_hint=(0.7, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.35})
        self.start_button.bind(on_press=self.start_server)
        self.add_widget(self.start_button)

        # Button to close popup
        self.popup = popup
        self.close = Button(text="Close", size_hint=(0.7, 0.2), pos_hint={'center_x': 0.5, 'y': 0.025})
        self.close.bind(on_press=self.popup.dismiss)
        self.add_widget(self.close)

    def start_server(self, instance):
        try:
            self.server = Server(int(self.port.text), self.output_log, socket.gethostbyname(socket.gethostname()))
        except ValueError:
            self.output_log.add_text('invalid character')
            return
        self.thread = threading.Thread(target=self.server.run)
        self.thread.daemon = True
        self.thread.start()
        self.output_log.add_text("Server started")
        close_server_button = Button(text='Close Server', size_hint=(0.3, 0.1), pos_hint={'top': 0.2, 'right': 0.4},
                                     color=(0, 0, 1, 5))
        close_server_button.bind(on_press=self.close_server)
        self.output_log.parent.add_widget(close_server_button)

        self.popup.dismiss()

    def close_server(self, instance):
        instance.parent.remove_widget(instance)
        self.server.close_server()
        self.server = None


class TaskBar(ActionBar):
    def __init__(self, output_log):
        super(TaskBar, self).__init__(pos_hint={'top': 1})
        self.action_view = ActionView()
        self.action_view.add_widget(ActionPrevious(title='FTP Server', with_previous=False))
        # button to enter the start server setup
        self.start_server = ActionButton(text="Start Server", font_name='Arial')
        self.start_popup = ServerSetup(output_log)
        self.start_server.bind(on_press=self.start_popup.open)
        self.action_view.add_widget(self.start_server)

        self.database_button = ActionButton(text="Manage Database", font_name='Arial')
        self.database_popup = Popup(title='Manage Database', content=DatabaseManageContent(), size_hint=(0.9, 0.8))
        self.database_button.bind(on_press=self.database_popup.open)
        self.action_view.add_widget(self.database_button)

        self.add_widget(self.action_view)


class ScrollableLabel(ScrollView):

    def __init__(self, **kwargs):
        super(ScrollableLabel, self).__init__(**kwargs)
        self.label = Label(size_hint=(1, None), text_size=(self.width, None), size=Window.size)
        self.label.bind(texture_size=self._set_summary_height)
        self.label.text_size = (self.label.width, None)
        self.add_widget(self.label)
        self.bar_width = 9

    @staticmethod
    def _set_summary_height(instance, size):
        """
        Changes size to enable scrolling
        """
        instance.height = size[1]
        instance.width = size[0]


class LogOutput(ScrollableLabel):
    """
    Label where output of what the server is doing will be written
    """
    def __init__(self, **kwargs):
        super(LogOutput, self).__init__(**kwargs)
        #self.canvas.
        # text color
        self.label.color = 0, 0, 0, 0.5
        self.label.outline_color = 1, 1, 1, 1
        self.label.outline_width = 2
        self.label.font_size = 16

    def add_text(self, message):
        self.label.text += message + '\n'
        # if self.text.count('\n') > 6:  # MAX LINES = 6
        #     self.text = '\n'.join(self.text.split('\n')[-4::])  # 4 = LINES TO KEEP


class StartWindow(RelativeLayout):
    def __init__(self):
        super(StartWindow, self).__init__()
        # background
        self.image = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.image)
        # text output
        self.output = LogOutput(size_hint=(1, 0.5), size=(self.width, self.height), pos_hint={'center_y': 0.65})
        self.output.bind(size=self._update_rect, pos=self._update_rect)

        with self.output.canvas.before:
            #Color(0.3, 0.3, 0.3, 1)
            Color(0, 0, 1, 0.5)
            #self.rect = Rectangle(size=self.output.size, pos=self.output.pos)
            self.rect = BorderImage(
                source='output_background.png',
                pos=self.output.pos,
                size=self.output.size,
            )

        self.add_widget(self.output)
        # action bar
        self.add_widget(TaskBar(self.output))

        # connected clients
        #self.connected = Label(text=)

    def _update_rect(self, instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size


class FTPApp(App):

    def build(self):
        return StartWindow()


def main():
    """
    Starts gui of python socket FTP server.
    """
    FTPApp().run()


if __name__ == '__main__':
    main()