from django import forms

from core.models import Region, Country, Province, County


class SingleRegionSelectForm(forms.Form):
    region = forms.ChoiceField(label='بخش')

    def __init__(self, *args, **kwargs):
        moderator = kwargs.pop('moderator')
        super().__init__(*args, **kwargs)
        regions = moderator.region.get_included_regions()
        region_choices = [(region.id,
                           ('استان %s' if region.type == Region.Type.PROVINCE else
                            'شهرستان %s' if region.type == Region.Type.COUNTY else 'کشور %s') % region.name)
                          for region in regions]
        self.fields['region'].choices = region_choices


class TimeReportForm(SingleRegionSelectForm):
    start_date = forms.DateField(label='شروع بازه', input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(label='پایان بازه', input_formats=['%Y-%m-%d'])
