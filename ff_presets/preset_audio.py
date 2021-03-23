import os
from ff_presets.config import read_yaml
from ff_presets.preset_base import _Preset
import copy


class PAudio(_Preset):
    def __init__(self, name: str = None, src: dict = None, stream_number: str = None, stream_preset: _Preset = None):
        '''
        name - если не указана переменная preset - путь к файлу, относительно директории с аудио пресетами,
             если указана - название пресета, нужное для трейса
        src - словарь с пресетом, который будет использован вместо загрузки из yaml
        stream_number - указание номера потока, который будет подставляться в ключи
        '''
        super().__init__(name=name, src=src, stream_number=stream_number)
        self.stream_number = stream_number
        self._cmd = []
        if not self.name and src:
            self.name = src.get('name', None)
        if name is None:
            self._cmd.append('-an')
            return
        if not src:
            self.path = os.path.join(self.presets_path, 'audio', str(name))
            if not self.path.endswith('.yaml'):
                self.path += '.yaml'
            self._src = read_yaml(self.path)
        else:
            self._src = copy.deepcopy(src)
        self._cmd.append(self.codec)
        self._cmd.append(self.bitrate)
        self._cmd.append(self.sample_rate)
        self._cmd.append(self.ac)

    @property
    def codec(self) -> [str, None]:
        codec = self._get_stream_param('codec', str)
        if codec:
            if isinstance(codec, dict):
                return '-acodec:{} {}'.format(codec['stream'], codec['value'])
            else:
                return '-acodec {}'.format(codec)

    @property
    def bitrate(self) -> [str, None]:
        bitrate = self._get_single_param('bitrate', str)
        if not bitrate:
            return
        bitrate = self._validate_weight_param(bitrate)
        if not bitrate:
            msg = 'Ошибка при валидации параметра bitrate'
            self._validation_errors.append(msg)
            return
        return '-b:a {}'.format(bitrate)

    @property
    def sample_rate(self) -> [str, None]:
        sample_rate = self._get_single_param('sample_rate', int)
        if sample_rate:
            return '-ar {}'.format(sample_rate)

    @property
    def ac(self) -> str:
        ac = self._get_single_param('ac', int)
        if ac:
            return '-ac {}'.format(ac)

    @property
    def filters(self) -> [str, None]:
        chains = self._get_single_param('filter_chains', list)
        if chains:
            filters = self._parse_filter_chains(chains)
            if filters:
                return '-af {}'.format(filters)
