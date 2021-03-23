import pathlib

from ff_presets.config import read_yaml, Config
from ff_presets.preset_base import _Preset, parse_maps
from ff_presets.preset_video import PVideo
from ff_presets.preset_audio import PAudio
import logging
import copy


class _Input:

    def __init__(self, src):
        """
        :param src:
        - input: строка или словарь
        Словарь:
            input: ""
            maps:
              - 0
              - 0: 0
              - 0: v
              - 0: "p:1344"
              - i: "0x401"
        """
        self._src = src
        self._validation_errors = []
        self._input = self._parse_input()
        self._maps = self._parse_maps()

    @property
    def validation_errors(self) -> list:
        return self._validation_errors

    def _parse_input(self) -> str:
        if isinstance(self._src, str):
            cmd = "-i {}".format(self._src)
            return cmd
        if not isinstance(self._src, dict) or 'addr' not in self._src:
            msg = "Ошибка при парсинге Stream файла. input должен быть строкой или словарем с ключами input и maps (" \
                  "optional) "
            self._validation_errors.append(msg)
            return ''
        cmd = "-i {}".format(self._src['addr'])
        return cmd

    def _parse_maps(self) -> str:
        if 'maps' not in self._src:
            return ''
        else:
            return parse_maps(self._src['maps'])

    @property
    def cmd(self):
        cmd = [self._input, self._maps]
        cmd = [x for x in cmd if x]
        return ' '.join(cmd)


class _Output:

    def __init__(self, stream_preset: _Preset, src):
        self.cfg = Config()
        self.stream_preset = stream_preset
        self._src = src
        self._validation_errors = []
        self.video_preset = self._get_video_preset()
        self.audio_preset = self._get_audio_preset()
        self._maps = self._parse_maps()
        self.output = self._setup_outputs

    def _parse_maps(self) -> str:
        if 'maps' not in self._src:
            return ''
        else:
            return parse_maps(self._src['maps'])

    @property
    def validation_errors(self):
        return self._validation_errors

    @property
    def cmd(self) -> str:
        cmd = [self._maps, ]
        if self.video_preset:
            cmd.append(self.video_preset.cmd)
        if self.audio_preset:
            cmd.append(self.audio_preset.cmd)
        if self.output:
            cmd.append(self.output)
        cmd = [x for x in cmd if x]
        return ' '.join(cmd)

    def _get_video_preset(self) -> PVideo:
        stream_number = self._src.get('stream_number', None)
        data = self._src.get('video_preset')
        if isinstance(data, str):
            preset = PVideo(name=data, stream_number=stream_number, stream_preset=self.stream_preset)
        elif isinstance(data, dict):
            if 'name' not in data:
                raise Exception("Нет поля 'name' в видео шаблоне")
            preset = PVideo(name=data['name'], src=data, stream_number=stream_number, stream_preset=self.stream_preset)
        elif data is None:
            return None
        self._validation_errors += preset.validation_errors
        return preset

    def _get_audio_preset(self) -> PAudio:
        stream = self._src.get('stream_number', None)
        data = self._src.get('audio_preset')
        if isinstance(data, str):
            preset = PAudio(name=data, stream_number=stream, stream_preset=self.stream_preset)
        elif isinstance(self._src.get('audio_preset'), dict):
            if 'name' not in data:
                raise Exception("Нет поля 'name' в аудио шаблоне")
            preset = PAudio(name=data['name'], src=data, stream_number=stream, stream_preset=self.stream_preset)
        elif data is None:
            return None
        self._validation_errors += preset.validation_errors
        return preset

    @property
    def _hls_params(self) -> list:
        cmd = []
        if 'hls_params' not in self._src or not isinstance(self._src['hls_params'], dict):
            return cmd
        for k, v in self._src['hls_params'].items():
            cmd.append('-{} {}'.format(k, v))
        return cmd

    @property
    def _setup_outputs(self) -> [str, None]:
        output_addr = self._src.get('output_addr', None)
        outputs = self._src.get('outputs', None)
        oformat = self._src.get('format', None)
        if not output_addr and not outputs:
            msg = 'Ошибка при парсинге одного из output. Требуется ключ output_addr с адресом или outputs со списком ' \
                  'выходных параметров '
            self._validation_errors.append(msg)
            return
        if output_addr and not oformat:
            msg = 'Ошибка при парсинге одного из output. Не указан ключ format'
            self._validation_errors.append(msg)
            return
        cmd = []
        cmd += self._hls_params
        if output_addr:
            cmd.append('-y -f {} {}'.format(oformat, output_addr))
        elif outputs:
            cmd.append(self._create_outputs_tee(outputs))
        cmd = [x for x in cmd if x]
        cmd = ' '.join(cmd)
        return cmd

    def get_fake_output(self) -> str:
        oformat = self._src.get('format', None)
        return '-f {} /dev/null'.format(oformat)

    def _create_outputs_tee(self, outputs):
        tee = []
        for output in outputs:
            tee_chunk = ''
            if 'addr' not in output:
                msg = "Ошибка валидации одного из outputs. При указании нескольких outputs в каждом должен быть ключ " \
                      "addr "
                self._validation_errors.append(msg)
                continue
            select = output.get('select', '')
            tformat = output.get('format', '')
            onfail = output.get('onfail', '')
            addr = output['addr']
            if select or format:
                tee_chunk = []
                if select:
                    tee_chunk.append(r"select=\'{}\'".format(select))
                if format:
                    tee_chunk.append('f={}'.format(tformat))
                if onfail:
                    tee_chunk.append('onfail={}'.format(onfail))
                tee_chunk = ':'.join(tee_chunk)
                tee_chunk = '[{}]'.format(tee_chunk)
            tee_chunk += addr
            tee.append(tee_chunk)
        cmd = '-f tee "{}"'.format('|'.join(tee))
        return cmd


