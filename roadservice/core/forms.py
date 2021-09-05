from django import forms

from accounts.models import Role, User
from core.exceptions import ResourceNotFoundError
from core.models import Region, Speciality


class AssignExpertForm(forms.Form):
    phone_number = forms.CharField(max_length=30, label="شماره تماس")


class AssignModeratorForm(forms.Form):
    phone_number = forms.CharField(max_length=30, label="شماره تماس")
    region = forms.ChoiceField(label='بخش')

    def __init__(self, *args, **kwargs):
        moderator = kwargs.pop('moderator')
        super().__init__(*args, **kwargs)
        regions = moderator.region.sub_regions.all()
        region_choices = [(region.id,
                           ('استان %s' if region.type == Region.Type.PROVINCE else 'شهرستان %s') % region.name)
                          for region in regions]
        self.fields['region'].choices = region_choices
        self.fields['region'].widget.attrs['class'] = 'ui fluid right aligned search dropdown'


class RegionMultipleFilterForm(forms.Form):
    regions = forms.MultipleChoiceField(label='بخش')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if user.role.type == Role.Type.COUNTY_EXPERT:
            regions = []
        else:
            regions = user.role.get_concrete().region.get_included_regions()
        region_choices = [(region.id,
                           ('استان %s' if region.type == Region.Type.PROVINCE else 'شهرستان %s') % region.name)
                          for region in regions if region.type != Region.Type.COUNTRY]
        self.fields['regions'].choices = region_choices
        self.fields['regions'].widget.attrs['class'] = 'ui fluid right aligned search dropdown'


class SingleStringForm(forms.Form):
    name = forms.CharField(label='نام')


class TeamCustomForm:
    def __init__(self, post):
        speciality_id = post.get('spaciality')
        try:
            self.speciality = Speciality.objects.get(id=speciality_id)
        except Speciality.DoesNotExist:
            raise ResourceNotFoundError()
        self.users = []
        for name in post:
            if name[:5] == 'phone':
                input_id = name[5:]
                phone = post.get(name)
                if phone and 'remove%s' % input_id not in post:
                    try:
                        user = User.objects.get(phone_number=phone)
                        self.users.append(user)
                    except User.DoesNotExist:
                        raise ResourceNotFoundError()
