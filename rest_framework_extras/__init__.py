class Mapping(object):
    _di = {}

    def set(self, key, value):
        self._di[key] = value

    def get(self, key):
        return self._di.get(key, None)


class_form_mapping = Mapping()
