from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from khayyam import *

from accounts.models import User
from core.forms import AssignModeratorForm, RegionMultipleFilterForm, SingleStringForm
from core.models import Region, CountryModerator, ProvinceModerator, Issue, \
    MissionType, Speciality, MachineryType, Machinery


class Home(View):
    def get(self, request, *args, **kwargs):
        # TODO: if not logged in, redirect to login page
        issues = Issue.objects.all()
        # TODO: filter issues by user @Kiarash
        context = {'issues': issues}
        return render(request=request,
                      template_name='core/dashboard.html',
                      context=context)


class IssueCard(View):
    def get(self, request, *args, **kwargs):
        issue_id = kwargs['issue_id']
        context = {'id': issue_id}
        print('ISSUE ID = ', issue_id)
        issue = Issue.objects.get(id=issue_id)
        context['issue'] = issue
        context['persian_datetime'] = JalaliDatetime(issue.created_at).strftime("%C")
        return render(request=request,
                      template_name='core/issuecard.html', context=context)

    def post(self, request, *args, **kwargs):
        issue_id = kwargs['issue_id']
        context = {'card': issue_id}
        return render(request=request,
                      template_name='core/issuecard.html', context=context)


class TeamDetails(View):
    def get(self, request, *args, **kwargs):
        team_id = kwargs['team_id']
        context = {'team': team_id}
        return render(request=request,
                      template_name='core/teamdetails.html', context=context)

    def post(self, request, *args, **kwargs):
        team_id = kwargs['team_id']
        context = {'team': team_id}
        return render(request=request,
                      template_name='core/teamdetails.html', context=context)


class ChangeTeam(View):
    def get(self, request, *args, **kwargs):
        team_id = kwargs['team_id']
        context = {'team': team_id}
        return render(request=request,
                      template_name='core/changeteam.html', context=context)

    def post(self, request, *args, **kwargs):
        team_id = kwargs['team_id']
        context = {'team': team_id}
        return render(request=request,
                      template_name='core/changeteam.html', context=context)


class AddSpeciality(View):
    def get(self, request, *args, **kwargs):
        form = SingleStringForm()
        context = {'form': form}
        return render(request=request,
                      template_name='core/addspeciality.html', context=context)

    def post(self, request, *args, **kwargs):
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            print('New Speciality Name:', name)
            # TODO: Create new Speciality
        context = {'form': form}
        messages.add_message(request, messages.INFO, 'نوع تخصص جدید اضافه شد!')
        return HttpResponseRedirect('/resources/')


class AddMissionType(View):
    def get(self, request, *args, **kwargs):
        form = SingleStringForm()
        context = {'form': form}
        return render(request=request,
                      template_name='core/addmissiontype.html', context=context)

    def post(self, request, *args, **kwargs):
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            print('New MissionType Name:', name)
            # TODO: Create new missionType
        context = {'form': form}
        messages.add_message(request, messages.INFO, 'نوع ماموریت جدید اضافه شد!')
        return HttpResponseRedirect('/resources/')


class ChangeMissionType(View):
    def get(self, request, *args, **kwargs):
        missiontype_id = kwargs['missiontype_id']
        form = SingleStringForm()
        missiontype = MissionType.objects.get(id=missiontype_id)
        context = {'form': form, 'missiontype': missiontype}
        return render(request=request,
                      template_name='core/addmissiontype.html', context=context)

    def post(self, request, *args, **kwargs):
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            print('New MissionType Name:', name)
            # TODO: Create new missionType
        context = {'form': form}
        messages.add_message(request, messages.INFO, 'نوع ماموریت جدید اضافه شد!')
        return HttpResponseRedirect('/resources/')


class ChangeMissionType(View):
    def get(self, request, *args, **kwargs):
        missiontype_id = kwargs['missiontype_id']
        form = SingleStringForm()
        missiontype = MissionType.objects.get(id=missiontype_id)
        context = {'form': form, 'missiontype': missiontype}
        return render(request=request,
                      template_name='core/changemissiontype.html', context=context)

    def post(self, request, *args, **kwargs):
        missiontype_id = kwargs['missiontype_id']
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            print('Modified Name:', name)
            # TODO: Modify speciality name
        messages.add_message(request, messages.INFO, 'نوع ماموریت بروز شد!')
        return HttpResponseRedirect('/resources/')


