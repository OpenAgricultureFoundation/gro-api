import logging
from django.conf import settings
from django_cron import CronJobBase, Schedule
from .models import Farm

logger = logging.getLogger(__name__)


class UpdateFarmIp(CronJobBase):
    """
    This job calls the :meth:`farms.models.Farm.check_network` function every
    hour to re-calculate the :attr:`ip` attribute of the
    :class:`~farms.models.Farm` just in case it changed.
    """
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'farms.update_farm_ip'

    @staticmethod
    def do():
        logger.info('Running cron job `farms.cron.UpdateFarmIp`')
        if not settings.SERVER_TYPE == settings.LEAF:
            logger.error('This cron job should only be run on leaf servers')
        farm = Farm.get_solo()
        old_ip = farm.ip
        farm.check_network()
        if farm.ip != old_ip:
            logger.info('IP Changed from %s to %s', old_ip, farm.ip)
            farm.save()
