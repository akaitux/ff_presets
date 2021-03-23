import pathlib


def get_project_location():
    current_dir = pathlib.Path(__file__).parent
    project_path = pathlib.Path(current_dir, '../../')
    return project_path


VIDEO_PRESET_DICT = {
    'aspect': '16:9',
    'bf': 2,
    'bitrate': '200k',
    'codec': 'tratata',
    'bufsize': '25m',
    'crf': 25,
    'fps': 20,
    'gop': 250,
    'no_scenecut': True,
    'tune': 'zerolatency',
    'maxrate': '25m',
    'preset': 'high',
    'profile': 'baseline',
    'level': 3.0,
    'qscale': 1,
    'refs': 1,
    'size': '1920x1080',
    'vframes': 20,
    'force_key_frames': "expr:gte(t,n_forced*2)",
    'forced-idr': True,
    'cbr': True,
    'x264_params': [
        {'level': '31'},
        {'ref': 3},
        "no-scenecut",
        {'vbv_maxrate': 6096},
    ],
    'x265_params': [
        {'level': '31'},
        {'ref': 3},
        "no-scenecut",
        {'vbv_maxrate': 6096},
    ],
    'filter_chains': [
        {
            'name': 'chain1',
            'filters': [
                {
                    'name': 'yadif',
                    'values': [0, 0, 0]
                },
                {
                    'name': 'drawtext',
                    'values': [{'text': 'hey'}]
                },
                'pullup',
                'hwupload_cuda',
            ],
        },
        {
            'name': 'chain2',
            'filters': [
                "some_filter"
            ]
        }
    ],
    'rc': 'vbr_hq',
    'rc-lookahead': 32,
    'cq': 20,
    'zerolatency': True,
    'spatial-aq': 1,
    'aq-strength': 12,
    'coder': 'cabac',
    'output_ts_offset': "$(date +%s.%N)",
    'additional_params': '-test 123 -test2 "test"',
}

AUDIO_PRESET_DICT = {
    'bitrate': '128k',
    'codec': 'libfdk_aac',
    'sample_rate': 44100,
    'ac': 1,
}

STREAM_PRESET_DICT = {
    'ffmpeg_params': [
        'deinterlace',
        {'fflags': '+genpts'},
        {'vsync': 0},
    ],
    'vdecoder': 'h264_cuvid',
    'hwaccel': 'cuda',
    'hwaccel_device': 0,
    'input': [
        {'addr': 'http://input', 'maps': ['0', {'0': 0}, {'0': 'v'}, {'0': 'p:1344'}, {'i': '0x401'}]},
        'http://...'

    ],
    'output': [
        {
            'video_preset': 'fullhd_tests',
            'audio_preset': 'aac_tests',
            'format': 'flv',
            'outputs': [
                {
                    'select': 'v:0,a',
                    'addr': 'local0',
                    'onfail': 'ignore',
                },
                {
                    'select': 'v:0,a',
                    'format': 'flv',
                    'addr': 'rtmp://server0/app/instance',
                }
            ],
            'hls_params': {
                'hls_param1': 123,
                'hls_param2': 456
            }
        }
    ]
}

CONFIG_DICT = {
    'presets': pathlib.Path(get_project_location(), "presets/"),
    'streams': pathlib.Path(get_project_location(), "presets/streams")
}
