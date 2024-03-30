jinja
=====

.. jinja:: ctx

    {% for feature in features %}

    {{ feature.properties.title }}
    -----------------------------------------------

    Event: {{ feature.properties.time_str }}

    {{ feature.properties.url }}

    ----

    {% endfor %}

    See also: https://earthquake.usgs.gov/
