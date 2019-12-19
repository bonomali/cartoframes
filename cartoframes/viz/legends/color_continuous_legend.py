from __future__ import absolute_import

from ..legend import Legend


def color_continuous_legend(title='', description='', footer='', prop='color',
                            variable=None, dynamic=True):
    """Helper function for quickly creating a color continuous legend

    Args:
        title (str, optional):
            Title of legend.
        description (str, optional):
            Description in legend.
        footer (str, optional):
            Footer of legend. This is often used to attribute data sources.
        prop (str, optional): Allowed properties are 'color' and 'stroke-color'.
            It is 'color' by default.
        variable (str, optional):
            If the information in the legend depends on a different value than the
            information set to the style property, it is possible to set an independent
            variable.
        dynamic (boolean, optional):
            Update and render the legend depending on viewport changes.
            Defaults to ``True``.

    Returns:
        A 'color-continuous' :py:class:`Legend <cartoframes.viz.Legend>`

    Examples:

        Default legend:

        .. code::

            from cartoframes.viz import Map, Layer, color_continuous_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=color_continuous_style('collisiontype')
                    legends=color_continuous_legend()
                )
            )

        Legend with custom parameters:

        .. code::

            from cartoframes.viz import Map, Layer, color_continuous_legend

            Map(
                Layer(
                    'seattle_collisions',
                    style=color_continuous_style('amount')
                    legends=color_continuous_legend(
                      title='Collision Type',
                      description="Seattle Collisions"
                      dynamic=False
                    )
                )
            )
    """

    return Legend('color-continuous', title, description, footer, prop, variable, dynamic)
