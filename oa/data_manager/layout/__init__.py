"""
This app defines the models and views that describe the layout of a farm. All
farms must contain a set of :class:`Tray`s, each of which contains a set of
:class:`PlantSite`s. All farms also contain an :class:`Enclosure` that wraps
the rest of the layout tree. Additional layers of abstraction between
:class:`Tray` and :class:`Enclosure` can be defined by the user in schema
files. There is a set of default layout schema for common farm layouts, but it
is also possible to define custom layout schema in simple configuration files.
For more information on the structure of these files, see
:file:`schemata/__init__.py`.
"""
default_app_config = 'oa.data_manager.layout.apps.LayoutConfig'
