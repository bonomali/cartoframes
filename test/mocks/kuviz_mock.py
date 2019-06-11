from carto.kuvizs import Kuviz

from cartoframes.viz.kuviz import KuvizPublisher, PRIVACY_PUBLIC, PRIVACY_PASSWORD, _validate_carto_kuviz, \
    kuviz_to_dict


class CartoKuvizMock(Kuviz):
    def __init__(self, name, id='a12345', url="https://carto.com", password=None):
        self.id = id
        self.url = url
        self.name = name
        if password:
            self.privacy = PRIVACY_PASSWORD
        else:
            self.privacy = PRIVACY_PUBLIC

    def delete(self):
        return True

    def save(self):
        return True


def _create_kuviz(html, name, context=None, password=None):
    carto_kuviz = CartoKuvizMock(name=name, password=password)
    _validate_carto_kuviz(carto_kuviz)
    return carto_kuviz


class KuvizPublisherMock(KuvizPublisher):
    def publish(self, html, name, password=None):
        return _create_kuviz(html=html, name=name, context=self._context, password=password)

    def _sync_layer(self, layer, table_name, context):
        layer.source.dataset._is_saved_in_carto = True

    def is_public(self):
        return True

    @staticmethod
    def all():
        kuviz = CartoKuvizMock(name="test")
        kuvizs = [kuviz, kuviz, kuviz]
        return [kuviz_to_dict(kuviz) for kuviz in kuvizs]
