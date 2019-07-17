from __future__ import absolute_import

from ..layer import Layer


def color_continuous_layer(
        source, value, title='', palette=None, description='', footer='',
        legend=True, popup=True, widget=True, animate=None):
    """Helper function for quickly creating a continuous color map

    Args:
        source (:py:class:`Dataset <cartoframes.data.Dataset>` or str): Dataset
          or text representing a table or query associated with user account.
        value (str): Column to symbolize by.
        title (str, optional): Title of legend
        palette (str, optional): Palette that can be a named cartocolor palette
          or other valid CARTO VL palette expression. Default is `bluyl`.
        description (str, optional): Description text legend placed under legend title.
        footer (str, optional): Footer text placed under legend items.
        legend (bool, optional): TODO.
        popup (bool, optional): TODO.
        widget (bool, optional): TODO.
        animate (str, optional): TODO.

    Returns:
        cartoframes.viz.Layer: Layer styled by `value`.
        Includes a legend, popup and widget on `value`.
    """
    animation_filter = 'animation(linear(${}), 20, fade(1,1))'.format(animate) if animate else '1'

    return Layer(
        source,
        style={
            'point': {
                'color': 'ramp(linear(${0}), {1})'.format(
                    value, palette or 'bluyl'),
                'filter': animation_filter
            },
            'line': {
                'color': 'ramp(linear(${0}), {1})'.format(
                    value, palette or 'bluyl'),
                'filter': animation_filter
            },
            'polygon': {
                'color': 'opacity(ramp(linear(${0}), {1}), 0.9)'.format(
                    value, palette or 'bluyl'),
                'filter': animation_filter
            }
        },
        popup=popup and not animate and {
            'hover': {
                'title': title or value,
                'value': '$' + value
            }
        },
        legend=legend and {
            'type': {
                'point': 'color-continuous-point',
                'line': 'color-continuous-line',
                'polygon': 'color-continuous-polygon'
            },
            'title': title or value,
            'description': description,
            'footer': footer
        },
        widgets=[
            animate and {
                'type': 'time-series',
                'value': animate,
                'title': 'Animation'
            },
            widget and {
                'type': 'histogram',
                'value': value,
                'title': 'Distribution'
            }
        ]
    )
