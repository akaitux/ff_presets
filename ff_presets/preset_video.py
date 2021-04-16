import os
from ff_presets.config import read_yaml
from ff_presets.preset_base import _Preset
import copy


class PVideo(_Preset):
    def __init__(self, name: str = None, src: dict = None, stream_number: str = None, stream_preset: _Preset = None):
        '''
        name - если не указана переменная preset - путь к файлу, относительно директории с видео пресетами, если указана - название пресета, нужное для трейса
        src - словарь с пресетом, который будет использован вместо загрузки из yaml
        stream_number - указание номера потока, который будет подставляться в ключи
        '''
        super().__init__(name=name, src=src, stream_number=stream_number)
        self.stream_number = stream_number
        self.stream_preset = stream_preset
        self._cmd = []
        if not self.name and src:
            self.name = src.get('name', None)
        if name is None:
            self._cmd.append('-vn')
            return
        if not src:
            self.path = os.path.join(self.presets_path, 'video', str(name))
            if not self.path.endswith('.yaml'):
                self.path += '.yaml'
            self._src = read_yaml(self.path)
        else:
            self._src = copy.deepcopy(src)
        self._cmd.append(self.size)
        self._cmd.append(self.codec)
        self._cmd.append(self.pix_fmt)
        self._cmd.append(self.crf)
        self._cmd.append(self.vframes)
        self._cmd.append(self.fps)
        self._cmd.append(self.no_scenecut)
        self._cmd.append(self.bitrate)
        self._cmd.append(self.maxrate)
        self._cmd.append(self.bufsize)
        self._cmd.append(self.profile)
        self._cmd.append(self.level)
        self._cmd.append(self.refs)
        self._cmd.append(self.tune)
        self._cmd.append(self.frames_in_gop)
        self._cmd.append(self.aspect)
        self._cmd.append(self.preset)
        self._cmd.append(self.qscale)
        self._cmd.append(self.bframes)
        self._cmd.append(self.x264_params)
        self._cmd.append(self.x265_params)
        self._cmd.append(self.filters)
        self._cmd.append(self.rc)
        self._cmd.append(self.cbr)
        self._cmd.append(self.rc_lookahead)
        self._cmd.append(self.cq)
        self._cmd.append(self.zerolatency)
        self._cmd.append(self.spatial_aq)
        self._cmd.append(self.aq_strength)
        self._cmd.append(self.coder)
        self._cmd.append(self.force_key_frames)
        self._cmd.append(self.forced_idr)
        self._cmd.append(self.output_ts_offset)
        self._cmd.append(self.additional_params)
        if self._cmd:
            self._cmd = [x for x in self._cmd if x]

    def _nvidia_filters_mutation(self, filter_):
        if not filter_:
            return
        if isinstance(filter_, dict):
            filter_ = copy.deepcopy(filter_)
            if filter_.get('name') == 'hwupload_cuda':
                if not self.stream_preset or self.stream_preset.hwaccel_device_num is None:
                    return filter_
                is_device_val = [x for x in filter_.get('values', []) if x == 'hwupload_cuda']
                if is_device_val:
                    return filter_
                filter_['values'].append({
                    'device': self.stream_preset.hwaccel_device_num
                })
                return filter_
        if isinstance(filter_, str):
            if filter_ == 'hwupload_cuda':
                if not self.stream_preset or self.stream_preset.hwaccel_device_num is None:
                    return filter_
                filter_ = {'name': 'hwupload_cuda', 'values': [{'device': self.stream_preset.hwaccel_device_num}]}
                return filter_
        return filter_

    @property
    def vframes(self) -> [str, None]:
        vframes = self._get_single_param('vframes', int)
        if vframes:
            return '-vframes {}'.format(vframes)

    @property
    def crf(self) -> [str, None]:
        crf = self._get_single_param('crf', int)
        if crf:
            return '-crf {}'.format(crf)

    @property
    def pix_fmt(self) -> [str, None]:
        pix_fmt = self._get_single_param('pix_fmt', str)
        if pix_fmt:
            return '-pix_fmt {}'.format(pix_fmt)

    @property
    def fps(self) -> [str, None]:
        fps = self._get_stream_param('fps', int)
        if isinstance(fps, dict):
            return '-r:{} {}'.format(fps['stream'], fps['value'])
        elif fps:
            return '-r {}'.format(fps)

    @property
    def size(self) -> [str, None]:
        size = self._get_stream_param('size', str)
        errmsg = 'Неправильный формат параметра size, ожидается <width>x<height>'
        if isinstance(size, dict):
            if 'x' not in size['value']:
                self._validation_errors.append(errmsg)
                return None
            return '-s:{} {}'.format(size['stream'], size['value'])
        elif size:
            if 'x' not in size:
                self._validation_errors.append(errmsg)
                return None
            return '-s {}'.format(size)

    @property
    def codec(self) -> [str, None]:
        codec = self._get_stream_param('codec', str)
        if codec:
            if isinstance(codec, dict):
                return '-vcodec:{} {}'.format(codec['stream'], codec['value'])
            else:
                return '-vcodec {}'.format(codec)

    @property
    def bitrate(self) -> [str, None]:
        bitrate = self._get_single_param('bitrate', str)
        if not bitrate:
            return
        bitrate = self._validate_weight_param(bitrate)
        if not bitrate:
            msg = 'Шаблон {}. Ошибка при валидации параметра bitrate'.format(self.name)
            self._validation_errors.append(msg)
            return
        return '-b:v {}'.format(bitrate)

    @property
    def maxrate(self) -> [str, None]:
        maxrate = self._get_single_param('maxrate', str)
        if not maxrate:
            return
        maxrate = self._validate_weight_param(maxrate)
        if not maxrate:
            msg = 'Шаблон {}. Ошибка при валидации параметра maxrate'.format(self.name)
            self._validation_errors.append(msg)
            return
        return '-maxrate {}'.format(maxrate)

    @property
    def bufsize(self) -> [str, None]:
        bufsize = self._get_single_param('bufsize', str)
        if not bufsize:
            return
        bufsize = self._validate_weight_param(bufsize)
        if not bufsize:
            msg = 'Шаблон {}. Ошибка при валидации параметра bufsize'.format(self.name)
            self._validation_errors.append(msg)
            return
        return '-bufsize {}'.format(bufsize)

    @property
    def profile(self) -> [str, None]:
        profile = self._get_single_param('profile', str)
        if profile:
            return '-profile:v {}'.format(profile)

    @property
    def level(self) -> [str, None]:
        level = self._get_single_param('level', float)
        if level:
            return '-level {}'.format(level)

    @property
    def refs(self) -> [str, None]:
        refs = self._get_single_param('refs', int)
        if refs:
            return '-refs {}'.format(refs)

    @property
    def tune(self) -> [str, None]:
        tune = self._get_single_param('tune', str)
        if tune:
            return '-tune {}'.format(tune)

    @property
    def frames_in_gop(self) -> [str, None]:
        gop = self._get_single_param('gop', int)
        if gop:
            return '-g {}'.format(gop)

    @property
    def aspect(self) -> [str, None]:
        aspect = self._get_stream_param('aspect', str)
        errmsg = 'Шаблон {}. Неправильный формат параметра aspect, ожидается <width>:<height>'.format(self.name)
        if isinstance(aspect, dict):
            if ':' not in aspect['value']:
                self._validation_errors.append(errmsg)
                return None
            return '-aspect:{} {}'.format(aspect['stream'], aspect['value'])
        elif aspect:
            if ':' not in aspect:
                self._validation_errors.append(errmsg)
                return None
            return '-aspect {}'.format(aspect)

    @property
    def preset(self) -> [str, None]:
        preset = self._get_stream_param('preset', str)
        if isinstance(preset, dict):
            return '-preset:{} {}'.format(preset['stream'], preset['value'])
        elif preset:
            return '-preset {}'.format(preset)

    @property
    def qscale(self) -> [str, None]:
        qscale = self._get_stream_param('qscale', int)
        if isinstance(qscale, dict):
            return '-qscale:{} {}'.format(qscale['stream'], qscale['value'])
        elif qscale:
            return '-qscale {}'.format(qscale)

    @property
    def bframes(self) -> [str, None]:
        bf = self._get_single_param('bf', int)
        if bf:
            return '-bf {}'.format(bf)

    @property
    def x264_params(self) -> [str, None]:
        params = self._get_single_param('x264_params', list)
        if params:
            params = self._gen_xparams(params)
            return '-x264opts {}'.format(params)

    @property
    def x265_params(self) -> [str, None]:
        params = self._get_single_param('x265_params', list)
        if params:
            params = self._gen_xparams(params)
            return '-x265opts {}'.format(params)

    @property
    def filters(self) -> [str, None]:
        chains = self._get_single_param('filter_chains', list)
        if chains:
            filters = self._parse_filter_chains(chains, mutations=[self._nvidia_filters_mutation, ])
            if filters:
                return '-vf "{}"'.format(filters)

    # NVENC
    @property
    def rc(self) -> [str, None]:
        rc = self._get_single_param('rc', str)
        if rc:
            return '-rc:v {}'.format(rc)

    # NVENC
    @property
    def rc_lookahead(self) -> [str, None]:
        rcl = self._get_single_param('rc-lookahead', int)
        if rcl:
            return '-rc-lookahead:v {}'.format(rcl)

    # NVENC
    @property
    def cq(self) -> [str, None]:
        cq = self._get_single_param('cq', float)
        if cq:
            return '-cq {}'.format(cq)

    @property
    def zerolatency(self) -> [str, None]:
        param = self._get_single_param('zerolatency', bool)
        if param: 
            if 'h264_nvenc' in self.cmd or 'h265_nvenc' in self.cmd:
                return '-zerolatency 1'
            else:
                return '-tune zerolatency'

    # NVENC
    @property
    def spatial_aq(self) -> [str, None]:
        sa = self._get_single_param('spatial-aq', int)
        if not sa:
            return
        if str(sa) != '1':
            self._validation_errors.append("spatial_aq должен быть равен 1")
            return
        return '-spatial-aq:v {}'.format(sa)

    # NVENC
    @property
    def aq_strength(self) -> [str, None]:
        aq = self._get_single_param('aq-strength', int)
        if aq:
            return '-aq-strength:v {}'.format(aq)

    # NVENC
    @property
    def coder(self) -> [str, None]:
        coder = self._get_single_param('coder', str)
        if coder:
            return '-coder:v {}'.format(coder)

    @property
    def force_key_frames(self) -> [str, None]:
        force_key_frames = self._get_single_param('force_key_frames', str)
        if force_key_frames:
            return r'-force_key_frames "{}"'.format(force_key_frames)

    @property
    def forced_idr(self) -> [str, None]:
        forced_idr = self._get_single_param('forced-idr', bool)
        if forced_idr:
            return '-forced-idr 1'

    # NVENC
    @property
    def cbr(self) -> [str, None]:
        cbr = self._get_single_param('cbr', bool)
        if cbr:
            return '-cbr 1'

    @property
    def output_ts_offset(self) -> [str, None]:
        output_ts_offset = self._get_single_param('output_ts_offset', str)
        if output_ts_offset:
            return '-output_ts_offset "{}"'.format(output_ts_offset)

    @property
    def no_scenecut(self) -> [str, None]:
        no_scenecut = self._get_single_param('no_scenecut', bool)
        if no_scenecut:
            return '-no-scenecut 1'

    @property
    def additional_params(self) -> [str, None]:
        return self._get_single_param('additional_params', str)
