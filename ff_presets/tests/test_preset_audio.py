import pytest
from ff_presets.preset_audio import PAudio
from ff_presets.config import Config
from ff_presets.tests.assets import CONFIG_DICT, AUDIO_PRESET_DICT


@pytest.fixture()
def config():
    config = Config()
    config.init(CONFIG_DICT)
    return config


@pytest.fixture()
def dict_preset(config):
    preset = PAudio('dict_preset', src=AUDIO_PRESET_DICT)
    return preset


@pytest.fixture()
def yaml_preset(config):
    preset = PAudio('aac_tests')
    return preset


def _test_validation_errors(preset):
    print("Ошибки валидации:\n {}".format(preset.validation_errors))
    assert len(preset.validation_errors) == 0


def _test_cmd(preset):
    cmd = '-acodec libfdk_aac -b:a 128k -ar 44100 -ac 1'
    if cmd != preset.cmd:
        print("Шаблон: {}".format(preset.name))
        print("Проверяемый cmd:\n{}".format(preset.cmd))
        print("Требуемый cmd:\n{}".format(cmd))
        assert cmd == preset.cmd


def test_validation_errors(yaml_preset, dict_preset):
    _test_validation_errors(yaml_preset)
    _test_validation_errors(dict_preset)


def test_cmd(yaml_preset, dict_preset):
    _test_cmd(yaml_preset)
    _test_cmd(dict_preset)
