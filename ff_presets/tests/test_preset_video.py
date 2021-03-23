import copy
from ff_presets.preset_stream import Stream
from ff_presets.preset_video import PVideo
from ff_presets.config import Config
from ff_presets.tests.assets import CONFIG_DICT, VIDEO_PRESET_DICT, STREAM_PRESET_DICT


def gen_config():
    config = Config()
    config.init(CONFIG_DICT)
    config.validation_mode = False
    return config


def gen_dict_preset():
    gen_config()
    stream_preset = gen_dict_stream_preset()
    preset = PVideo('dict_preset', src=VIDEO_PRESET_DICT, stream_preset=stream_preset)
    return preset


def gen_yaml_preset():
    gen_config()
    stream_preset = gen_dict_stream_preset()
    preset = PVideo(name='fullhd_tests', stream_preset=stream_preset)
    return preset


def gen_dict_stream_preset():
    gen_config()
    preset = Stream('dict_preset', src=STREAM_PRESET_DICT)
    return preset


def _test_no_validation_errors(preset):
    print("Ошибки валидации:\n {}".format(preset.validation_errors))
    assert preset.is_valid is True


def _test_validation_errors(preset):
    print("Ошибки валидации:\n {}".format(preset.validation_errors))
    assert preset.is_valid is False


def test_validation_errors():
    yaml_preset = gen_yaml_preset()
    dict_preset = gen_dict_preset()
    _test_no_validation_errors(yaml_preset)
    _test_no_validation_errors(dict_preset)
    yaml_preset._src['bitrate'] = 1234
    dict_preset._src['bitrate'] = "20mm"
    print("Yaml bitrate", yaml_preset.bitrate)
    print("Dict bitrate", dict_preset.bitrate)
    _test_validation_errors(yaml_preset)
    _test_validation_errors(dict_preset)


def test_zerolatency():
    preset_conf = copy.deepcopy(VIDEO_PRESET_DICT)
    preset_conf['codec'] = 'h264_nvenc'
    preset = PVideo('dict_preset', src=preset_conf)
    assert '-zerolatency 1' == preset.zerolatency
    preset_conf['codec'] = 'h264'
    preset = PVideo('dict_preset', src=preset_conf)
    assert '-tune zerolatency' == preset.zerolatency


def test_params():
    yaml_preset = gen_yaml_preset()
    dict_preset = gen_dict_preset()

    _test_params(yaml_preset, 'asset YAML')
    _test_params(dict_preset, 'asset DICT')


def _test_params(preset, name):
    print("Test {}".format(name))

    assert preset.codec == '-vcodec tratata'

    # assert self.pix_fmt != '-pix_fmt'

    assert preset.crf == '-crf 25'
    preset._src['crf'] = 'test'
    assert preset.crf is None

    assert preset.vframes == '-vframes 20'
    preset._src['vframes'] = 'test'
    assert preset.vframes is None

    assert preset.fps == '-r 20'
    preset._src['fps'] = 'test'
    assert preset.fps is None

    assert preset.size == '-s 1920x1080'

    assert preset.no_scenecut == '-no-scenecut 1'
    preset._src['no_scenecut'] = 1
    assert preset.no_scenecut is None

    assert preset.bitrate == '-b:v 200k'
    preset._src['bitrate'] = '1000mb'
    assert preset.bitrate is None
    preset._src['bitrate'] = 1000
    assert preset.bitrate is None

    assert preset.maxrate == '-maxrate 25m'
    preset._src['maxrate'] = '25mb'
    assert preset.maxrate is None
    preset._src['maxrate'] = 1000
    assert preset.maxrate is None

    assert preset.bufsize == '-bufsize 25m'
    preset._src['bufsize'] = '25mb'
    assert preset.bufsize is None
    preset._src['bufsize'] = 1000
    assert preset.bufsize is None

    assert preset.profile == '-profile:v baseline'

    assert preset.level == '-level 3.0'
    preset._src['level'] = 3
    assert preset.level == '-level 3'

    assert preset.refs == '-refs 1'

    assert preset.tune == '-tune zerolatency'

    assert preset.frames_in_gop == '-g 250'

    assert preset.aspect == '-aspect 16:9'
    preset._src['aspect'] = '16-9'
    assert preset.aspect is None

    assert preset.preset == '-preset high'

    assert preset.qscale == '-qscale 1'

    assert preset.bframes == '-bf 2'

    assert preset.x264_params == '-x264opts level=31:ref=3:no-scenecut:vbv_maxrate=6096'

    assert preset.x265_params == '-x265opts level=31:ref=3:no-scenecut:vbv_maxrate=6096'

    assert preset.filters == '-vf "yadif=0:0:0,drawtext=text=hey,pullup,hwupload_cuda=device=0;some_filter"'
    preset._src['filter_chains'].append({
        'name': 'test_nvidia',
        'filters': [
            {'name': 'hwupload_nvidia', 'values': [
                    {'device': 1},
                ]
            },
        ]
    })
    assert preset.filters == '-vf "yadif=0:0:0,drawtext=text=hey,pullup,hwupload_cuda=device=0;some_filter;hwupload_nvidia=device=1"'

    assert preset.rc == '-rc:v vbr_hq'
    preset._src['rc'] = 5
    assert preset.rc is None

    assert preset.rc_lookahead == '-rc-lookahead:v 32'

    assert preset.cq == '-cq 20'

    assert preset.zerolatency == '-tune zerolatency'
    
    assert preset.spatial_aq == '-spatial-aq:v 1'

    assert preset.aq_strength == '-aq-strength:v 12'

    assert preset.coder == '-coder:v cabac'

    assert preset.force_key_frames == '-force_key_frames "expr:gte(t,n_forced*2)"'

    assert preset.forced_idr == '-forced-idr 1'

    assert preset.cbr == '-cbr 1'

    assert preset.output_ts_offset == '-output_ts_offset "$(date +%s.%N)"'

    assert preset.additional_params == '-test 123 -test2 "test"'
