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
        """ Ensure that this object fits inside it's parent """
        total_length = attrs['x'] + attrs['length']
        parent_length = attrs['parent'].length
        if parent_length and not total_length <= parent_length:
            raise serializers.ValidationError(
                "Model is too long to fit in its parent"
            )
        total_width = attrs['y'] + attrs['width']
        parent_width = attrs['parent'].width
        if parent_width and not total_width <= parent_width:
            raise serializers.ValidationError(
                "Model is too wide to fit in its parent"
            )
        total_height = attrs['z'] + attrs['height']
        parent_height = attrs['parent'].height
        if parent_height and not total_height <= parent_height:
            raise serializers.ValidationError(
                "Model is too tall to fit in its parent"
            )
        return attrs

    def ranges_overlap(range1, range2):
        return (range1[1] > range2[0]) and (range1[0] < range2[1])

    def check_for_overlap(self, attrs, others):
        this_x_range = (attrs['x'], attrs['x'] + attrs['length'])
        this_y_range = (attrs['y'], attrs['y'] + attrs['width'])
        this_z_range = (attrs['z'], attrs['z'] + attrs['height'])
        for other in others:
            other_x_range = (other.x, other.x + other.length)
            other_y_range = (other.y, other.y + other.width)
            other_z_range = (other.z, other.z + other.height)
            if self.ranges_overlap(other_x_range, this_x_range) \
                    and self.ranges_overlap(other_y_range, this_y_range) \
                    and self.ranges_overlap(other_z_range, this_z_range):
                raise ValidationError(
                    'Entity cannot overlap with another entity of the same '
                    'type'
                )

    def create(self, validated_data):
        parent = validated_data['parent']
        others = parent.children
        self.check_for_overlap(validated_data, others)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        parent = validated_data['parent']
        others = (
            child for child in instance.children if child.pk != instance.pk
        )
        self.check_for_overlap(validated_data, others)
        return super().update(instance, validated_data)


class TraySerializer(LayoutObjectSerializer):
    class Meta:
        model = Tray

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
