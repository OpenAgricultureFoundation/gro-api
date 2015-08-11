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

    start_timestamp = IntegerField(allow_null=True)

    @cached_property
    def current_time(self):
        return time.time()

    def parse_time_string(self, time_string):
        time_args = time_string.split(b':')
        if len(time_args) != 4:
            raise InvalidTimeString()
        time_args = [int(arg) for arg in time_args]
        return time_args.pop() + 60*time_args.pop() + 60*60*time_args.pop() + \
                60*60*24*time_args.pop()

    def validate_start_timestamp(self, val):
        return val or self.current_time

    def create(self, validated_data):
        recipe = validated_data['recipe']
        tray = validated_data['tray']
        start_timestamp = validated_data.get(
            'start_timestamp', self.current_time
        )
        if start_timestamp < self.current_time:
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
        set_points = [SetPoint(
            tray=tray, property=property, timestamp=start_timestamp-1,
            value=None
        ) for property in ResourceProperty.objects.all()]
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
                instance.delete()
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
        validated_data['end_timestamp'] = command_timestamp
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
        raise APIException(
            'Recipe runs can only be created and deleted. To change what the '
            'recipe will do, either edit the set points manually or delete '
            'this run and start a new one.'
        )
