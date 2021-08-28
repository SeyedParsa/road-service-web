from django import forms

from core.models import Country, Province, County


class AssignModeratorForm(forms.Form):
    region_instances = ()
    regions = ()
    user = forms.DecimalField(label='شناسه کاربر')
    region = forms.ChoiceField(label='بخش', choices=regions)

    def __init__(self, *args, **kwargs):
        provinces = Province.objects.all()
        counties = County.objects.all()
        self.region_field = list((region.id-1, "استان " + region.name) for region in provinces)\
                          + list((region.id-1 + len(provinces), "شهرستان " + region.name) for region in counties)
        self.region_instances = list(provinces) + list(counties)
        super().__init__(*args, **kwargs)
        self.fields['region'].choices = self.region_field


class RegionMultipleFilterForm(forms.Form):
    regions = forms.MultipleChoiceField(label='بخش')

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: filter regions by user @Kiarash
        provinces = Province.objects.all()
        counties = County.objects.all()
        region_choices = list((region.id, "استان " + region.name) for region in provinces) \
                              + list((region.id, "شهرستان " + region.name) for region in counties)
        self.fields['regions'].choices = region_choices
        self.fields['regions'].widget.attrs['class'] = 'ui fluid right aligned search dropdown'
