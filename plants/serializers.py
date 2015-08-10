from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ReadOnlyField, ValidationError
from cityfarm_api.serializers import BaseSerializer
from .models import (
    PlantModel, PlantType, Plant, SowEvent, TransferEvent, HarvestEvent,
    PlantComment
)


class PlantTypeSerializer(BaseSerializer):
    class Meta:
        model = PlantType

    def update(self, instance, validated_data):
        new_parent = validated_data['parent']
        if instance.is_above(new_parent):
            raise ValidationError(
                'That operation would create a cycle in the plant type graph, '
                'which is not allowed.'
            )
        return super().update(instance, validated_data)


class SowEventSerializer(BaseSerializer):
    class Meta:
        model = SowEvent


class TransferEventSerializer(BaseSerializer):
    class Meta:
        model = TransferEvent


class HarvestEventSerializer(BaseSerializer):
    class Meta:
        model = HarvestEvent


class PlantCommentSerializer(BaseSerializer):
    class Meta:
        model = PlantComment


class Plant(BaseSerializer):
    class Meta:
        model = Plant

    index = ReadOnlyField()
    sow_event = SowEventSerializer(read_only=True)
    transfer_events = TransferEventSerializer(many=True, read_only=True)
    harvest_event = HarvestEventSerializer(read_only=True)
    comments = PlantCommentSerializer(many=True, read_only=True)

    def create(self, validated_data):
        site = validated_data['site']
        if not site:
            raise ValidationError(
                'Plants cannot be created without being placed in a site.'
            )
        plant_type = validated_data['plant_type']
        plant_type.plant_count += 1
        validated_data['index'] = plant_type.plant_count
        instance = super().create(validated_data)
        sow_event = SowEvent(plant=instance, site=instance.site)
        sow_event.save()
        plant_type.save()
        return instance

    def update(self, instance, validated_data):
        try:
            instance.harvest_event
        except ObjectDoesNotExist:
            pass
        else:
            raise ValidationError(
                'Plants that have already been harvested cannot be edited.'
            )
        new_plant_type = validated_data.get('plant_type', instance.plant_type)
        if new_plant_type != instance.plant_type:
            raise ValidationError(
                'Changing the type of an existing plant is not allowed.'
            )
        new_site = validated_data.get('site', instance.site)
        if new_site != instance.site:
            if new_site:
                event = TransferEvent(
                    plant=instance, from_site =instance.site, to_site=new_site
                )
            else:
                event = HarvestEvent(
                    plant=instance
                )
            instance = super().update(instance, validated_data)
            event.save()
            return instance
        else:
            # Nothing changed, but let's update anyway just for fun
            return super().update(instance, validated_data)
