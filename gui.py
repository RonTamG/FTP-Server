# -*- coding: utf-8 -*-
import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from kivy.uix.image import Image

from kivy.uix.actionbar import ActionBar, ActionView, ActionButton, ActionPrevious

from test_server import Server

import threading

class ServerSetup(Popup):
    def __init__(self, server, output_log):
        super(ServerSetup, self).__init__()
        self.title = 'Start Server'
        self.content = ServerSetupContent(self, server, output_log)
        self.size_hint = (0.9, 0.8)


class ServerSetupContent(RelativeLayout):
    def __init__(self, popup, server, output_log):
        super(ServerSetupContent, self).__init__()
        self.server = server
        self.output_log = output_log
        self.port = TextInput(multiline=False, size_hint=(0.4, 0.2), pos_hint = {'center_x': 0.75, 'center_y': 0.75})
        self.add_widget(self.port)
        self.port_label = Label(text='Enter port to run on', pos_hint={'center_x': 0.2, 'center_y': 0.75}, font_size=20)
        self.add_widget(self.port_label)
        self.start_button = Button(text='Start', size_hint=(0.7, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.35})
        self.start_button.bind(on_press=self.start_server)
        self.add_widget(self.start_button)

        # Button to close popup
        self.popup = popup
        self.close = Button(text="Close", size_hint=(0.7, 0.2), pos_hint={'center_x': 0.5})
        self.close.bind(on_press=self.popup.dismiss)
        self.add_widget(self.close)

    def start_server(self, instance):
        self.server = Server(int(self.port.text), self.output_log)
        thread = threading.Thread(target=self.server.run)
        thread.daemon = True
        thread.start()


class TaskBar(ActionBar):
    def __init__(self, server, output_log):
        super(TaskBar, self).__init__(pos_hint={'top': 1})
        self.action_view = ActionView(use_separator=True)
        self.action_view.add_widget(ActionPrevious(title='FTP Server', with_previous=False))
        # button to enter the start server setup
        self.start_server = ActionButton(text="Start Server", font_name='Arial')
        self.start_popup = ServerSetup(server, output_log)
        self.start_server.bind(on_press=self.start_popup.open)
        self.action_view.add_widget(self.start_server)

        self.add_widget(self.action_view)


class LogOutput(Label):
    """
    Label where output of what the server is doing will be written
    """
    def __init__(self, **kwargs):
        super(LogOutput, self).__init__(**kwargs)
        self.color = 0, 0, 0, 0.5
        self.outline_color = 1, 1, 1, 1
        self.outline_width = 2

    def add_text(self, message):
        self.text += message + '\n'
        if self.text.count('\n') > 6:  # MAX LINES = 6
            self.text = '\n'.join(self.text.split('\n')[-4::])  # 4 = LINES TO KEEP

        # text doesn't change label size anymore
        self.text_size = (self.width, None)


class StartWindow(FloatLayout):
    def __init__(self):
        super(StartWindow, self).__init__()
        self.server = None
        # background
        self.image = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.image)
        # text output
        self.output_log = LogOutput(pos_hint={'left': 1, 'top': 1}, size_hint=(0.4, 0.5))
        self.add_widget(self.output_log)
        # action bar
        self.add_widget(TaskBar(self.server, self.output_log))


class FTPApp(App):

    def build(self):
        return StartWindow()


def main():
    """
    Add Documentation here
    """
    FTPApp().run()  # Add Your Code Here


if __name__ == '__main__':
    main()