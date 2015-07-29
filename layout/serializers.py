"""
This module creates serializers for some of the models defines in the
layout.models module
"""
from rest_framework import serializers
from cityfarm_api.serializers import BaseSerializer
from .models import (
    Enclosure, Tray, PlantSite, dynamic_models, TrayLayout, PlantSiteLayout
)


class TrayLayoutSerializer(BaseSerializer):
    class Meta:
        model = TrayLayout
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
        for row in range(instance.num_rows):
            for col in range(instance.num_cols):
                if should_create(row, col):
                    site = PlantSiteLayout(parent=instance, row=row, col=col)
                    site.save()

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


class EnclosureSerializer(BaseSerializer):
    class Meta:
        model = Enclosure
        nest_if_recursive = ('model',)


class LayoutObjectSerializer(BaseSerializer):
    """ A Serializer for subclasses of LayoutObject """
    def validate_location(self, attrs):
        """ Ensure that this object fits inside it's parent """
        total_length = (attrs['x'] or 0) + (attrs['length'] or 0)
        parent_length = attrs['parent'].length
        if parent_length and not total_length <= parent_length:
            raise serializers.ValidationError(
                "Model is too long to fit in its parent"
            )
        total_width = (attrs['y'] or 0) + (attrs['width'] or 0)
        parent_width = attrs['parent'].width
        if parent_width and not total_width <= parent_width:
            raise serializers.ValidationError(
                "Model is too wide to fit in its parent"
            )
        total_height = (attrs['z'] or 0) + (attrs['height'] or 0)
        parent_height = attrs['parent'].height
        if parent_height and not total_height <= parent_height:
            raise serializers.ValidationError(
                "Model is too tall to fit in its parent"
            )
        return attrs

    def validate(self, attrs):
        return self.validate_location(attrs)


class TraySerializer(LayoutObjectSerializer):
    class Meta:
        model = Tray
        nest_if_recursive = ('model',)

    layout = serializers.HyperlinkedRelatedField(
        view_name='traylayout-detail', queryset=TrayLayout.objects.all(),
        write_only=True, required=False
    )

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
        layout = validated_data.pop('layout')
        if layout is not None:
            validated_data['num_rows'] = layout.num_rows
            validated_data['num_cols'] = layout.num_cols
        instance = super().create(validated_data)
        if layout is not None:
            self.create_sites(instance, layout)
        return instance

    def update(self, instance, validated_data):
        if 'layout' in validated_data:
            layout = validated_data.pop('layout')
            self.clear_sites(instance)
            self.create_sites(instance, layout)
        return super().update(instance, validated_data)

for entity_name, entity_model in dynamic_models.items():
    class Serializer(LayoutObjectSerializer):
        class Meta:
            model = entity_model
            never_nest = ('parent',)
            nest_if_recursive = ('model',)
