from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from khayyam import *

from accounts.models import User, Role
from core.exceptions import DuplicatedInfoError, BusyResourceError
from core.forms import AssignModeratorForm, RegionMultipleFilterForm, SingleStringForm
from core.models import Region, CountryModerator, ProvinceModerator, Issue, MissionType, Speciality, MachineryType, \
    Machinery


class Home(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTY_EXPERT, Role.Type.COUNTRY_MODERATOR,
                                            Role.Type.PROVINCE_MODERATOR, Role.Type.COUNTY_MODERATOR]

    def get(self, request, *args, **kwargs):
        if request.user.role.type == Role.Type.COUNTY_EXPERT:
            issues = request.user.role.get_concrete().get_issues()
        else:
            regions = [request.user.role.get_concrete().region]
            issues = request.user.role.get_concrete().get_issues(regions)
        context = {'issues': issues}
        return render(request=request,
                      template_name='core/dashboard.html',
                      context=context)


class IssueCard(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTY_EXPERT, Role.Type.COUNTRY_MODERATOR,
                                            Role.Type.PROVINCE_MODERATOR, Role.Type.COUNTY_MODERATOR]

    def get(self, request, issue_id):
        issue = Issue.objects.get(id=issue_id)
        if not request.user.role.get_concrete().can_view_issue(issue):
            return HttpResponseForbidden()
        context = {
            'id': issue_id,
            'issue': issue,
            'persian_datetime': JalaliDatetime(issue.created_at).strftime("%C")
        }
        return render(request=request,
                      template_name='core/issuecard.html', context=context)


class AssignModerator(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.PROVINCE_MODERATOR, Role.Type.COUNTY_MODERATOR]

    def get(self, request, *args, **kwargs):
        assign_moderator_form = AssignModeratorForm()
        return render(request=request,
                      template_name='core/assignmoderator.html',
                      context={'form': assign_moderator_form})

    def post(self, request, *args, **kwargs):
        # TODO: just wrong! :D
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
            messages.add_message(request, messages.ERROR, 'فرم نامعتبر است!')
            print('invalid form!')
        return render(request=request,
                      template_name='core/assignmoderator.html',
                      context=context)


class Resources(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTY_EXPERT, Role.Type.COUNTRY_MODERATOR,
                                            Role.Type.PROVINCE_MODERATOR, Role.Type.COUNTY_MODERATOR]

    def process(self, request, form, regions=None):
        if request.user.role.type == Role.Type.COUNTY_EXPERT:
            teams = request.user.role.get_concrete().get_teams()
            machineries = request.user.role.get_concrete().get_machineries()
        else:
            if not regions:
                regions = [request.user.role.get_concrete().region]
            teams = request.user.role.get_concrete().get_teams(regions)
            machineries = request.user.role.get_concrete().get_machineries(regions)
        machinery_count = {machinery_type: {'total': 0, 'available': 0} for machinery_type in
                           MachineryType.objects.all()}
        for machinery in machineries:
            machinery_count[machinery.type]['total'] += machinery.total_count
            machinery_count[machinery.type]['available'] += machinery.available_count
        mission_types = MissionType.objects.all()
        specialities = Speciality.objects.all()
        context = {'filter_form': form,
                   'teams': teams,
                   # TODO @Mahdi: User machinery_count instead of machineries
                   'machineries': Machinery.objects.all(),
                   'mission_types': mission_types,
                   'specialities': specialities}
        return render(request=request,
                      template_name='core/resources.html',
                      context=context)

    def get(self, request, *args, **kwargs):
        form = RegionMultipleFilterForm(user=self.request.user)
        return self.process(request, form)

    def post(self, request, *args, **kwargs):
        form = RegionMultipleFilterForm(request.POST, user=self.request.user)
        regions = None
        if form.is_valid():
            messages.add_message(request, messages.INFO, 'جدول بروز شد!')
            region_ids = form.cleaned_data.get('regions')
            regions = [Region.objects.get(id=region_id) for region_id in region_ids]
        else:
            messages.add_message(request, messages.ERROR, 'فرم نامعتبر است!')
        return self.process(request, form, regions)


# TODO: add team


class ChangeTeam(View):
    # TODO
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


