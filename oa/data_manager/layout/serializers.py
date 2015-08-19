"""
This module creates serializers for some of the models defines in the
layout.models module
"""
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_detail_view_name
from ..data_manager.serializers import BaseSerializer
from ..farms.models import Farm
from ..resources.models import Resource
from .models import (
    Model3D, TrayLayout, PlantSiteLayout, Enclosure, Tray, PlantSite,
    dynamic_models
)


class Model3DSerializer(BaseSerializer):
    class Meta:
        model = Model3D


class TrayLayoutSerializer(BaseSerializer):
    class Meta:
        model = TrayLayout
    # TODO: Remove this once it is implemented in the frontend
    condition = serializers.ChoiceField(
        ('all', 'odd', 'even', 'none'), write_only=True, required=False
    )

    def create_sites(self, instance, condition):
        if condition == 'all':
            def should_create(row, col):
                return True
        elif condition == 'odd':
            def should_create(row, col):
                return bool((row + col) % 2)
        elif condition == 'even':
            def should_create(row, col):
                return bool((row + col + 1) % 2)
        elif condition == 'none':
            def should_create(row, col):
                return False
        sites = []
        for row in range(instance.num_rows):
            for col in range(instance.num_cols):
                if should_create(row, col):
                    sites.append(
                        PlantSiteLayout(parent=instance, row=row, col=col)
                    )
        PlantSiteLayout.objects.bulk_create(sites)

    def clear_sites(self, instance):
        for site in instance.plant_sites.all():
            site.delete()

    def create(self, validated_data):
        condition = validated_data.pop('condition', 'none')
        instance = super().create(validated_data)
        self.create_sites(instance, condition)
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.num_rows = validated_data.get('num_rows', instance.num_rows)
        instance.num_cols = validated_data.get('num_cols', instance.num_cols)
        condition = validated_data.pop('condition', 'none')
        self.clear_sites(instance)
        self.create_sites(instance, condition)
        instance.save()
        return instance


class PlantSiteLayoutSerializer(BaseSerializer):
    class Meta:
        model = PlantSiteLayout

class ResourcesMixin:
    """
    :class:`cityfarm_api.serializers.BaseSerializer` doesn't know how to
    automatically serialize generic relations, so we treat them as serializer
    methods and implement the getter in this mixin for reuse
    """
    resources_view_name = get_detail_view_name(Resource)

    def get_resources(self, obj):
        child = serializers.HyperlinkedIdentityField(
            view_name=self.resources_view_name
        )
        field = serializers.ListField(child=child)
        field.parent = self
        return field.to_representation(obj.resources.all())


class EnclosureSerializer(BaseSerializer, ResourcesMixin):
    class Meta:
        model = Enclosure
        nest_if_recursive = ('model',)

    resources = serializers.SerializerMethodField()

    def create(self, validated_data):
        if not validated_data['name']:
            validated_data['name'] = "{} Enclosure".format(
                Farm.get_solo().name
            )
        return super().create(validated_data)


class LayoutObjectSerializer(BaseSerializer, ResourcesMixin):
    def create(self, validated_data):
        instance = super().create(validated_data)
        if not instance.name:
            instance.name = "{} {} {}".format(
                Farm.get_solo().name, self.Meta.model.__name__, instance.pk
            )
            instance.save()
        return instance

    def validate(self, attrs):
        # Check which values are in attrs
        return attrs


#     def validate(self, attrs):
#         """ Ensure that this object fits inside it's parent """
#         total_length = (attrs['x'] or 0) + (attrs['length'] or 0)
#         parent_length = attrs['parent'].length
#         if parent_length and not total_length <= parent_length:
#             raise serializers.ValidationError(
#                 "Model is too long to fit in its parent"
#             )
#         total_width = (attrs['y'] or 0) + (attrs['width'] or 0)
#         parent_width = attrs['parent'].width
#         if parent_width and not total_width <= parent_width:
#             raise serializers.ValidationError(
#                 "Model is too wide to fit in its parent"
#             )
#         total_height = (attrs['z'] or 0) + (attrs['height'] or 0)
#         parent_height = attrs['parent'].height
#         if parent_height and not total_height <= parent_height:
#             raise serializers.ValidationError(
#                 "Model is too tall to fit in its parent"
#             )
#         return attrs

class TraySerializer(LayoutObjectSerializer):
    class Meta:
        model = Tray
        never_next = ('parent', )
        nest_if_recursive = ('model',)

    layout = serializers.HyperlinkedRelatedField(
        view_name='traylayout-detail', queryset=TrayLayout.objects.all(),
        write_only=True, required=False
    )
    resources = serializers.SerializerMethodField()

    def create_sites(self, instance, layout):
        for layout_site in layout.plant_sites.all():
            plant_site = PlantSite(
                parent=instance, row=layout_site.row, col=layout_site.col
            )
            plant_site.save()

    def clear_sites(self, instance):
        for plant_site in instance.plant_sites.all():
            plant_site.delete()

    def create(self, validated_data):
        layout = validated_data.pop('layout', None)
        if layout is not None:
            validated_data['num_rows'] = layout.num_rows
            validated_data['num_cols'] = layout.num_cols
        instance = super().create(validated_data)
        if layout is not None:
            self.create_sites(instance, layout)
        return instance

    def update(self, instance, validated_data):
        layout = validated_data.pop('layout', None)
        if layout is not None:
            validated_data['num_rows'] = layout.num_rows
            validated_data['num_cols'] = layout.num_cols
        instance = super().update(instance, validated_data)
        if layout is not None:
            self.clear_sites(instance)
            self.create_sites(instance, layout)
        return instance


class PlantSiteSerializer(BaseSerializer):
    class Meta:
        model = PlantSite


dynamic_serializers = {}
for entity_name, entity_model in dynamic_models.items():
    class Serializer(LayoutObjectSerializer, ResourcesMixin):
        class Meta:
            model = entity_model
            never_nest = ('parent',)
            nest_if_recursive = ('model',)

        resources = serializers.SerializerMethodField()
    dynamic_serializers[entity_name] = Serializer
