import datetime

from django.db import models

# Create your models here.


# from pychartjs import BaseChart, ChartType, Color
from pytz import utc

from core.models import ServiceTeam, Region, Issue, Mission


# class BarGraph(BaseChart):
#     type = ChartType.Bar
#
#     class labels:
#         def __init__(self):
#             self.dates = [1, 2, 3]
#
#     class data:
#         def __init__(self):
#             self.label = 'label'
#             self.data = [10, 20, 15]
#         backgroundColor = Color.Blue
#
#     def __init__(self, *args, **kwargs):
#         super().__init__()
#         # self.labels.dates = kwargs.pop('dates')
#         # self.data.data = kwargs.pop('values')
#         # self.data.label = kwargs.pop('label')


class Report:
    class Type(models.TextChoices):
        TIME_REPORT = 'T',
        STATE_REPORT = 'S',
        LIST_REPORT = 'L'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = models.CharField(max_length=40)
        self.type = models.CharField(max_length=2, choices=self.Type.choices)
        self.data = []

    class Meta:
        abstract = True


class TimeReport(Report):

    def add_item(self, time, value):
        # print('adding', time, value)
        self.data.append((time, value))

    def __init__(self, name, y_axis_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.y_axis_name = y_axis_name
        self.Type = Report.Type.TIME_REPORT


# class GraphGenerator:
#     class __GraphGenerator:
#         def __init__(self, arg):
#             self.val = arg
#
#         def __str__(self):
#             return repr(self) + self.val
#     instance = None

#
#     def __init__(self, arg):
#         if not GraphGenerator.instance:
#             GraphGenerator.instance = GraphGenerator.__GraphGenerator(arg)
#         else:
#             GraphGenerator.instance.val = arg
#
#     def __getattr__(self, name):
#         return getattr(self.instance, name)
#
#     def get_bar_chart(self, time_report):
#         bar_graph = BarGraph(label=time_report.name, dates=[str(a[0]) for a in time_report.data],
#                              values=[a[1] for a in time_report.data])
#         return bar_graph


# Singleton:
class ReportGenerator:
    class __ReportGenerator:
        def __init__(self, arg):
            self.val = arg

        def __str__(self):
            return repr(self) + self.val
    instance = None

    def __init__(self, arg):
        if not ReportGenerator.instance:
            ReportGenerator.instance = ReportGenerator.__ReportGenerator(arg)
        else:
            ReportGenerator.instance.val = arg

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def is_county_matching_region(self, county, region):
        return region.type is Region.Type.COUNTY and county.name == region.name\
        or (region.type is Region.Type.PROVINCE and county.province.name == region.name)\
        or (region.type is Region.Type.COUNTRY and county.province.country.name == region.name)

    def region_teams_time_report(self, region, start_time, end_time):
        time_report = TimeReport(name="تعداد تیم‌های بخش انتخابی در بازه انتخابی", y_axis_name="تعداد تیم")
        service_teams = list(ServiceTeam.objects.all())
        region_teams = [team for team in service_teams if self.is_county_matching_region(team.county, region)]
        # start_time = min(team.created_at for team in region_teams)
        # end_time = datetime.datetime.now()
        # start_time = start_time.replace(tzinfo=utc)
        # end_time = end_time.replace(tzinfo=utc)
        # while start_time.date() <= end_time.date():
        while start_time <= end_time:
            time_report.add_item(start_time, len(list(team for team in region_teams
                                                      if team.created_at.date() <= start_time
                                                      and (team.deleted_at is None
                                                           or team.deleted_at.date() >= start_time))))
            start_time += datetime.timedelta(days=1)
        return time_report

    def region_issues_time_report(self, region, start_time, end_time):
        time_report = TimeReport(name="تعداد مشکلات بخش انتخابی در بازه انتخابی", y_axis_name="تعداد مشکلات")
        issues = list(Issue.objects.all())
        region_issues = [issue for issue in issues if self.is_county_matching_region(issue.county, region)]

        while start_time <= end_time:
            time_report.add_item(start_time, len(list(issue for issue in region_issues
                                                      if issue.created_at.date() == start_time)))
            start_time += datetime.timedelta(days=1)

        return time_report

    def region_missions_time_report(self, region, start_time, end_time):
        # TODO: Report different types of missions
        time_report = TimeReport(name="تعداد ماموریت‌های بخش انتخابی در بازه انتخابی", y_axis_name="تعداد ماموریت‌ها")
        missions = list(Mission.objects.all())
        region_missions = [mission for mission in missions if self.is_county_matching_region(mission.county, region)]

        while start_time <= end_time:
            time_report.add_item(start_time, len(list(mission for mission in region_missions
                                                      if mission.created_at_date == start_time)))
            start_time += datetime.timedelta(days=1)

        return time_report

    def region_scores_time_report(self, region, start_time, end_time):
        # TODO: add service teams scores
        time_report = TimeReport(name="تعداد ماموریت‌های بخش انتخابی در بازه انتخابی", y_axis_name="تعداد ماموریت‌ها")
        missions = list(Mission.objects.all())
        region_missions = [mission for mission in missions if
                           self.is_county_matching_region(mission.county, region)]

        score_sum = 0
        score_cnt = 0
        while start_time <= end_time:
            daily_missions = list(mission for mission in region_missions
                                                      if mission.created_at_date == start_time)
            mission_scores = [mission.score for mission in daily_missions if mission.state == Issue.State.SCORED]
            score_sum += sum(mission_scores)
            score_cnt += len(mission_scores)
            time_report.add_item(start_time, score_sum/score_cnt if score_cnt > 0 else 0)
            start_time += datetime.timedelta(days=1)
        return time_report

    def time_report(self, region, start_time, end_time):
        result = [self.region_teams_time_report(region, start_time, end_time),
                  self.region_issues_time_report(region, start_time, end_time),
                  self.region_missions_time_report(region, start_time, end_time),
                  self.region_scores_time_report(region, start_time, end_time)]
        return result
