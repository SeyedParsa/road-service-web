from django import forms

from accounts.models import Role
from core.models import Country, Province, County, Region


class AssignModeratorForm(forms.Form):
    region_instances = ()
    regions = ()
    user = forms.DecimalField(label='شناسه کاربر')
    region = forms.ChoiceField(label='بخش', choices=regions)

    def __init__(self, *args, **kwargs):
        provinces = Province.objects.all()
        counties = County.objects.all()
        self.region_field = list((region.id - 1, "استان " + region.name) for region in provinces) \
                            + list((region.id - 1 + len(provinces), "شهرستان " + region.name) for region in counties)
        self.region_instances = list(provinces) + list(counties)
        super().__init__(*args, **kwargs)
        self.fields['region'].choices = self.region_field


class RegionMultipleFilterForm(forms.Form):
    regions = forms.MultipleChoiceField(label='بخش')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if user.role.type == Role.Type.COUNTY_EXPERT:
            regions = []
        else:
            regions = user.role.get_concrete().region.get_including_regions()
        region_choices = [(region.id,
                           ('استان %s' if region.type == Region.Type.PROVINCE else 'شهرستان %s') % region.name)
                          for region in regions if region.type != Region.Type.COUNTRY]
        self.fields['regions'].choices = region_choices
        self.fields['regions'].widget.attrs['class'] = 'ui fluid right aligned search dropdown'


class SingleStringForm(forms.Form):
    name = forms.CharField(label='نام')
