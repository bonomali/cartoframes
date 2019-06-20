from __future__ import absolute_import

from ..layer import Layer


def size_continuous_layer(source, value, title='', size=None, color=None):
    """Helper function for quickly creating a size symbol map with
    continuous size scaled by `value`.

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by
        title (str, optional): Title of legend
        size (str, optiona): Min/max size array in CARTO VL syntax. Default is
          '[2, 40]' for point geometries and '[1, 10]' for lines.
        color (str, optional): Hex value, rgb expression, or other valid
          CARTO VL color. Defaults is '#FFB927' for point geometries and
          '#4CC8A3' for lines.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`. Includes Legend and
        popup on `value`.
    """
    return Layer(
        source,
        style={
            'point': {
                'width': 'ramp(linear(sqrt(${0}), sqrt(globalMin(${0})), sqrt(globalMax(${0}))), {1})'.format(
                    value, size or [2, 40]),
                'color': 'opacity({0}, 0.8)'.format(color or '#FFB927'),
                'strokeColor': 'opacity(#222,ramp(linear(zoom(),0,18),[0,0.6]))'
            },
            'line': {
                'width': 'ramp(linear(${0}), {1})'.format(value, size or [1, 10]),
                'color': 'opacity({0}, 0.8)'.format(color or '#4CC8A3')
            }
        },
        popup={
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend={
            'type': {
                'point': 'size-continuous-point',
                'line': 'size-continuous-line',
                'polygon': 'size-continuous-polygon'
            },
            'title': title or value,
            'description': ''
        }
    )