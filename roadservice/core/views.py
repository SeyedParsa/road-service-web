from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from khayyam import *

from accounts.forms import SignUpForm
from accounts.models import User, Role
from core.exceptions import DuplicatedInfoError, BusyResourceError, ResourceNotFoundError, AccessDeniedError, \
    OccupiedUserError
from core.forms import AssignModeratorForm, RegionMultipleFilterForm, SingleStringForm, TeamCustomForm, AssignExpertForm
from core.models import Region, Issue, MissionType, Speciality, MachineryType, Machinery, ServiceTeam


class Home(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTY_EXPERT, Role.Type.COUNTRY_MODERATOR,
                                            Role.Type.PROVINCE_MODERATOR, Role.Type.COUNTY_MODERATOR]

    def process(self, request, form, regions=None):
        if request.user.role.type == Role.Type.COUNTY_EXPERT:
            issues = request.user.role.get_concrete().get_issues()
        else:
            if not regions:
                regions = [request.user.role.get_concrete().region]
            issues = request.user.role.get_concrete().get_issues(regions)
        context = {'issues': issues.order_by('-created_at'), 'form': form}
        return render(request=request,
                      template_name='core/dashboard.html',
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
                   'teams': teams.order_by('-id'),
                   'machinery_count': machinery_count,
                   'mission_types': mission_types.order_by('-id'),
                   'specialities': specialities.order_by('-id')}
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


class AddTeam(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, *args, **kwargs):
        context = {'specialities': Speciality.objects.all()}
        return render(request=request,
                      template_name='core/changeteam.html', context=context)

    def post(self, request, *args, **kwargs):
        try:
            form = TeamCustomForm(request.POST)
            request.user.role.moderator.countymoderator.add_service_team(form.speciality, form.users)
            messages.add_message(request, messages.INFO, 'تیم اضافه  شد!')
        except ResourceNotFoundError:
            messages.add_message(request, messages.ERROR, 'منابع درخواستی وجود ندارند!')
        except OccupiedUserError:
            messages.add_message(request, messages.ERROR, 'منابع درخواستی نقش دیگری دارند!')
        return HttpResponseRedirect(reverse('core:resources'))


class ChangeTeam(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, team_id):
        team = ServiceTeam.objects.get(id=team_id)
        context = {'team': team, 'specialities': Speciality.objects.all()}
        return render(request=request,
                      template_name='core/changeteam.html', context=context)

    def post(self, request, team_id):
        team = ServiceTeam.objects.get(id=team_id)
        try:
            form = TeamCustomForm(request.POST)
            request.user.role.moderator.countymoderator.edit_service_team(team, form.speciality, form.users)
            messages.add_message(request, messages.INFO, 'تیم بروز شد!')
        except ResourceNotFoundError:
            messages.add_message(request, messages.ERROR, 'منابع درخواستی وجود ندارند!')
        except OccupiedUserError:
            messages.add_message(request, messages.ERROR, 'منابع درخواستی نقش دیگری دارند!')
        return HttpResponseRedirect(reverse('core:resources'))


class RemoveTeam(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, team_id):
        team = ServiceTeam.objects.get(id=team_id)
        try:
            request.user.role.moderator.countymoderator.delete_service_team(team)
            messages.add_message(request, messages.INFO, 'تیم حذف شد!')
        except BusyResourceError:
            messages.add_message(request, messages.ERROR, 'تیم مشغول ماموریت است!')
        return HttpResponseRedirect(reverse('core:resources'))


class AddMachinery(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, machinery_type_id):
        machinery_type = MachineryType.objects.get(id=machinery_type_id)
        request.user.role.moderator.countymoderator.increase_machinery(machinery_type)
        messages.add_message(request, messages.INFO, str('یک ' + machinery_type.name + ' اضافه شد!'))
        return HttpResponseRedirect(reverse('core:resources'))


class RemoveMachinery(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type == Role.Type.COUNTY_MODERATOR

    def get(self, request, machinery_type_id):
        machinery_type = MachineryType.objects.get(id=machinery_type_id)
        try:
            request.user.role.moderator.countymoderator.decrease_machinery(machinery_type)
            messages.add_message(request, messages.INFO, str('یک ' + machinery_type.name + ' حذف شد!'))
        except ResourceNotFoundError:
            messages.add_message(request, messages.ERROR, str('ماشینی از این نوع وجود ندارد!'))
        except BusyResourceError:
            messages.add_message(request, messages.ERROR, str('همه‌ی ماشین‌های این نوع مشغولند!'))
        return HttpResponseRedirect(reverse('core:resources'))


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


class Signup(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTRY_MODERATOR,
                                            Role.Type.PROVINCE_MODERATOR, Role.Type.COUNTY_MODERATOR]

    def get(self, request):
        form = SignUpForm()
        return render(request=request,
                      template_name='core/signup.html',
                      context={'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password1']
            request.user.role.get_concrete().create_new_user(phone_number,
                                                             password,
                                                             phone_number,
                                                             first_name,
                                                             last_name)
            messages.success(request, "کاربر جدید با موافقیت اضافه شد!")
            return HttpResponseRedirect(reverse('core:resources'))
        else:
            messages.error(request, "فرم معتبر نیست!")
            return render(request=request,
                          template_name='core/signup.html',
                          context={'form': form})


class AssignModerator(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.PROVINCE_MODERATOR, Role.Type.COUNTY_MODERATOR,
                                            Role.Type.COUNTRY_MODERATOR]

    def get(self, request, *args, **kwargs):
        assign_moderator_form = AssignModeratorForm(moderator=request.user.role.get_concrete())
        return render(request=request,
                      template_name='core/assignmoderator.html',
                      context={'form': assign_moderator_form})

    def post(self, request, *args, **kwargs):
        moderator = request.user.role.get_concrete()
        form = AssignModeratorForm(request.POST, moderator=moderator)
        if form.is_valid():
            region_id = form.cleaned_data['region']
            region = Region.objects.get(id=region_id)
            phone_number = form.cleaned_data['phone_number']
            try:
                user = User.objects.get(phone_number=phone_number)
                moderator.assign_moderator(user, region)
                messages.add_message(request, messages.INFO, 'دسترسی داده شد!')
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'کاربر مورد نظر یافت نشد!')
            except AccessDeniedError:
                messages.add_message(request, messages.ERROR, 'شما مدیر این بخش نیستید!')
            except OccupiedUserError:
                messages.add_message(request, messages.ERROR, 'کاربر نقش دیگری دارد!')
            return HttpResponseRedirect(reverse('core:resources'))
        else:
            messages.add_message(request, messages.ERROR, 'فرم نامعتبر است!')
        return render(request=request,
                      template_name='core/assignmoderator.html',
                      context={'form': form})


class AssignExpert(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTY_MODERATOR]

    def get(self, request, *args, **kwargs):
        form = AssignExpertForm()
        return render(request=request,
                      template_name='core/assignexpert.html',
                      context={'form': form})

    def post(self, request, *args, **kwargs):
        country_moderator = request.user.role.get_concrete()
        form = AssignExpertForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            try:
                user = User.objects.get(phone_number=phone_number)
                country_moderator.assign_expert(user)
                messages.add_message(request, messages.INFO, 'دسترسی داده شد!')
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'کاربر مورد نظر یافت نشد!')
            except OccupiedUserError:
                messages.add_message(request, messages.ERROR, 'کاربر نقش دیگری دارد!')
            return HttpResponseRedirect(reverse('core:resources'))
        else:
            messages.add_message(request, messages.ERROR, 'فرم نامعتبر است!')
        return render(request=request,
                      template_name='core/assignexpert.html',
                      context={'form': form})
