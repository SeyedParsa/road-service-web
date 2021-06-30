from django.contrib import messages
from django.shortcuts import render

# Create your views here.
from django.views import View

from reporting.forms import TimeReportForm, StatusReportForm
from reporting.models import TimeReport, ReportGenerator


# class TestView(View):
#     def get(self, request, *args, **kwargs):
#         print('heey')
#         new_chart = BarGraph()
#         new_chart.data.label = "اعداد زیبا"  # can change data after creation
#
#         chart_json = new_chart.get()
#
#         return render(request=request,
#                       template_name='chart.html',
#                       context={"chartJSON": chart_json})

class StatusReport(View):
    def get(self, request, *args, **kwargs):
        status_report_form = StatusReportForm()
        # print(time_report_form.region.choices)
        return render(request=request,
                      template_name='reporting/statusreport.html',
                      context={'form': status_report_form })

    def post(self, request, *args, **kwargs):
        form = StatusReportForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            region_id = int(form.cleaned_data['region'])
            region = form.region_instances[region_id]
            #status_report = ReportGenerator(0).st(region, start_date, end_date)
            # context['report'] = time_report
            # teams_chart = GraphGenerator(0).get_bar_chart(time_report[0])
            # issues_chart = GraphGenerator(0).get_bar_chart(time_report[1])
            #
            # print(teams_chart.data.label)
            # print(issues_chart.data.label)
            # team_chart_json = teams_chart.get()
            # issues_chart_json = issues_chart.get()
            # context["teamChartJSON"] = team_chart_json
            # context["issuesChartJSON"] = issues_chart_json
            # context["teams_report"] = time_report[0]
            # context["issues_report"] = time_report[1]
            # context["missions_report"] = time_report[2]
            # context["scores_report"] = time_report[3]
            messages.add_message(request, messages.INFO, 'گزارش به روز شد!')
        else:
            print('invalid form!')
        return render(request=request,
                      template_name='reporting/statusreport.html',
                      context=context)




class TimeReport(View):
    def get(self, request, *args, **kwargs):
        time_report_form = TimeReportForm()
        # print(time_report_form.region.choices)
        return render(request=request,
                      template_name='reporting/timereport.html',
                      context={'form': time_report_form})

    def post(self, request, *args, **kwargs):
        form = TimeReportForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            region_id = int(form.cleaned_data['region'])
            region = form.region_instances[region_id]
            time_report = ReportGenerator(0).time_report(region, start_date, end_date)
            # context['report'] = time_report
            # teams_chart = GraphGenerator(0).get_bar_chart(time_report[0])
            # issues_chart = GraphGenerator(0).get_bar_chart(time_report[1])
            #
            # print(teams_chart.data.label)
            # print(issues_chart.data.label)
            # team_chart_json = teams_chart.get()
            # issues_chart_json = issues_chart.get()
            # context["teamChartJSON"] = team_chart_json
            # context["issuesChartJSON"] = issues_chart_json
            context["teams_report"] = time_report[0]
            context["issues_report"] = time_report[1]
            context["missions_report"] = time_report[2]
            context["scores_report"] = time_report[3]
            messages.add_message(request, messages.INFO, 'گزارش به روز شد!')
        else:
            print('invalid form!')
        return render(request=request,
                      template_name='reporting/timereport.html',
                      context=context)
