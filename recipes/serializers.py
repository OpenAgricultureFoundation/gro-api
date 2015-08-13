import time
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.serializers import IntegerField
from cityfarm_api.serializers import BaseSerializer
from resources.models import ResourceProperty
from .models import Recipe, RecipeRun, SetPoint

logger = logging.getLogger(__name__)


class RecipeSerializer(BaseSerializer):
    class Meta:
        model = Recipe

    def validate_plant_types(self, value):
        for first_type in value:
            for second_type in value:
                if first_type is second_type:
                    continue
                if first_type.is_above(second_type):
                    raise ValidationError(
                        'Supplied set of plant types is redundant. Plant type '
                        '"{}" is contained in plant type "{}"'.format(
                            second_type.common_name, first_type.common_name
                        )
                    )
        return value


class InvalidTimeString(Exception):
    pass


class RecipeRunSerializer(BaseSerializer):
    class Meta:
        model = RecipeRun

    start_timestamp = IntegerField(required=False, allow_null=True)
    end_timestamp = IntegerField(required=False, allow_null=True)

    def parse_time_string(self, time_string):
        time_args = time_string.split(b':')
        if len(time_args) != 4:
            raise InvalidTimeString()
        try:
            time_args = [int(arg) for arg in time_args]
        except ValueError:
            raise InvalidTimeString()
        return time_args.pop() + 60*time_args.pop() + 60*60*time_args.pop() + \
                60*60*24*time_args.pop()

    def create(self, validated_data):
        current_time = time.time()
        recipe = validated_data['recipe']
        tray = validated_data['tray']
        start_timestamp = validated_data['start_timestamp'] or current_time
        if start_timestamp < current_time:
            raise ValidationError(
                'Start timestamp must be a time in the future.'
            )
        qs = RecipeRun.objects.filter(
            tray=tray, start_timestamp__lt=start_timestamp,
            end_timestamp__gt=start_timestamp
        )
        if qs.count():
            raise ValidationError(
                'The proposed recipe run overlaps with an existing recipe run.'
            )
        try:
            next_start_timestamp = RecipeRun.objects.filter(
                tray=tray, start_timestamp__gte=start_timestamp
            ).earliest().start_timestamp
        except ObjectDoesNotExist:
            next_start_timestamp = float("inf")
        set_points = []
        end_timestamp = None
        for line in recipe.file:
            line = line.strip()
            if not line:
                continue
            args = line.split(b' ')
            time_string = args.pop(0)
            try:
                timedelta = self.parse_time_string(time_string)
            except InvalidTimeString:
                logger.warning(
                    'Encountered invalid time string "%s" in recipe "%s"',
                    time_string, recipe.name
                )
                continue
            command_timestamp = start_timestamp + timedelta
            if command_timestamp >= next_start_timestamp:
                raise ValidationError(
                    'The proposed recipe run overlaps with an existing recipe '
                    'run.'
                )
            command = args.pop(0)
            command_type = command[0:1]
            if command_type == b'S':
                property = ResourceProperty.objects.get_by_natural_key(
                        command[1:2], command[2:4]
                )
                value = float(args.pop(0))
                set_point = SetPoint(
                    tray=tray, property=property, timestamp=command_timestamp,
                    value=value
                )
                set_points.append(set_point)
            elif command_type == b'G':
                if command == b'GTFO':
                    end_timestamp = command_timestamp
                    set_points.extend([
                        SetPoint(
                            tray=tray, property=property,
                            timestamp=end_timestamp, value=None
                        ) for property in ResourceProperty.objects.all()
                    ])
                    break
            else:
                logger.warning(
                    'Encountered invalid command type "%s" in recipe "%s"',
                    command_type, recipe.name
                )
                continue
            if args:
                logger.warning(
                    'Recipe line "%s" contained extra arguments'.format(line)
                )
        if not end_timestamp:
            raise ValidationError(
                'Recipe file did not include an end timestamp.'
            )
        validated_data['start_timestamp'] = start_timestamp
        validated_data['end_timestamp'] = end_timestamp
        instance = super().create(validated_data)
        try:
            for set_point in set_points:
                set_point.recipe_run = instance
            SetPoint.objects.bulk_create(set_points)
        except:
            instance.delete()
            raise
        return instance

    def update(self, instance, validated_data):
        start_timestamp = validated_data.get(
            'start_timestamp', instance.start_timestamp
        )
        if start_timestamp != instance.start_timestamp:
            raise ValidationError(
                'Changing the start time of an existing recipe run is not '
                'allowed.'
            )
        recipe = validated_data.get('recipe', instance.recipe)
        if recipe != instance.recipe:
            raise ValidationError(
                'Changing the recipe of a recipe run is not allowed. To '
                'switch recipes, stop the current one and then start the '
                'desired one.'
            )
        tray = validated_data.get('tray', instance.tray)
        if tray != instance.tray:
            raise ValidationError(
                'Changing the tray of a recipe run is not allowed.'
            )
        end_timestamp = validated_data.get(
            'end_timestamp', instance.end_timestamp
        )
        if end_timestamp > instance.end_timestamp:
            raise ValidationError(
                'Extending a recipe run is not allowed.'
            )
        if end_timestamp < instance.end_timestamp:
            SetPoint.objects.filter(
                recipe_run=instance,
                timestamp__gt=validated_data['end_timestamp']
            ).delete()
            SetPoint.objects.bulk_create([
                SetPoint(
                    tray=tray, property=property, timestamp=end_timestamp,
                    value=None, recipe_run=instance
                ) for property in ResourceProperty.objects.all()
            ])
        return super().update(instance, validated_data)
