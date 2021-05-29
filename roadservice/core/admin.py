from django.contrib import admin

from core.models import Province, County, Speciality, Machinery, ServiceTeam, Citizen, Serviceman, Issue, \
    SpecialityRequirement, MachineryRequirement, MissionType, Mission, CountyExpert, Country, CountryModerator, \
    ProvinceModerator, CountyModerator, MachineryType

admin.site.register(Country)
admin.site.register(Province)
admin.site.register(County)
admin.site.register(CountryModerator)
admin.site.register(ProvinceModerator)
admin.site.register(CountyModerator)
admin.site.register(Speciality)
admin.site.register(MachineryType)
admin.site.register(Machinery)
admin.site.register(ServiceTeam)
admin.site.register(Serviceman)
admin.site.register(Citizen)
admin.site.register(Issue)
admin.site.register(SpecialityRequirement)
admin.site.register(MachineryRequirement)
admin.site.register(MissionType)
admin.site.register(Mission)
admin.site.register(CountyExpert)
