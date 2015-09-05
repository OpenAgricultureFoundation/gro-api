import django_filters

class HistoryFilterMixin(django_filters.FilterSet):
    min_time = django_filters.NumberFilter(name='timestamp', lookup_type='gte')
    max_time = django_filters.NumberFilter(name='timestamp', lookup_type='lte')
