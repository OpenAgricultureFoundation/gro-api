from django.db import transaction
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_detail_view_name
from ..core.const import ENCLOSURE, TRAY
from ..core.serializers import BaseSerializer
from ..farms.models import Farm
from ..resources.models import Resource
from .models import (
    LayoutModel3D, TrayLayout, PlantSiteLayout, Enclosure, Tray,
    generated_models, PlantSite
)


class LayoutModel3DSerializer(BaseSerializer):
    class Meta:
        model = LayoutModel3D


class TrayLayoutSerializer(BaseSerializer):
    class Meta:
        model = TrayLayout


class PlantSiteLayoutSerializer(BaseSerializer):
    class Meta:
        model = PlantSiteLayout

    def validate_parent(self, parent):
        if parent.is_locked:
            raise ValidationError(
                'The tray layout containing this plant site is locked, so '
                'this site cannot be modified.'
            )

    def many_create(self, validated_data):
        parent_layout = validated_data[0].parent
        for site in validated_data:
            if site.parent != parent_layout:
                raise ValidationError(
                    'Creating plant sites for multiple tray layouts in a '
                    'single request is not allowed'
                )
        sites = super().many_create(validated_data)
        # We we create the plant sites in bulk, we have to send 2 post_save
        # signals to make sure that the dimensions of the parent TrayLayout
        # remain consistent: 1 for the site with the highest row, and 1 for the
        # site with the highest column
        max_row_site = sites[0]
        max_col_site = sites[1]
        for site in sites:
            if site.row > max_row_site.row:
                max_row_size = site
            if site.col > max_col_site.col:
                max_col_site = site
        post_save.send(PlantSiteLayout, instance=max_row_site)
        post_save.send(PlantSiteLayout, instance=max_col_site)
        return sites


class LayoutObjectSerializer(BaseSerializer):
    def validate(self, attrs):
        """ Ensure that this object fits inside its parent """
        if attrs['parent'] is None:
            if attrs['type'] == ENCLOSURE:
                return attrs
            else:
                raise serializers.ValidationError(
                    'All layout objects (except the Enclosure) must have '
                    'parents'
                )
        total_length = attrs['x'] + attrs['outer_length']
        parent_length = attrs['parent'].outer_length
        if total_length > parent_length:
            raise serializers.ValidationError(
                "Model is too long to fit in its parent"
            )
        total_width = attrs['y'] + attrs['outer_width']
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
        if parent is not None:
            others = parent.children.all()
            self.check_for_overlap(validated_data, others)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        parent = validated_data['parent']
        if parent is not None:
            others = (
                child for child in parent.children.all()
                if child.pk != instance.pk
            )
            self.check_for_overlap(validated_data, others)
        return super().update(instance, validated_data)


class EnclosureSerializer(LayoutObjectSerializer):
    class Meta:
        model = Enclosure


class TraySerializer(LayoutObjectSerializer):
    class Meta:
        model = Tray

    layout = serializers.HyperlinkedRelatedField(
        write_only=True, queryset=TrayLayout.objects.all(),
        view_name='traylayout-detail'
    )
    num_rows = serializers.SerializerMethodField()
    num_cols = serializers.SerializerMethodField()

    def get_num_rows(self, obj):
        return obj.extra_info.num_rows

    def get_num_cols(self, obj):
        return obj.extra_info.num_cols

    def create_sites(self, instance, old_num_rows, old_num_cols, new_num_rows,
            new_num_cols):
        sites = []
        for r in range(new_num_rows):
            for c in range(num_num_cols):
                if r < old_num_rows and c < old_num_cols:
                    continue
                sites.append(PlantSite(
                    parent=instance, row=r, col=c, is_active=False
                ))
        PlantSite.objects.bulk_create(sites)

    def apply_layout(self, instance, layout):
        with transaction.atomic():
            instance.plant_sites.all().update(is_active=False)
            for layout_site in layout.plant_sites.all():
                instance.plant_sites.objects.get(
                    row=layout_site.row, col=layout_site.col
                ).update(is_active=True)

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


generated_serializers = {}
for entity_name, entity_model in generated_models.items():
    class Serializer(LayoutObjectSerializer):
        class Meta:
            model = entity_model
    generated_serializers[entity_name] = Serializer


class PlantSiteSerializer(BaseSerializer):
    class Meta:
        model = PlantSite
