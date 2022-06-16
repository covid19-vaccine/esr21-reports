from __future__ import with_statement
from datetime import date
from edc_base.view_mixins import EdcBaseViewMixin
from esr21_subject.models import *
from dateutil.relativedelta import relativedelta
from django.contrib.sites.models import Site
from edc_constants.constants import *
from django.db.models import Q


class DemographicsMixin(EdcBaseViewMixin):

    @property
    def site_names(self):
        site_names = Site.objects.order_by('id').values_list('name', flat=True)
        site_names = list(map(lambda name: name.split('-')[1], site_names))
        return site_names

    @property
    def site_ids(self):
        site_ids = Site.objects.order_by('id').values_list('id', flat=True)
        return site_ids

    @property
    def enrolled_statistics(self):
        """
        Total Enrolled, should be vaccinated
        """

        total_enrolled = []

        for site_id in self.site_ids:
            enrolled = VaccinationDetails.objects.filter(
                received_dose_before='first_dose', site_id=site_id).values_list(
                'subject_visit__subject_identifier', flat=True).distinct().count()

            total_enrolled.append(enrolled)

        total_enrolled.insert(0, sum(total_enrolled))

        return total_enrolled

    @property
    def males_statistics(self):
        """
        Males enrolled in the study 
        """
        males = []

        for site_id in self.site_ids:

            males_consented = InformedConsent.objects.filter(
                site_id=site_id, gender=MALE, subject_identifier__in=self.enrolled_pids).count()
            males.append(males_consented)

        males.insert(0, sum(males))

        return ['Males', *males]

    @property
    def females_statistics(self):
        """
        Females enrolled in the study
        """
        females = []

        for site_id in self.site_ids:

            females_consented = InformedConsent.objects.filter(
                site_id=site_id, gender=FEMALE, subject_identifier__in=self.enrolled_pids).count()
            females.append(females_consented)

        females.insert(0, sum(females))

        return ['Females', *females]

    def _get_age_range(self, site_id, lower_limit_age, upper_limit_age=None) -> int:

        total = 0

        if lower_limit_age and upper_limit_age:
            lower_limit_dob = (
                date.today() - relativedelta(years=lower_limit_age)).isoformat()
            upper_limit_dob = (
                date.today() - relativedelta(years=upper_limit_age)).isoformat()
            total = InformedConsent.objects.filter(dob__range=[
                                                   upper_limit_dob, lower_limit_dob], site_id=site_id, subject_identifier__in=self.enrolled_pids).count()

        elif lower_limit_age and not upper_limit_age:
            lower_limit_dob = (
                date.today() - relativedelta(years=lower_limit_age)).isoformat()
            total = InformedConsent.objects.filter(
                dob__lte=lower_limit_dob, site_id=site_id, subject_identifier__in=self.enrolled_pids).count()

        return total

    @property
    def age_range_statistics(self):
        age_18_to_30 = []
        age_30_to_40 = []
        age_40_to_50 = []
        age_50_to_60 = []
        age_60_to_70 = []
        age_70_and_above = []

        for site_id in self.site_ids:

            totals = self._get_age_range(site_id, 18, 29)
            age_18_to_30.append(totals)

            totals = self._get_age_range(site_id, 30, 39)
            age_30_to_40.append(totals)

            totals = self._get_age_range(site_id, 40, 49)
            age_40_to_50.append(totals)

            totals = self._get_age_range(site_id, 50, 59)
            age_50_to_60.append(totals)

            totals = self._get_age_range(site_id, 60, 69)
            age_60_to_70.append(totals)

            totals = self._get_age_range(site_id, 70)
            age_70_and_above.append(totals)

        age_18_to_30.insert(0, sum(age_18_to_30))
        age_30_to_40.insert(0, sum(age_30_to_40))
        age_40_to_50.insert(0, sum(age_40_to_50))
        age_50_to_60.insert(0, sum(age_50_to_60))
        age_60_to_70.insert(0, sum(age_60_to_70))
        age_70_and_above.insert(0, sum(age_70_and_above))

        return dict(age_18_to_30=age_18_to_30,
                    age_30_to_40=age_30_to_40,
                    age_40_to_50=age_40_to_50,
                    age_50_to_60=age_50_to_60,
                    age_60_to_70=age_60_to_70,
                    age_70_and_above=age_70_and_above)

    @property
    def hiv_statistics(self):
        hiv_positive = []
        hiv_negative = []
        hiv_unknown = []

        for site_id in self.site_ids:

            status = POS
            positive = RapidHIVTesting.objects.filter((
                Q(subject_visit__subject_identifier__in=self.enrolled_pids) &
                Q(site_id=site_id)) & (Q(hiv_result=status) |
                                       Q(rapid_test_result=status))).count()

            status = NEG
            negative = RapidHIVTesting.objects.filter((
                Q(subject_visit__subject_identifier__in=self.enrolled_pids) &
                Q(site_id=site_id)) & (Q(hiv_result=status) |
                                       Q(rapid_test_result=status))).count()

            status = IND
            unknown = RapidHIVTesting.objects.filter((
                Q(subject_visit__subject_identifier__in=self.enrolled_pids) &
                Q(site_id=site_id)) & (Q(hiv_result=status) |
                                       Q(rapid_test_result=status))).count()

            hiv_positive.append(positive)
            hiv_negative.append(negative)
            hiv_unknown.append(unknown)

        hiv_positive.insert(0, sum(hiv_positive))
        hiv_negative.insert(0, sum(hiv_negative))
        hiv_unknown.insert(0, sum(hiv_unknown))

        return [['HIV Positive', *hiv_positive],
                ['HIV Negative', *hiv_negative],
                ['Unknown', *hiv_unknown]]

    @property
    def race_statistics(self):
        black_african = []
        asian = []
        caucasian = []
        other_race = []

        for site_id in self.site_ids:

            ethnicity_count = DemographicsData.objects.filter(
                ethnicity='Black African', subject_visit__subject_identifier__in=self.enrolled_pids, site_id=site_id).count()
            black_african.append(ethnicity_count)

            ethnicity_count = DemographicsData.objects.filter(
                ethnicity='Asian', subject_visit__subject_identifier__in=self.enrolled_pids, site_id=site_id).count()
            asian.append(ethnicity_count)

            ethnicity_count = DemographicsData.objects.filter(
                ethnicity='Caucasian', subject_visit__subject_identifier__in=self.enrolled_pids, site_id=site_id).count()
            caucasian.append(ethnicity_count)

            ethnicity_count = DemographicsData.objects.filter(
                ethnicity_other__isnull=False, subject_visit__subject_identifier__in=self.enrolled_pids, site_id=site_id).count()
            other_race.append(ethnicity_count)

        black_african.insert(0, sum(black_african))
        asian.insert(0, sum(asian))
        caucasian.insert(0, sum(caucasian))
        other_race.insert(0, sum(other_race))

        return [['Black African', *black_african],
                ['Asian', *asian],
                ['Caucasian', *caucasian],
                ['Other Race', *other_race]]

    @property
    def enrolled_pids(self):
        enrolled = VaccinationDetails.objects.filter(
            received_dose_before='first_dose').values_list(
            'subject_visit__subject_identifier', flat=True).distinct()
        return enrolled

    @property
    def pregnancy_statistics(self):
        pregnancies = []
        for site_id in self.site_ids:
            male_consents = InformedConsent.objects.filter(
                gender=MALE).values_list('subject_identifier', flat=True)

            # exclude all males if any exist with pregnancy tests
            all_pregnancies = PregnancyTest.objects.filter(site_id=site_id, subject_visit__subject_identifier__in=self.enrolled_pids, result=POS)\
                .exclude(subject_visit__subject_identifier__in=male_consents) \
                .count()
            pregnancies.append(all_pregnancies)

        pregnancies.insert(0, sum(pregnancies))

        return ['Pregnancies', *pregnancies]

    @property
    def diabates_statistics(self):

        diabetes = []

        for site_id in self.site_ids:
            with_diabetes = MedicalHistory.objects.filter(
                subject_visit__subject_identifier__in=self.enrolled_pids, diabetes=YES, site_id=site_id,).count()

            diabetes.append(with_diabetes)

        diabetes.insert(0, sum(diabetes))

        return ["Diabetes", *diabetes]
    
    @property
    def demographics_statistics(self):
        statistics = dict()
        
        statistics.update(
            site_names=self.site_names,
            age_stats=self.age_range_statistics,
            diabates_stats=self.diabates_statistics,
            females_stats=self.females_statistics,
            males_stats=self.males_statistics,
            hiv_stats=self.hiv_statistics,
            pregnency_stats=self.pregnancy_statistics,
            race_stats=self.race_statistics,
        )
        
        return statistics
    
    @property
    def demographics_statistics_preprocessor(self):
        statistics =  self.cache_preprocessor('demographics_statistics')
        
        if statistics:
            return statistics
        else:
            return dict()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            **self.demographics_statistics_preprocessor
        )

        return context
