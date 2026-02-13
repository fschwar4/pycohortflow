``cfd_util`` — Utilities
========================

.. module:: pycohortflow.cfd_util

This module provides colour handling, text wrapping, figure saving, and
TOML-based style configuration loading.

Configuration
-------------

.. autofunction:: load_style_config

Colour Utilities
----------------

.. autofunction:: gradient_palette

.. autofunction:: resolve_color

.. autofunction:: get_matplotlib_named_colors

.. autofunction:: named_color

Figure I/O
----------

.. autofunction:: save_figure

Text Helpers
------------

.. autofunction:: wrap_lines

Internal Helpers
----------------

The following functions are used internally and are not part of the public
API.  They are documented here for contributors.

.. autofunction:: _hex_to_rgb

.. autofunction:: _rgb_to_hex

.. autofunction:: _interpolate_color

.. autofunction:: _recursive_update