class Stream(_Preset):

    def __init__(self, name: str = None, src: dict = None):
        super().__init__(name=name, src=src)
        self._cfg = Config()
        self.path = None
        self.name = name
        if not self.name:
            self.name = ''
        if src:
            self._src = copy.deepcopy(src)
        elif name:
            self.path = self.get_stream_file_path(name)
            self._src = read_yaml(self.path)
        else:
            msg = 'Ошибка генерации команды для стрима. Не указано название стрима (name) или его данные  (preset)' 
            logging.error(msg)
            raise ValueError(msg)
        self._cmd = self.build_cmd()

    def get_stream_file_path(self, name):
        name = str(name)
        if not name.endswith('.yaml'):
            name += '.yaml'
        if name[0] not in ('//', '.', '~'):
            streams_path = self._cfg.streams_path
            if not streams_path:
                msg = "Не указан путь к стримам или директория не существует"
                logging.error(msg)
                raise Exception(msg)
            return pathlib.Path(streams_path, name)
        else:
            return pathlib.Path(name).resolve()

    def build_cmd(self):
        cmd = [self.ffmpeg_params,
               self.hwaccel,
               self.hwaccel_device,
               self.vdecoder,
               self.inputs,
               self.outputs,
              ]
        cmd = [x for x in cmd if x]
        return cmd

    @property
    def hwaccel(self) -> [str, None]:
        hwaccel = self._get_single_param('hwaccel', str)
        if hwaccel:
            return '-hwaccel {}'.format(hwaccel)

    @property
    def hwaccel_device(self) -> [str, None]:
        hwaccel_device = self._get_single_param('hwaccel_device', int)
        if hwaccel_device is not None:
            return '-hwaccel_device {}'.format(hwaccel_device)

    @property
    def hwaccel_device_num(self) -> [str, None]:
        hwaccel_device_num = self._get_single_param('hwaccel_device', int)
        if hwaccel_device_num is not None:
            return hwaccel_device_num

    @property
    def vdecoder(self) -> [str, None]:
        vdecoder = self._get_single_param('vdecoder', str)
        if vdecoder:
            return '-c:v {}'.format(vdecoder)

    @property
    def ffmpeg_params(self) -> [str, None]:
        cmd = []
        ffmpeg_params = self._get_single_param('ffmpeg_params', list)
        if ffmpeg_params is None:
            return ''
        for param in ffmpeg_params:
            if isinstance(param, str):
                cmd.append('-{}'.format(param))
            if isinstance(param, dict):
                for k, v in param.items():
                    cmd.append('-{} {}'.format(k, v))
        cmd = ' '.join(cmd)
        return cmd

    @property
    def inputs(self) -> [str, None]:
        cmd = []
        inputs_raw = self._get_single_param('input', list)
        if not inputs_raw:
            msg = "Ошибка при парсинге шаблона {}. Требуется указать input".format(self.name)
            self._validation_errors.append(msg)
            return
        for _src in inputs_raw:
            input = _Input(_src)
            self._validation_errors += input.validation_errors
            cmd.append(input.cmd)
        cmd = ' '.join(cmd)
        return cmd

    @property
    def outputs(self) -> [str, None]:
        cmd = []
        outputs_raw = self._get_single_param('output', list)
        if not outputs_raw:
            msg = "Ошибка при парсинге шаблона {}. Требуется указать output".format(self.name)
            self._validation_errors.append(msg)
            return
        for _src in outputs_raw:
            output = _Output(self, _src)
            self._validation_errors += output.validation_errors
            cmd.append(output.cmd)
        cmd = ' '.join(cmd)
        return cmd
