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

import configparser
import os
import logging
import typing


class OptionsConfig(object):

    def __init__(self):
        self._config = configparser.ConfigParser()
        self._path_resources = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
        self._filename = 'options.ini'
        self._filepath = os.path.join(self._path_resources, self._filename)

        logging.info("Loading optionis.ini file")
        if os.path.exists(self._filepath):
            logging.info('... file exists loading configurations')
            # load options.ini from resource folder
            try:
                self._config.read(self._filepath)
            except Exception as e:
                logging.error('Loading options.ini file failed: {}'.format(e))

        if not self._config.has_section('Theme'):
            self._config.add_section('Theme')
        if not self._config.has_section('Options'):
            self._config.add_section('Options')
        if not self._config.has_section('Last'):
            self._config.add_section('Last')

    @property
    def theme(self) -> str:
        return self._config['Theme'].get('theme', 'dark')

    @theme.setter
    def theme(self, theme : str):
        if theme == 'dark' or theme == 'light':
            self._config['Theme']['theme'] = theme
        else:
            logging.error("Wrong theme type...(dark|light)")

    @property
    def auto_connect(self) -> bool:
        return self._config['Options'].get('auto_connect', 'False') == 'True'

    @auto_connect.setter
    def auto_connect(self, value : bool):
        self._config['Options']['auto_connect'] = str(value)

    @property
    def auto_scene_load(self) -> bool:
        return self._config['Options'].get('auto_scene_load', 'False') == 'True'

    @auto_scene_load.setter
    def auto_scene_load(self, value : bool):
        self._config['Options']['auto_scene_load'] = str(value)

    @property
    def auto_image_load(self) -> bool:
        return self._config['Options'].get('auto_rendered_image_load', 'False') == 'True'

    @auto_image_load.setter
    def auto_image_load(self, value : bool):
        self._config['Options']['auto_rendered_image_load'] = str(value)

    @property
    def last_hostname(self) -> str:
        return self._config['Last'].get('hostname', 'localhost')

    @last_hostname.setter
    def last_hostname(self, hostname : str):
        self._config['Last']['hostname'] = hostname

    @property
    def last_port(self) -> int:
        return int(self._config['Last'].get('port', '50013'))

    @last_port.setter
    def last_port(self, port : int):
        self._config['Last']['port'] = str(port)

    @property
    def last_rendered_image_filepath(self) -> typing.Optional[str]:
        return self._config['Last'].get('rendered_image_filepath')

    @last_rendered_image_filepath.setter
    def last_rendered_image_filepath(self, filepath : str):
        self._config['Last']['rendered_image_filepath'] = filepath

    @property
    def last_reference_image_filepath(self) -> typing.Optional[str]:
        return self._config['Last'].get('reference_image_filepath')

    @last_reference_image_filepath.setter
    def last_reference_image_filepath(self, filepath : str):
        self._config['Last']['reference_image_filepath'] = filepath

    def save(self):
        with open(self._filepath, 'w') as configfile:
            self._config.write(configfile)
