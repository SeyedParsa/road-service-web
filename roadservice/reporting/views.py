from abc import abstractmethod

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views import View

from accounts.models import Role
from core.models import Region
from reporting.forms import TimeReportForm, SingleRegionSelectForm
from reporting.models import ReportGenerator


class SingleRegionReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTRY_MODERATOR, Role.Type.PROVINCE_MODERATOR,
                                            Role.Type.COUNTY_MODERATOR]

    @abstractmethod
    def process(self, request, form, region=None):
        raise NotImplementedError

    def get(self, request):
        form = SingleRegionSelectForm(moderator=request.user.role.moderator)
        return self.process(request, form)

    def post(self, request):
        form = SingleRegionSelectForm(request.POST, moderator=request.user.role.moderator)
        region = None
        if form.is_valid():
            region_id = form.cleaned_data['region']
            region = Region.objects.get(id=region_id)
            messages.add_message(request, messages.INFO, 'گزارش به روز شد!')
        else:
            messages.add_message(request, messages.ERROR, 'فرم نامعتبر است!')
        return self.process(request, form, region)


class StatusReport(SingleRegionReportView):
    def process(self, request, form, region=None):
        if not region:
            region = request.user.role.moderator.region
        report = ReportGenerator.get_instance().get_distribution_report(region)
        return render(request=request,
                      template_name='reporting/statusreport.html',
                      context={'form': form, 'speciality_dist': dict(report.speciality_dist),
                               'mission_type_dist': dict(report.mission_type_dist),
                               'score_dist': dict(report.score_dist),
                               'machinery_type_dist': dict(report.machinery_type_dist)})


class TimeReport(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.has_role() and \
            self.request.user.role.type in [Role.Type.COUNTRY_MODERATOR, Role.Type.PROVINCE_MODERATOR,
                                            Role.Type.COUNTY_MODERATOR]

    def process(self, request, form, region=None, start_date=None, end_date=None):
        if not region:
            region = request.user.role.moderator.region
        if not start_date:
            start_date = None  # TODO @Mahdi: select some defualt start date
        if not end_date:
            end_date = None  # TODO @Mahdi: select some defualt end date
        # TODO: report = ReportGenerator.get_instance().get_...
        # TODO: Create context + RETURN render
        # return render(request=request,
        #               template_name='reporting/timereport.html',
        #               context={'form': time_report_form})

    def get(self, request):
        time_report_form = TimeReportForm(moderator=request.user.role.moderator)
        return self.process(request, time_report_form)

    def post(self, request, *args, **kwargs):
        form = TimeReportForm(request.POST)
        start_date = None
        end_date = None
        region = None
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            # TODO @Mahdi: make sure these dates are correct (that they're really what we want)
            region_id = form.cleaned_data['region']
            region = Region.objects.get(id=region_id)
            messages.add_message(request, messages.INFO, 'گزارش به روز شد!')
        else:
            messages.add_message(request, messages.ERROR, 'فرم نامعتبر است!')
        return self.process(request, form, region, start_date, end_date)


class RegionReport(SingleRegionReportView):
    def process(self, request, form, region):
        if not region:
            region = request.user.role.moderator.region
        # TODO report = ReportGenerator.get_instance().get_...
        # TODO: Create context + RETURN render
        # return render(request=request,
        #               template_name='reporting/regionreport.html',
        #               context={'form': status_report_form})
