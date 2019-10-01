from cartoframes.exceptions import DiscoveryException
from .repo_client import RepoClient


def get_variable_repo():
    return _REPO


class VariableRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return self._to_variables(self.client.get_variables())

    def get_by_id(self, variable_id):
        result = self.client.get_variables('id', variable_id)

        if len(result) == 0:
            raise DiscoveryException('The id does not correspond with any existing variable in the catalog. '
                                     'You can check the full list of available variables with Variables.get_all()')

        data = self._from_repo(result[0])
        return self._to_variable(data)

    def get_by_dataset(self, dataset_id):
        return self._to_variables(self.client.get_variables('dataset_id', dataset_id))

    def get_by_variable_group(self, variable_group_id):
        return self._to_variables(self.client.get_variables('variable_group_id', variable_group_id))

    @staticmethod
    def _from_repo(row):
        # TODO: Map properties
        return row

    @staticmethod
    def _to_variable(result):
        from cartoframes.data.observatory.variable import Variable

        return Variable(result)

    @staticmethod
    def _to_variables(results):
        if len(results) == 0:
            return None

        from cartoframes.data.observatory.variable import Variables

        return Variables([VariableRepository._from_repo(result) for result in results])


_REPO = VariableRepository()