class ChangeSpeciality(View):
    def get(self, request, *args, **kwargs):
        speciality_id = kwargs['speciality_id']
        form = SingleStringForm()
        speciality = Speciality.objects.get(id=speciality_id)
        context = {'form': form, 'speciality': speciality}
        return render(request=request,
                      template_name='core/changespeciality.html', context=context)

    def post(self, request, *args, **kwargs):
        speciality_id = kwargs['speciality_id']
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            print('Modified Name:', name)
            # TODO: Modify speciality name
        messages.add_message(request, messages.INFO, 'نوع تخصص بروز شد!')
        return HttpResponseRedirect('/resources/')


class AssignModerator(View):
    def get(self, request, *args, **kwargs):
        assign_moderator_form = AssignModeratorForm()
        return render(request=request,
                      template_name='core/assignmoderator.html',
                      context={'form': assign_moderator_form})

    def post(self, request, *args, **kwargs):
        form = AssignModeratorForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            region_id = int(form.cleaned_data['region'])
            region = form.region_instances[region_id]
            user_id = form.cleaned_data['user']
            user = User.objects.get(id=user_id)
            if region.type == Region.Type.PROVINCE:
                CountryModerator.assign_province_moderator(user, region)
            else:
                ProvinceModerator.assign_county_moderator(user, region)
            messages.add_message(request, messages.INFO, 'دسترسی داده شد!')
        else:
            print('invalid form!')
        messages.add_message(request, messages.INFO, 'دسترسی داده شد!')
        return render(request=request,
                      template_name='core/assignmoderator.html',
                      context=context)


class Resources(View):
    def get(self, request, *args, **kwargs):
        context = {'filter_form': RegionMultipleFilterForm(),
                   'machineries': Machinery.objects.all(),
                   'mission_types': MissionType.objects.all(),
                   'specialities': Speciality.objects.all()}
        # TODO: filter objects from above lines by user accessible objects @Kiarash
        return render(request=request,
                      template_name='core/resources.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        form = RegionMultipleFilterForm(request.POST)
        context = {'filter_form': form,
                   'machineries': Machinery.objects.all(),
                   'mission_types': MissionType.objects.all(),
                   'specialities': Speciality.objects.all()}
        # TODO: filter objects from above lines by user accessible objects @Kiarash
        if form.is_valid():
            messages.add_message(request, messages.INFO, 'جدول بروز شد!')
            regions = form.cleaned_data.get('regions')
            print(regions)
            # TODO: Do the filtering! @Kiarash
            # TODO: lab lab lab @KIARASH!
        else:
            messages.add_message(request, messages.ERROR, 'فرم نامعتبر است!')
        return render(request=request,
                      template_name='core/resources.html',
                      context=context)


class AddMachinery(View):
    def get(self, request, *args, **kwargs):
        machinery_id = kwargs['machinery_id']
        machinery = MachineryType.objects.get(id=machinery_id)
        context = {'machinery': machinery_id}
        # TODO: Add a new machinery!
        messages.add_message(request, messages.INFO, str('یک ' + machinery.name + ' اضافه شد!'))
        return HttpResponseRedirect('/resources/')


class RemoveMachinery(View):
    def get(self, request, *args, **kwargs):
        machinery_id = kwargs['machinery_id']
        machinery = MachineryType.objects.get(id=machinery_id)
        context = {'machinery': machinery_id}
        # TODO: remove a single machinery!
        messages.add_message(request, messages.INFO, str('یک ' + machinery.name + ' حذف شد!'))
        return HttpResponseRedirect('/resources/')


class RemoveMissionType(View):
    def get(self, request, *args, **kwargs):
        missiontype_id = kwargs['missiontype_id']
        context = {'missiontype_id': missiontype_id}
        # TODO: remove missiontype!
        messages.add_message(request, messages.INFO, 'نوع ماموریت حذف شد!')
        return HttpResponseRedirect('/resources/')


class RemoveSpeciality(View):
    def get(self, request, *args, **kwargs):
        speciality_id = kwargs['speciality_id']
        context = {'speciality_id': speciality_id}
        # TODO: remove speciality!
        messages.add_message(request, messages.INFO, 'نوع تخصص حذف شد!')
        return HttpResponseRedirect('/resources/')


class RemoveTeam(View):
    def get(self, request, *args, **kwargs):
        team_id = kwargs['team_id']
        context = {'team_id': team_id}
        # TODO: remove team!
        messages.add_message(request, messages.INFO, 'تیم  حذف شد!')
        return HttpResponseRedirect('/resources/')
