from ff_presets.preset_stream import Stream
from ff_presets.config import Config
from ff_presets.tests.assets import CONFIG_DICT, STREAM_PRESET_DICT


def gen_config():
    config = Config()
    config.init(CONFIG_DICT)
    config.validation_mode = False
    return config


def gen_dict_preset():
    gen_config()
    preset = Stream('dict_preset', src=STREAM_PRESET_DICT)
    return preset


def gen_yaml_preset():
    gen_config()
    preset = Stream('stream_tests.yaml')
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
    yaml_preset._src['vdecoder'] = 123
    dict_preset._src['vdecoder'] = 123
    print('Yaml vdecoder: ', yaml_preset.vdecoder)
    print('Dict vdecoder: ', dict_preset.vdecoder)
    _test_validation_errors(yaml_preset)
    _test_validation_errors(dict_preset)


def test_params():
    yaml_preset = gen_yaml_preset()
    dict_preset = gen_dict_preset()
    _test_params(yaml_preset, 'YAML')
    _test_params(dict_preset, 'DICT')


def _test_params(preset, name):
    print('Test asset {}'.format(name))
    assert preset.ffmpeg_params == '-deinterlace -fflags +genpts -vsync 0'
    assert preset.hwaccel == '-hwaccel cuda'
    assert preset.hwaccel_device == '-hwaccel_device 0'
    assert preset.vdecoder == '-c:v h264_cuvid'
    assert preset.inputs == '-i http://input -map 0 -map 0:0 -map 0:v -map 0:p:1344 -map i:0x401 -i http://...'
    assert preset.outputs