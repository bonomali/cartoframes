from __future__ import absolute_import

from ..utils import gen_variable_name


class Popup(object):
    """Popup

    Args:
        data (dict): The popup definition for a layer. It contains the information
          to show a popup on 'click' and 'hover' events with the attributes provided
          in the definition using the `VL expressions syntax
          <https://carto.com/developers/carto-vl/reference/#cartoexpressions>`.

    Example:

        Show columns.

        .. code::
            from cartoframes.vis import Popup

            Popup({
                'hover': ['$name'],
                'click': ['$name', '$pop_max']
            })

        Show expressions.

        .. code::
            from cartoframes.vis import Popup

            Popup({
                'click': ['$pop_min % 100', 'sqrt($pop_max)']
            })

        Show labels.

        .. code::
            from cartoframes.vis import Popup

            Popup({
                'hover': [{
                    'label': 'Name',
                    'value': '$name'
                }],
                'click': [{
                    'label': 'Name',
                    'value': '$name'
                }, {
                    'label': 'Pop max',
                    'value': '$pop_max'
                }]
            })

    """

    def __init__(self, data=None):
        self._init_popup(data)

    def _init_popup(self, data):
        self._click = []
        self._hover = []
        if data is not None:
            if isinstance(data, dict):
                # TODO: error control
                if 'click' in data:
                    self._click = data.get('click', [])
                if 'hover' in data:
                    self._hover = data.get('hover', [])
            else:
                raise ValueError('Wrong popup input')

    def get_interactivity(self):
        interactivity = []
        if len(self._click) > 0:
            interactivity.append({
                'event': 'click',
                'attrs': self._get_attrs(self._click)
            })
        if len(self._hover) > 0:
            interactivity.append({
                'event': 'hover',
                'attrs': self._get_attrs(self._hover)
            })
        return interactivity

    def _get_attrs(self, array):
        output = []
        for item in array:
            if item:
                if isinstance(item, str):
                    output.append({
                        'name': gen_variable_name(item),
                        'label': item
                    })
                elif isinstance(item, dict) and 'value' in item:
                    output.append({
                        'name': gen_variable_name(item.get('value')),
                        'label': item.get('label')
                    })
                else:
                    raise ValueError('Wrong popup input')
        return output

    def get_variables(self):
        variables = {}
        self._get_vars(variables, self._click)
        self._get_vars(variables, self._hover)
        return variables

    def _get_vars(self, output, array):
        for item in array:
            if item:
                if isinstance(item, str):
                    name = gen_variable_name(item)
                    output[name] = item
                elif isinstance(item, dict) and 'value' in item:
                    name = gen_variable_name(item.get('value'))
                    output[name] = item.get('value')
                else:
                    raise ValueError('Wrong popup input')
