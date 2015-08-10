import time
import logging
from rest_framework.exceptions import APIException
from cityfarm_api.serializers import BaseSerializer
from resources.models import ResourceProperty
from .models import RecipeRun, SetPoint

logger = logging.getLogger(__name__)


class InvalidTimeString(Exception):
    pass


class RecipeRunSerializer(BaseSerializer):
    class Meta:
        model = RecipeRun

    def parse_time_string(self, time_string):
        time_args = time_string.split(b':')
        if len(time_args) != 4:
            raise InvalidTimeString()
        time_args = [int(arg) for arg in time_args]
        return time_args.pop() + 60*time_args.pop() + 60*60*time_args.pop() + \
                60*60*24*time_args.pop()

    def create(self, validated_data):
        recipe = validated_data['recipe']
        tray = validated_data['tray']
        start_timestamp = validated_data.get('start_timestamp', time.time())
        # We have to create this object now so that set points we create during
        # parsing can reference it. Thus, we have to save a fake value here and
        # overwrite it later
        validated_data['end_timestamp'] = 0
        instance = super().create(validated_data)
        set_points = []
        for line in recipe.file:
            line = line.strip()
            if not line:
                continue
            args = line.split(b' ')
            if len(args) != 3:
                logger.warning(
                    'Encountered invalid recipe command "%s" in recipe "%s"',
                    line, recipe.name
                )
                continue
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
            command = args.pop(0)
            command_type = command[0:1]
            if command_type == b'S':
                property = ResourceProperty.objects.get_by_natural_key(
                        command[1:2], command[2:4]
                )
                value = float(args.pop(0))
                set_point = SetPoint(
                    tray=tray, property=property, timestamp=command_timestamp,
                    value=value, recipe_run=instance
                )
                set_point.save()
            else:
                logger.warning(
                    'Encountered invalid command type "%s" in recipe "%s"',
                    command_type, recipe.name
                )
                continue
            assert not args
        instance.end_timestamp = command_timestamp
        instance.save()
        return instance

    def update(self, instance, validated_data):
        raise APIException(
            'Recipe runs can only be created and deleted. To change what the '
            'recipe will do, either edit the set points manually or delete '
            'this run and start a new one.'
        )
