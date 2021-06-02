from django.shortcuts import render

# Create your views here.
from django.views import View

from reporting.forms import TimeReportForm
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


class TimeReportView(View):
    def get(self, request, *args, **kwargs):
        print('heey! get request')
        time_report_form = TimeReportForm()
        print(time_report_form.regions)
        # print(time_report_form.region.choices)
        return render(request=request,
                      template_name='timereports.html',
                      context={'form': time_report_form})

    def post(self, request, *args, **kwargs):
        form = TimeReportForm(request.POST)
        print('hoy! post request')
        context = {'form': form}
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            region_id = int(form.cleaned_data['region'])
            region = form.regionInstances[region_id]
            time_report = ReportGenerator(0).time_report(region, start_date, end_date)
            # context['report'] = time_report
            print(time_report[0].name)
            print(time_report[1].name)
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
        else:
            print('invalid form!')
        return render(request=request,
                      template_name='timereports.html',
                      context=context)
