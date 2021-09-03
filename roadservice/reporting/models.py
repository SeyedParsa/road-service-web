from collections import defaultdict

from django.db.models import Avg, Q
from django.utils import timezone
from django.db import models
from core.models import ServiceTeam, Region, Issue, Mission
from reporting.exceptions import SingletonInitError


class Report:
    class Type(models.TextChoices):
        INTERVAL_REPORT = 'I',
        DISTRIBUTION_REPORT = 'D',
        SUBREGIONS_REPORT = 'S'


class IntervalReport(Report):
    def __init__(self, region, start_time, end_time):
        self.region = region
        self.start_time = start_time
        self.end_time = end_time
        self.interval_delta = timezone.timedelta(weeks=1)
        self.bin_starts = []
        self.team_counts = []
        self.issue_counts = []
        self.failed_issue_counts = []
        self.successful_issue_counts = []
        self.score_averages = []
        self.Type = Report.Type.INTERVAL_REPORT


class DistributionReport(Report):
    def __init__(self, region):
        self.region = region
        self.mission_type_dist = defaultdict(int)
        self.speciality_dist = defaultdict(int)
        self.machinery_type_dist = defaultdict(int)
        self.score_dist = defaultdict(int)
        self.Type = Report.Type.DISTRIBUTION_REPORT


class SubregionsReport(Report):
    def __init__(self, region):
        self.region = region
        self.subregions_info = []  # the list would contain tuples of the form:
        # (subregion, mission_count, issue_count, mission_score_avg, mission_success_rate, team_count)
        self.Type = Report.Type.SUBREGIONS_REPORT


class ReportGenerator:
    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if ReportGenerator.__instance is not None:
            raise SingletonInitError()
        ReportGenerator.__instance = self

    def get_interval_report(self, region, start_time, end_time):
        report = IntervalReport(region, start_time, end_time)
        time = start_time
        while time < end_time:
            bin_start = time
            bin_end = time + report.interval_delta
            time += report.interval_delta
            report.bin_starts.append(bin_start)
            report.team_counts.append(region.get_teams().filter(
                Q(created_at__lt=bin_end) & (Q(deleted_at__gt=bin_start) | Q(deleted_at__isnull=True))).count())
            issues = region.get_issues().filter(created_at__gte=bin_start, created_at__lt=bin_end)
            report.issue_counts.append(issues.count())
            report.failed_issue_counts.append(issues.filter(state=Issue.State.FAILED).count())
            report.successful_issue_counts.append(issues.filter(
                Q(state=Issue.State.DONE) | Q(state=Issue.State.SCORED)).count())
            missions = region.get_missions().filter(issue__created_at__gte=bin_start, issue__created_at__lt=bin_end)
            report.score_averages.append(missions.aggregate(Avg('score'))['score__avg'])
        return report

    def get_distribution_report(self, region):
        report = DistributionReport(region)
        for mission in region.get_missions():
            report.mission_type_dist[mission.type.name] += 1
            if mission.score is not None:
                report.score_dist[mission.score] += 1
        for team in region.get_teams():
            report.speciality_dist[team.speciality.name] += 1
        for machinery in region.get_machineries():
            report.machinery_type_dist[machinery.type.name] += machinery.total_count
        return report

    def get_subregions_report(self, region):
        report = SubregionsReport(region)
        for subregion in region.sub_regions.all():
            missions = subregion.get_missions()
            issues = subregion.get_issues()
            mission_count = missions.count()
            issue_count = issues.count()
            mission_score_avg = missions.aggregate(Avg('score'))['score__avg']  # TODO
            successful_issues_count = issues.filter(Q(state=Issue.State.DONE) | Q(state=Issue.State.SCORED)).count()
            failed_issues_count = issues.filter(state=Issue.State.FAILED).count()
            finished_issues_count = successful_issues_count + failed_issues_count
            mission_success_rate = None if (finished_issues_count == 0) else \
                successful_issues_count / finished_issues_count
            team_count = subregion.get_teams().count()
            report.subregions_info.append((subregion, mission_count, issue_count,
                                           mission_score_avg, mission_success_rate, team_count))
        return report
