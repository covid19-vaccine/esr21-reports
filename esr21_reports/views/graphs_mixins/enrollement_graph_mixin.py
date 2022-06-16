import json
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from edc_base.view_mixins import EdcBaseViewMixin
from esr21_subject.models import VaccinationDetails, InformedConsent
from edc_constants.constants import FEMALE, MALE


class EnrollmentGraphMixin(EdcBaseViewMixin):

    enrollment_stats_model = 'esr21_reports.enrollmentstatistics'
    
    


    @property
    def enrollment_stats_cls(self):
        return django_apps.get_model(self.enrollment_stats_model)

    @property
    def site_age_dist(self):
        age_dist = []
        for site in self.sites_names:
            age_dist.append(
                [site, self.get_distribution_site(site_name_postfix=site)])
        return age_dist

    @property
    def site_ids(self):
        site_ids = Site.objects.order_by('id').values_list('id', flat=True)
        return site_ids

    def get_vaccinated_by_site(self, site_id):
        """Return a dictionary of site first dose vaccinations by gender.
        """
        statistics = {
            'females': [],
            'males': []}

        female_pids = InformedConsent.objects.filter(gender=FEMALE).values_list(
            'subject_identifier', flat=True)
        female_pids = list(set(female_pids))

        male_pids = InformedConsent.objects.filter(gender=MALE).values_list(
            'subject_identifier', flat=True)
        male_pids = list(set(male_pids))

        enrolled = VaccinationDetails.objects.distinct().count()
        males = VaccinationDetails.objects.filter(
            subject_visit__subject_identifier__in=male_pids,
            site_id=site_id).distinct().count()
        male_percentage = (males / enrolled) * 100
        statistics['males'].append(round(male_percentage, 1))

        females = VaccinationDetails.objects.filter(
            subject_visit__subject_identifier__in=female_pids,
            site_id=site_id).distinct().count()
        female_percentage = (females / enrolled) * 100
        statistics['females'].append(round(female_percentage, 1))

        return male_percentage, female_percentage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_enrollments = self.enrollment_stats_cls.objects.all()
        females = []
        males = []
        overalls = []
        sites = []
        totals = 0
        percentages = []
        for enrollment in all_enrollments:
            sites.append(enrollment.site)
            females.append(enrollment.female)
            males.append(enrollment.male)
            overalls.append(enrollment.total)
            totals += enrollment.total
        for overal in overalls:
            percentage = (overal / totals) * 100
            percentages.append(percentage)
        overalls.append(totals)
        sites.append('All Sites')
        context.update(
            site_names=sites,
            females=json.dumps(females),
            males=json.dumps(males),
            overall=json.dumps(overalls),
            overall_percentages=json.dumps(percentages),
        )
        return context
