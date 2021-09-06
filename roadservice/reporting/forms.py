from django import forms


class SingleRegionSelectForm(forms.Form):
    region = forms.ChoiceField(label='بخش')

    def __init__(self, *args, **kwargs):
        moderator = kwargs.pop('moderator')
        super().__init__(*args, **kwargs)
        regions = moderator.region.get_included_regions()
        region_choices = [(region.id, region.full_name) for region in regions]
        self.fields['region'].choices = region_choices
        self.fields['region'].widget.attrs['class'] = 'ui fluid right aligned search dropdown'


class TimeReportForm(SingleRegionSelectForm):
    start_date = forms.DateField(label='شروع بازه')
    end_date = forms.DateField(label='پایان بازه')
