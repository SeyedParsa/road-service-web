from django import forms

from core.models import Region, Country, Province, County


class TimeReportForm(forms.Form):
    regionInstances = ()
    regions = ()
    region = forms.ChoiceField(label='بخش', choices=regions)
    start_date = forms.DateField(label='شروع بازه', input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(label='پایان بازه', input_formats=['%Y-%m-%d'])

    def __init__(self, *args, **kwargs):
        countries = Country.objects.all()
        provinces = Province.objects.all()
        counties = County.objects.all()
        self.region_field = list((region.id-1, "کشور " + region.name) for region in countries)\
                            + list((region.id-1 + len(countries), "استان " + region.name) for region in provinces)\
                            + list((region.id-1 + len(countries) + len(provinces), "شهرستان " + region.name) for region in counties)
        self.regionInstances = list(countries) + list(provinces) + list(counties)
        super(TimeReportForm, self).__init__(*args, **kwargs)
        self.fields['region'].choices = self.region_field
