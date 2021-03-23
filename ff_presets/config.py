import logging
import copy
import pathlib
from typing import IO
import argparse
import os
import logging

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sp', '--streams_path', help="Путь к директории со стримами")
    parser.add_argument('-pp', '--presets_path', help="Путь к директории с пресетами")
    parser.add_argument('-c', '--config', help="Путь к конфигу (config.yaml)")
    parser.add_argument('-s', '--stream', help="Название стрима (test_stream или test_stream.yaml из директории со стримами) или путь к файлу")
    parser.add_argument('-a', '--audio', help="Название пресета аудио (test_audio или test_audio.yaml из директории с аудио пресетами) или путь к файлу")
    parser.add_argument('-v', '--video', help="Название пресета видео (test_video или test_video.yaml из директории с видео пресетами) или путь к файлу")
    parser.add_argument('-i', '--info', action='store_true', help="Показать список доступных стримов и пресетов")
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true', help="Вывод только ERROR и CRITICAL")
    parser.add_argument('-j', '--json', action='store_true', help="Используется вместе с -i. Вывод в json формате если это возможно")
    args = parser.parse_args()
    return parser, args


def _read_yaml(stream: IO[str]) -> dict:
    try:
        data = yaml.load(stream, Loader=Loader)
        return data
    except Exception as e:
        logging.error('Error while parsing yaml')
        raise e


def read_yaml(filepath: str) -> dict:
    with open(str(filepath), 'r') as stream:
        return _read_yaml(stream)


class Config:
    _instance = None
    _first_run = True

    # standalone - имеется ввиду запуск как самостоятельной CLI утилиты
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._first_run = True
        else:
            cls._first_run = False
        return cls._instance

    def __init__(self, is_library_mode=False):
        if not self._first_run:
            return
        self.is_library_mode = is_library_mode
        self.debug = False
        self.args = {}
        self.params = {}
        if not is_library_mode:
            self._init_cli()
        else:
            self._init_lib()

    def _init_cli(self):
        self.parser, self.args = parse_args()
        self.debug = self.args.debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
        elif self.args.quiet:
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=logging.INFO)
        self.app_cfg_path = self._find_config()
        try:
            self.params = read_yaml(self.app_cfg_path)
        except FileNotFoundError:
            logging.debug('Файл конфигурации не найден ({})'.format(self.app_cfg_path))
            self.params = {}
        if not self.params:
            logging.debug('Конфигурационный файл пуст')
    
    def _init_lib(self):
        pass

    def _find_config(self):
        app_cfg_path = None
        if self.args.config:
            return self.args.config
        current_dir = pathlib.Path(__file__).parent
        app_cfg_path = pathlib.Path(current_dir, '../config.yaml')
        if not os.path.exists(str(app_cfg_path)):
            app_cfg_path = pathlib.Path(current_dir, '/opt/ff_presets/conf/config.yaml')
        if not os.path.exists(str(app_cfg_path)):
            app_cfg_path = pathlib.Path(current_dir, '/etc/ff_presets/config.yaml')
        if not os.path.exists(str(app_cfg_path)):
            return None
        return app_cfg_path

    def init(self, config):
        self.params = config

    def set(self, parameter: str, value: any) -> None:
        self.params[parameter] = value

    def get(self, parameter: str, empty: any = '') -> any:
        result = self.params.get(parameter, None)
        if result is not None:
            return copy.deepcopy(result)
        else:
            return empty

    @property
    def presets_path(self) -> str:
        if not self.args or 'presets_path' not in self.args:
            return None
        if self.args.presets_path:
            presets_path = self.args.presets_path
        else:
            presets_path = self.get('presets', None)
        if presets_path and not os.path.exists(presets_path):
            logging.debug('Директория со пресетами из конфига не найдена, включен автопоиск')
            presets_path = None
        if not presets_path and 'presets' in os.listdir():
            presets_path = os.path.join(os.getcwd(), 'presets')
        if presets_path and not os.path.exists(presets_path):
            return None
        return presets_path

    @property
    def streams_path(self) -> str:
        if self.args.streams_path:
            streams_path = self.args.streams_path
        else:
            streams_path = self.get('streams', None)
        if streams_path and not os.path.exists(streams_path):
            logging.debug('Директория со стримами из конфига не найдена, включен автопоиск')
            streams_path = None
        if not streams_path and self.presets_path:
            if 'streams' in os.listdir(self.presets_path):
                streams_path = os.path.join(self.presets_path, 'streams')
        if not streams_path and 'presets' in os.listdir():
            if 'streams' in os.listdir('presets'):
                streams_path = os.path.join(os.getcwd(), 'presets/streams')
        if not streams_path and 'streams' in os.listdir():
            streams_path = os.path.join(os.getcwd(), 'streams')
        if streams_path and not os.path.exists(streams_path):
            return None
        return streams_path

