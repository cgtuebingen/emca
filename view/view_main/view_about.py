"""
    MIT License

    Copyright (c) 2020 Christoph Kreisl
    Copyright (c) 2021 Lukas Ruppert

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from core.pyside2_uic import loadUi
from PySide2.QtCore import Qt
from PySide2.QtCore import Slot
from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QApplication
import os
import base64
import six
import logging


class ViewAbout(QWidget):

    """
        ViewAbout
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        ui_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'about.ui'))
        loadUi(ui_filepath, self)

        # center widget depending on screen size
        desktop_widget = QApplication.desktop()
        screen_rect = desktop_widget.availableGeometry(self)
        self.move(screen_rect.center() - self.rect().center())

        # Info
        by_developer = b'xt6Wp83ozdjq09XehLDoyc7p0A'
        mail = b'0Mnb1eDV2NzVic3b4YrU3tLK3NiVwt2V1M7hlNHQ3ZXRxg'
        github_link = b'z93o2Oiclpjb0enK3Muiy-TPlszf2trL2tWjzeLFyA'
        github = '<a href=\"{0}\" style=\"color: white;\">{0}</a>'.format(self.decode("github", github_link))

        version_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'VERSION'))
        version_number = self.get_current_version(version_filepath)

        contributors_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'CONTRIBUTORS'))
        contributors = self.get_contributors(contributors_filepath)
        self.textContributors.append(contributors)

        self.labelBy.setText(self.decode("dev", by_developer))
        self.labelVersionNumber.setText(version_number)
        self.labelMyMail.setText(self.decode("mail", mail))
        self.labelMyMail.setWindowFlag(Qt.FramelessWindowHint)
        self.labelMyMail.setAttribute(Qt.WA_NoSystemBackground)
        self.labelMyMail.setAttribute(Qt.WA_TranslucentBackground)

        self.labelGithubLink.setText(github)
        self.labelGithubLink.setWindowFlag(Qt.FramelessWindowHint)
        self.labelGithubLink.setAttribute(Qt.WA_NoSystemBackground)
        self.labelGithubLink.setAttribute(Qt.WA_TranslucentBackground)

        self.pbDonate.clicked.connect(self.donate)
        self.pbClose.clicked.connect(self.close)

    @Slot(bool, name='donate')
    def donate(self):
        QDesktopServices.openUrl(QUrl(self.decode("donate", b'zOPi0eefk57l2OuT1NDn0dXRktzTkNfQ1tTX1OA'), QUrl.TolerantMode))

    @staticmethod
    def get_current_version(version_filepath):
        if not os.path.exists(version_filepath):
            raise FileExistsError('VERSION file does not exist')
        with open(version_filepath, 'r') as file:
            return file.readline()

    @staticmethod
    def get_contributors(contributors_filepath):
        if not os.path.exists(contributors_filepath):
            raise FileExistsError('CONTRIBUTORS file does not exist')
        with open(contributors_filepath, 'r') as file:
            contributors = file.readlines()
        contributors = [x.rstrip("\n") for x in contributors]
        contributors = list(filter(None, contributors))
        return ", ".join(contributors)

    @staticmethod
    def encode(key, string):
        encoded_chars = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
            encoded_chars.append(encoded_c)
        encoded_string = ''.join(encoded_chars)
        encoded_string = encoded_string.encode('latin') if six.PY3 else encoded_string
        return base64.urlsafe_b64encode(encoded_string).rstrip(b'=')

    @staticmethod
    def decode(key, string):
        string = base64.urlsafe_b64decode(string + b'===')
        string = string.decode('latin') if six.PY3 else string
        encoded_chars = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
            encoded_chars.append(encoded_c)
        encoded_string = ''.join(encoded_chars)
        return encoded_string
