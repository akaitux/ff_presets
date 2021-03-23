#!/usr/bin/env python3
from ff_presets.config import Config
from ff_presets.preset_stream import Stream
from ff_presets.preset_video import PVideo
from ff_presets.preset_audio import PAudio
import traceback
import pathlib
import sys
import json


def main():
    cfg = Config()
    if cfg.args.info:
        info(cfg)
        return
    try:
        if cfg.args.stream:
            preset = Stream(name=cfg.args.stream)
        elif cfg.args.video:
            preset = PVideo(name=cfg.args.video)
        elif cfg.args.audio: 
            preset = PAudio(name=cfg.args.audio)
        else:
            cfg.parser.print_help()
            sys.exit(0)
    except Exception as e:
        print(str(e))
        if cfg.debug:
            print(traceback.format_exc())
        sys.exit(1)
    if not preset.is_valid:
        print("Валидация стрима {} не пройдена".format(preset.name))
        sys.exit(1)
    print(preset.cmd)


def _info_print_dir(path: pathlib.Path, parents=None):
    for s in path.iterdir():
        if s.is_dir():
            if not parents:
                parents = []
            _info_print_dir(s, parents + [s, ])
        else:
            if parents:
                printed_path = '/'.join([x.name for x in parents]) + '/' + s.name
            else:
                printed_path = s.name
            print('\t{}'.format(printed_path))


def _get_json_paths(path: pathlib.Path, parents=None):
    paths = []
    for s in path.iterdir():
        if s.is_dir():
            if not parents:
                parents = []
            paths += _get_json_paths(s, parents + [s, ])
        else:
            if parents:
                path = '/'.join([x.name for x in parents]) + '/' + s.name
            else:
                path = s.name
            paths.append(path)
    return paths


def info(cfg):
    if not cfg.streams_path or not cfg.presets_path:
        msg = "Не найдены директории presets и streams\n"
        msg += "Их можно указать в конфиге (presets: <path>, streams: <path>), через аргументы "
        msg += "или запустить скрипт из директории, где уже есть presets и presets/streams"
        print(msg)
        sys.exit(1)
    streams_path = pathlib.Path(cfg.streams_path)
    presets_path = pathlib.Path(cfg.presets_path)
    audio_presets_path = pathlib.Path(presets_path, 'audio')
    video_presets_path = pathlib.Path(presets_path, 'video')
    if not cfg.args.json:
        print('Config: {}'.format(cfg.app_cfg_path))
        print('Presets dir: {}'.format(presets_path))
        print('Streams dir: {}'.format(streams_path))
        print('Video presets dir: {}'.format(video_presets_path))
        print('Audio presets dir: {}'.format(audio_presets_path))
        print('Streams:')
        _info_print_dir(streams_path)
        print('Audio presets:')
        _info_print_dir(audio_presets_path)
        print('Video presets:')
        _info_print_dir(video_presets_path)
    else:
        output = {'streams_path': str(streams_path),
                  'video_presets_path': str(video_presets_path),
                  'audio_presets_path': str(audio_presets_path),
                  'streams': _get_json_paths(streams_path),
                  'audio_presets': _get_json_paths(audio_presets_path),
                  'video_presets': _get_json_paths(video_presets_path),
                  }
        print(json.dumps(output))


def find_same_outputs():
    pass


if __name__ == "__main__":
    main()
