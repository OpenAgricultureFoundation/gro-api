"""
This module defines a base model class form which all models in this project
should inherit.
"""
from collections import defaultdict
from django.db.models.options import Options
from django.conf import settings
from solo import models as solo_models
from solo import settings as solo_settings
from .utils.enum import ServerType
from .utils.layout import (
    system_layout, LayoutDependentAttribute, LayoutDependentCachedProperty
)

class DynamicOptions(Options):
    is_dynamic = True
    _get_fields_cache = LayoutDependentAttribute('get_fields_cache', default=dict)

    @LayoutDependentCachedProperty
    def fields(self):
        return Options.fields.func(self)

    @LayoutDependentCachedProperty
    def concrete_fields(self):
        return Options.concrete_fields.func(self)

    @LayoutDependentCachedProperty
    def local_concrete_fields(self):
        return Options.local_concrete_fields.func(self)

    @LayoutDependentCachedProperty
    def many_to_many(self):
        return Options.many_to_many.func(self)

    @LayoutDependentCachedProperty
    def related_objects(self):
        return Options.related_objects.func(self)

    @LayoutDependentCachedProperty
    def _forward_fields_map(self):
        return Options._forward_fields_map.func(self)

    @LayoutDependentCachedProperty
    def fields_map(self):
        return Options.fields_map.func(self)

    def _populate_dynamic_directed_relation_graph(self):
        dynamic_related_objects_graph = defaultdict(lambda: defaultdict(list))

        all_models = self.apps.get_models(include_auto_created=True)
        all_dynamic_models = tuple(model for model in all_models if
                model._meta.__class__ is DynamicOptions)
        for model in all_dynamic_models:
            if model._meta.abstract:
                continue
            all_fields = model._meta._get_fields(
                reverse=False, include_parents=False
            )
            fields_with_dynamic_relations = (
                f for f in all_fields if f.is_relation and
                getattr(f, 'is_dynamic', False)
            )
            for f in fields_with_dynamic_relations:
                for layout in system_layout.allowed_values:
                    with system_layout.as_value(layout):
                        if f.rel.to and not isinstance(f.rel.to, str):
                            dynamic_related_objects_graph[f.rel.to._meta][layout].append(f)
        for model in all_dynamic_models:
            model._meta.__dict__['_dynamic_relation_tree'] = \
                dynamic_related_objects_graph[model._meta]
        return self.__dict__['_dynamic_relation_tree']

    @property
    def _dynamic_relation_tree(self):
        if '_dynamic_relation_tree' not in self.__dict__:
            self._populate_dynamic_directed_relation_graph()
        dynamic_relation_tree = self.__dict__['_dynamic_relation_tree']
        return dynamic_relation_tree[system_layout.current_value]

    @property
    def _relation_tree(self):
        if '_relation_tree' not in self.__dict__:
            self._populate_directed_relation_graph()
        if '_dynamic_relation_tree' not in self.__dict__:
            old_relation_tree = self.__dict__['_relation_tree']
            new_relation_tree = [f for f in old_relation_tree
                if not getattr(f, 'is_dynamic', False)]
            self.__dict__['_relation_tree'] = new_relation_tree
        return self._dynamic_relation_tree + self.__dict__['_relation_tree']


if settings.SERVER_TYPE == ServerType.LEAF:
    SingletonModel = solo_models.SingletonModel
else:
    from .middleware import get_request_cache
    class SingletonModel(solo_models.SingletonModel):
        class Meta:
            abstract = True

        @classmethod
        def get_cache_key(cls):
            request_cache = get_request_cache()
            farm = request_cache.get('farm')
            prefix = solo_settings.SOLO_CACHE_PREFIX
            return '{}:{}:{}'.format(prefix, farm, cls.__name__.lower())
