from django_filters import FilterSet, ChoiceFilter, CharFilter
from .models import City

class CityFilter(FilterSet):
    region = ChoiceFilter(
        field_name='region',
        label='Регион',
        choices=lambda: [(r, r) for r in City.objects.exclude(region__isnull=True).exclude(region__exact='').order_by('region').values_list('region', flat=True).distinct()],
        empty_label='Все регионы',
    )
    country = ChoiceFilter(
        field_name='country',
        label='Страна',
        choices=lambda: [(c, c) for c in City.objects.exclude(country__isnull=True).exclude(country__exact='').order_by('country').values_list('country', flat=True).distinct()],
        empty_label='Все страны',
    )

    class Meta:
        model = City
        fields = ['region', 'country'] 