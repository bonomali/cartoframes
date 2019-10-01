from .entity import SingleEntity, EntitiesList
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.variable_group_repo import get_variable_group_repo

_DATASET_ID_FIELD = 'id'


class Dataset(SingleEntity):

    id_field = _DATASET_ID_FIELD
    entity_repo = get_dataset_repo()

    def variables(self):
        return get_variable_repo().get_by_dataset(self.id)

    def variables_groups(self):
        return get_variable_group_repo().get_by_dataset(self.id)

    @property
    def id(self):
        return self.data[self.id_field]

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    @property
    def provider(self):
        return self.data['provider_id']

    @property
    def category(self):
        return self.data['category_id']

    @property
    def data_source(self):
        return self.data['data_source_id']

    @property
    def country(self):
        return self.data['country_iso_code3']

    @property
    def language(self):
        return self.data['language_iso_code3']

    @property
    def geography(self):
        return self.data['geography_id']

    @property
    def temporal_aggregation(self):
        return self.data['temporal_aggregation']

    @property
    def time_coverage(self):
        return self.data['time_coverage']

    @property
    def update_frequency(self):
        return self.data['update_frequency']

    @property
    def version(self):
        return self.data['version']

    @property
    def is_public_data(self):
        return self.data['is_public_data']

    @property
    def summary(self):
        return self.data['summary_jsonb']


class Datasets(EntitiesList):

    id_field = _DATASET_ID_FIELD
    entity_repo = get_dataset_repo()

    @classmethod
    def _get_single_entity_class(cls):
        return Dataset