class RemoveTeam(View):
    def get(self, request, *args, **kwargs):
        team_id = kwargs['team_id']
        context = {'team_id': team_id}
        # TODO: remove team!
        messages.add_message(request, messages.INFO, 'تیم  حذف شد!')
        return HttpResponseRedirect('/resources/')


class AddMachinery(View):
    def get(self, request, machinery_id):
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


class AddMissionType(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_EXPERT

    def get(self, request, *args, **kwargs):
        form = SingleStringForm()
        context = {'form': form}
        return render(request=request,
                      template_name='core/addmissiontype.html', context=context)

    def post(self, request, *args, **kwargs):
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            try:
                request.user.role.countyexpert.add_mission_type(name)
                messages.add_message(request, messages.INFO, 'نوع ماموریت جدید اضافه شد!')
            except DuplicatedInfoError as e:
                messages.add_message(request, messages.ERROR, 'نوع ماموریت با این اسم از قبل موجود است!')
        return HttpResponseRedirect(reverse('core:resources'))


class ChangeMissionType(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_EXPERT

    def get(self, request, mission_type_id):
        form = SingleStringForm()
        mission_type = MissionType.objects.get(id=mission_type_id)
        context = {'form': form, 'missiontype': mission_type}
        return render(request=request,
                      template_name='core/changemissiontype.html', context=context)

    def post(self, request, mission_type_id):
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            mission_type = MissionType.objects.get(id=mission_type_id)
            try:
                request.user.role.countyexpert.rename_mission_type(mission_type, name)
                messages.add_message(request, messages.INFO, 'نوع ماموریت بروز شد!')
            except DuplicatedInfoError as e:
                messages.add_message(request, messages.ERROR, 'نوع ماموریت با این اسم از قبل موجود است!')
        return HttpResponseRedirect(reverse('core:resources'))


class RemoveMissionType(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_EXPERT

    def get(self, request, mission_type_id):
        mission_type = MissionType.objects.get(id=mission_type_id)
        try:
            request.user.role.countyexpert.delete_mission_type(mission_type)
            messages.add_message(request, messages.INFO, 'نوع ماموریت حذف شد!')
        except BusyResourceError as e:
            messages.add_message(request, messages.ERROR, 'ماموریت‌هایی از این نوع موجود است!')
        return HttpResponseRedirect(reverse('core:resources'))


class AddSpeciality(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, *args, **kwargs):
        form = SingleStringForm()
        context = {'form': form}
        return render(request=request,
                      template_name='core/addspeciality.html', context=context)

    def post(self, request, *args, **kwargs):
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            try:
                request.user.role.moderator.countymoderator.add_speciality(name)
                messages.add_message(request, messages.INFO, 'نوع تخصص جدید اضافه شد!')
            except DuplicatedInfoError as e:
                messages.add_message(request, messages.ERROR, 'نوع تخصص با این اسم از قبل موجود است!')
        return HttpResponseRedirect(reverse('core:resources'))


class ChangeSpeciality(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, speciality_id):
        form = SingleStringForm()
        speciality = Speciality.objects.get(id=speciality_id)
        context = {'form': form, 'speciality': speciality}
        return render(request=request,
                      template_name='core/changespeciality.html', context=context)

    def post(self, request, speciality_id):
        form = SingleStringForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            speciality = Speciality.objects.get(id=speciality_id)
            try:
                request.user.role.moderator.countymoderator.rename_speciality(speciality, name)
                messages.add_message(request, messages.INFO, 'نوع تخصص بروز شد!')
            except DuplicatedInfoError as e:
                messages.add_message(request, messages.ERROR, 'نوع تخصص با این اسم از قبل موجود است!')
        return HttpResponseRedirect(reverse('core:resources'))


class RemoveSpeciality(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, speciality_id):
        speciality = Speciality.objects.get(id=speciality_id)
        try:
            request.user.role.moderator.countymoderator.delete_speciality(speciality)
            messages.add_message(request, messages.INFO, 'نوع تخصص حذف شد!')
        except BusyResourceError as e:
            messages.add_message(request, messages.ERROR, 'تیم‌هایی با این تخصص وجود دارد!')
        return HttpResponseRedirect(reverse('core:resources'))

