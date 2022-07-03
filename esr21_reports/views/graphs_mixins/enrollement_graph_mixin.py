import json
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from edc_base.view_mixins import EdcBaseViewMixin
from esr21_subject.models import VaccinationDetails, InformedConsent
from edc_constants.constants import FEMALE, MALE
from django.db.models import Q

from ...models import VaccinationEnrollments


class EnrollmentGraphMixin(EdcBaseViewMixin):

    enrollment_stats_model = 'esr21_reports.enrollmentstatistics'
    
    doses = ['sinovac', 'pfizer', 'moderna', 'janssen', 'astrazeneca']

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

    @property
    def total_2nd_booster_enrollments(self):
        doses = VaccinationEnrollments.objects.all()
        total_doses = []
        for dose in doses:
            total = dose.sinovac+dose.pfizer+dose.astrazeneca+dose.moderna+dose.janssen
            total_doses.append(total)
        return sum(total_doses)

    @property
    def pie_total_doses_enrolled(self):
        other_vaccines = self.total_2nd_booster_enrollments
        total = VaccinationDetails.objects.filter(received_dose_before='first_dose').distinct().count()
        azd_1222 = total - other_vaccines
        return [azd_1222, other_vaccines]

    def total_enrolled(self):
        second_dose = self.second_dose_at_enrollment
        booster_dose = self.booster_dose_at_enrollment
        first_dose = self.first_dose_enrollment
        return [sum(first_dose), sum(second_dose), sum(booster_dose)]

    @property
    def first_dose_enrollment(self):
        totals = []
        for site_id in range(40, 45):
            first_dose = VaccinationDetails.objects.filter(
                received_dose_before='first_dose', site_id=site_id).distinct().count()
            totals.append(first_dose)
        return totals

    @property
    def second_dose_at_enrollment(self):
        totals = []

        ids = self.vaccination_history_cls.objects.filter(
            Q(dose_quantity=1)).exclude(
            Q(dose1_product_name='azd_1222')).values_list('subject_identifier',
                                                          flat=True)

        for site_id in range(40, 45):
            total_second_dose = self.vaccination_model_cls.objects.filter(
                site_id=site_id,
                received_dose_before='second_dose',
                subject_visit__subject_identifier__in=ids).values_list(
                    'subject_visit__subject_identifier', flat=True).distinct().count()
            totals.append(total_second_dose)

        return totals

    @property
    def booster_dose_at_enrollment(self):
        totals = []

        ids = self.vaccination_history_cls.objects.filter(
            dose_quantity=2).exclude(
                Q(dose1_product_name='azd_1222') | Q(dose2_product_name='azd_1222')).values_list(
                'subject_identifier', flat=True)

        for site_id in range(40, 45):
            total_booster = self.vaccination_model_cls.objects.filter(
                site_id=site_id,
                received_dose_before='booster_dose',
                subject_visit__subject_identifier__in=ids
                ).values_list('subject_visit__subject_identifier',
                              flat=True).distinct().count()
            totals.append(total_booster)

        return totals

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
            overall_dose_enrollements=self.total_2nd_booster_enrollments,
            total_enrolled=self.total_enrolled(),
            second_dose_at_enrollment=self.second_dose_at_enrollment,
            booster_dose_at_enrollment=self.booster_dose_at_enrollment,
            first_dose_enrollment=self.first_dose_enrollment,
            pie_total_doses_enrolled=self.pie_total_doses_enrolled
        )
        return context
