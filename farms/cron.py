from django_cron import CronJobBase, Schedule

class UpdateFarmIp(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'farms.update_farm_ip'
    def do(self):
        farm = Farm.get_solo()
        old_ip = farm.ip
        farm.check_network()
        if farm.ip != old_ip:
            farm.save()
