import base64
import json
import os

from app import common
from app.res.const import Const


class ConfigBase:
    _config_name = ('com.%s.%s' % (Const.author, Const.app_name)).lower()
    _config_path = os.path.expanduser('~/Library/Application Support/%s' % _config_name)
    _protect_fields = []
    language = ''

    def load(self):
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as io:
                    config = json.load(io)
                    for f in self._protect_fields:
                        config[f] = base64.b64decode(config[f][::-1].encode()).decode()
                    common.dict_to_object(config, self, new_fields=False)
                    common.log('config_load', 'Info', common.object_to_dict(self))
        except:
            self.save()

    def save(self):
        with open(self._config_path, 'w') as io:
            config = common.object_to_dict(self)
            for f in self._protect_fields:
                config[f] = base64.b64encode(config[f].encode()).decode()[::-1]
            json.dump(config, io, indent='  ')
            common.log('config_save', 'Info', common.object_to_dict(self))

    def clear(self):
        if os.path.exists(self._config_path):
            os.unlink(self._config_path)
