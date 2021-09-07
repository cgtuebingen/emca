"""
    MIT License

    Copyright (c) 2020 Christoph Kreisl

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

import configparser
import os
import sys
import logging


class OptionsConfig(object):

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._path_resources = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
        self._filename = 'options.ini'
        self._filepath = os.path.join(self._path_resources, self._filename)
        self.load_options_config(self._filepath)

    def load_options_config(self, filepath):
        logging.info("Loading optionis.ini file")
        if os.path.exists(filepath):
            logging.info('... file exists loading configurations')
            # load options.ini from resource folder
            try:
                self._config.read(self._filepath)
            except Exception as e:
                logging.error('Loading options.ini file failed: {}'.format(e))
                sys.exit(1)
        else:
            logging.info('... file does not exist creating new file with default configurations')
            # create options.ini with default settings
            self._config['Theme'] = {'theme': 'dark'}
            self._config['Options'] = {
                'auto_connect': 'False',
                'auto_scene_load': 'False',
                'auto_rendered_image_load': 'False'}
            self._config['Last'] = {
                'hostname': 'localhost',
                'port': '50013',
                'rendered_image_filepath': "",
                'reference_image_filepath': ""}
            with open(self._filepath, 'w') as configfile:
                self._config.write(configfile)
            logging.info("... done. Default auto generated file: {}".format(self._filepath))

    def get_theme(self):
        return self._config['Theme']['theme']

    def set_theme(self, theme):
        if theme == 'dark' or theme == 'light':
            self._config['Theme']['theme'] = theme
        else:
            logging.error("Wrong theme type...(dark|light)")

    def get_option_auto_connect(self):
        try:
            val = self._config['Options']['auto_connect']
            return val == 'True'
        except Exception as e:
            logging.error(e)
            return False

    def set_options_auto_connect(self, value):
        self._config['Options']['auto_connect'] = str(value)

    def get_option_auto_scene_load(self):
        try:
            val = self._config['Options']['auto_scene_load']
            return val == 'True'
        except Exception as e:
            logging.error(e)
            return False

    def set_option_auto_scene_load(self, value):
        self._config['Options']['auto_scene_load'] = str(value)

    def get_option_auto_image_load(self):
        try:
            val = self._config['Options']['auto_rendered_image_load']
            return val == 'True'
        except Exception as e:
            logging.error(e)
            return False

    def set_option_auto_image_load(self, value):
        self._config['Options']['auto_rendered_image_load'] = str(value)

    def get_last_hostname(self):
        return self._config['Last']['hostname']

    def set_last_hostname(self, hostname):
        self._config['Last']['hostname'] = str(hostname)

    def get_last_port(self):
        return int(self._config['Last']['port'])

    def set_last_port(self, port):
        self._config['Last']['port'] = str(port)

    def set_last_hostname_and_port(self, hostname, port):
        if self.get_last_hostname() != hostname:
            self.set_last_hostname(hostname)
        if self.get_last_port() != str(port):
            self.set_last_port(port)

    def get_last_rendered_image_filepath(self):
        path = self._config['Last'].get('rendered_image_filepath', None)
        return path

    def set_last_rendered_image_filepath(self, filepath):
        self._config['Last']['rendered_image_filepath'] = str(filepath)

    def get_last_reference_image_filepath(self):
        path = self._config['Last'].get('reference_image_filepath', None)
        return path

    def set_last_reference_image_filepath(self, filepath):
        self._config['Last']['reference_image_filepath'] = str(filepath)

    def is_last_hostname_set(self):
        return self._config['Last']['hostname'] != ""

    def is_last_port_set(self):
        return self._config['Last']['port'] != ""

    def is_last_rendered_image_filepath_set(self):
        return self._config['Last']['rendered_image_filepath'] != ""

    def is_last_reference_image_filepath_set(self):
        return self._config['Last']['rendered_image_filepath'] != ""

    def save(self):
        with open(self._filepath, 'w') as configfile:
            self._config.write(configfile)
