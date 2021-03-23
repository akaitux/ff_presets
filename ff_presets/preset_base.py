from ff_presets.config import Config
import logging
import os


def parse_maps(maps) -> str:
    cmd = []
    if not maps:
        return ''
    for fmap in maps:
        if isinstance(fmap, dict):
            for k, v in fmap.items():
                cmd.append('-map {}:{}'.format(k, v))
        else:
            cmd.append('-map {}'.format(fmap))
    return ' '.join(cmd)


class _Preset:

    def __init__(self, name: str = None, src: dict = None, stream_number: str = None, presets_path='presets'):
        self.stream_number = stream_number
        self._validation_errors = []
        self._cfg = Config()
        self._cmd = []
        self.presets_path = self._cfg.presets_path
        if src is None and (self.presets_path is None or not os.path.exists(self.presets_path)):
            msg = "Не указан пресет как словарь, не указан путь к пресетам или директория не существует ({})".format(name)
            logging.error(msg)
            raise ValueError(msg)
        self.path = None
        self._src = None
        self.name = name

    @property
    def is_valid(self) -> bool:
        if len(self.validation_errors) > 0:
            logging.error('Найдены ошибки при валидации:')
            for error in self.validation_errors:
                logging.error('VALIDATION_ERROR: {}'.format(error))
            return False
        return True

    @property
    def cmd(self) -> [str, None]:
        if len(self._validation_errors) > 0:
            logging.debug("Ошибки при проверке шаблона {}".format(self.name))
            msg = ''
            for error in self._validation_errors:
                msg += error + '\n'
            logging.debug(msg)
            return ''
        if len(self._cmd) > 0:
            cmd = [x for x in self._cmd if x]
            return ' '.join(cmd)

    @property
    def validation_errors(self):
        return self._validation_errors

    def _get_single_param(self, param_name, ptype, param=None):
        if param is None:
            param = self._src.get(param_name, None)
        if param is None:
            return None
        if ptype == float and isinstance(param, int):
            return param
        if not isinstance(param, ptype):
            msg = 'Шаблон {}. Ошибка при валидации параметра {}. Ожидаемый тип - {}.'.format(self.name, param_name, ptype)
            msg += ' Полученный - {}'.format(type(param))
            self._validation_errors.append(msg)
            return None
        return param

    def _validate_weight_param(self, param):
        is_error = False
        if not param:
            return
        if str(param)[-1].lower() in ['b', 'k', 'm', 'g']:
            if not str(param[:-1]).isdigit():
                is_error = True
        elif not is_error:
            check = self._get_single_param('bitrate', int, param)
            if not check:
                is_error = True
        if not is_error and param:
            return param

    def _get_stream_param(self, param_name, ptype, param=None):
        if param is None:
            param = self._src.get(param_name, None)
        if param is None:
            return None
        if isinstance(param, ptype) and self.stream_number is not None:
            param = {'value': param, 'stream': int(self.stream_number)}
        if isinstance(param, ptype):
            return param
        if not isinstance(param, dict):
            msg = 'Ошибка при валидации параметра {pname} . Ожидаемый тип - {ptype} или' \
                  ' {pname}: value: {ptype}, stream: 0. Полученный - {getted}.'
            msg = msg.format(pname=param_name, ptype=ptype, getted=type(param))
            self._validation_errors.append(msg)
            return None
        if 'value' not in param or 'stream' not in param:
            msg = 'Ошибка при валидации параметра {}. Должен быть словарем и содержать ключи ' \
                  '"value" со значением параметра и "stream" с номером потока'
            msg = msg.format(param_name)
            self._validation_errors.append(msg)
            return None
        if not isinstance(param['value'], ptype):
            msg = 'Ошибка при валидации параметра {}.value . Ожидаемый тип - {}'
            msg = msg.format(param_name, ptype)
            self._validation_errors.append(msg)
            return None
        if not isinstance(param['stream'], int):
            msg = 'Ошибка при валидации параметра {}.stream. Ожидаемый тип - {}'
            msg = msg.format(param_name, int)
            self._validation_errors.append(msg)
            return None
        return param

    def _parse_filter_chains(self, chains, mutations=None):
        "mutations - list of functions which change filter (str or dict) and return new changed filter"
        if not chains:
            return
        chains_cmd = []
        for chain in chains:
            chains_cmd.append(self._parse_chain(chain, mutations=mutations))
        chains_cmd = [x for x in chains_cmd if x is not None]
        chains_cmd = ';'.join(chains_cmd)
        return chains_cmd

    def _parse_chain(self, chain, mutations=None):
        "mutations - list of functions which change filter (str or dict) and return new changed filter"
        chain_cmd = []
        if 'filters' not in chain or chain.get('filters') is None:
            msg = 'Неправильный формат chain {}, нет ключей "name" или "filters"'.format(chain)
            self._validation_errors.append(msg)
            return
        for filter_ in chain['filters']:
            if mutations:
                for mutation in mutations:
                    filter_ = mutation(filter_)
            chain_cmd.append(self._parse_filter(filter_))
        chain_cmd = [x for x in chain_cmd if x is not None]
        chain_cmd = ','.join(chain_cmd)
        return chain_cmd

    def _parse_filter(self, filter):
        if isinstance(filter, dict):
            if 'name' not in filter or 'values' not in filter:
                msg = 'Неправильный формат фильтра {}, нет ключей "name" или "values"'.format(filter)
                self._validation_errors.append(msg)
                return
            filter_values = []
            for value in filter['values']:
                if isinstance(value, dict):
                    for k, v in value.items():
                        filter_values.append("{}={}".format(k, v))
                elif value is not None:
                    filter_values.append(str(value))
            filter_values = ':'.join(filter_values)
            filter_cmd = '{}={}'.format(filter['name'], filter_values)
            return filter_cmd
        elif isinstance(filter, str):
            return filter

    def _gen_xparams(self, params):
        params = self._get_single_param('x264_params', list)
        if not params:
            return
        cmd = []
        for param in params:
            if isinstance(param, dict):
                for k, v in param.items():
                    cmd.append('{}={}'.format(k, v))
            else:
                cmd.append('{}'.format(param))
        cmd = ':'.join(cmd)
        return cmd

