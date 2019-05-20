from __future__ import absolute_import

from . import defaults


class Style(object):
    """Style

    Args:
        style (str, dict): The style for the layer. It can be a dictionary or a viz string.
          More info at
          `CARTO VL styling <https://carto.com/developers/carto-vl/guides/style-with-expressions/>`

    Example:

        String API.

        .. code::
            from cartoframes.vis import Style

            Style('color: blue')

            Style('''
                @sum: sqrt($pop_max) / 100
                @grad: [red, blue, green]
                color: ramp(globalEqIntervals($pop_min, 3), @grad)
                filter: @sum > 20
            ''')

        Dict API.

        .. code::
            from cartoframes.vis import Style

            Style({
                'color': 'blue'
            })

            Style({
                'vars': {
                    'sum': 'sqrt($pop_max) / 100',
                    'grad': '[red, blue, green]'
                },
                'color': 'ramp(globalEqIntervals($pop_min, 3), @grad)',
                'filter': '@sum > 20'
            })
    """

    def __init__(self, style=None):
        self._style = self._init_style(style)

    def _init_style(self, style):
        if style is None:
            return defaults.STYLE_DEFAULTS
        elif isinstance(style, (str, dict)):
            return style
        else:
            raise ValueError('`style` must be a string or a dictionary')

    def compute_viz(self, geom_type=None, variables={}):
        style = self._style
        if isinstance(style, dict):
            if geom_type and geom_type in style:
                style = style.get(geom_type)
            return self._parse_style_dict(style, variables)
        elif isinstance(style, str):
            return self._parse_style_str(style, variables)
        else:
            raise ValueError('`style` must be a string or a dictionary')

    def _parse_style_dict(self, style, ext_vars):
        style_vars = style.get('vars', {})
        variables = dict(style_vars.items() + ext_vars.items())

        serialized_variables = self._serialize_variables(variables)
        serialized_properties = self._serialize_properties(style)
    
        return serialized_variables + serialized_properties

    def _parse_style_str(self, style, ext_vars):
        serialized_variables = self._serialize_variables(ext_vars)

        return '{0}\n{1}'.format(serialized_variables, style)

    def _serialize_variables(self, variables={}):
        output = ''
        for var in variables:
            output +='@{name}: {value}\n'.format(
                name=var,
                value=_convstr(variables.get(var))
            )
        return output

    def _serialize_properties(self, properties={}):
        output = ''
        for prop in properties:
            if prop not in defaults.STYLE_PROPERTIES:
                raise ValueError(
                    'Style property "{0}" is not valid. Valid style properties are: {1}'.format(
                        prop,
                        ', '.join(defaults.STYLE_PROPERTIES)
                    ))
            if prop != 'vars':
                output += '{name}: {value}\n'.format(
                    name=prop,
                    value=_convstr(properties.get(prop))
                )
        return output


def _convstr(obj):
    """Converts all types to strings or None"""
    return str(obj) if obj is not None else None
