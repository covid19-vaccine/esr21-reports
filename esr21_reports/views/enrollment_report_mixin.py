from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin
from ..models import VaccinationEnrollments, ScreeningStatistics


class EnrollmentReportMixin(EdcBaseViewMixin):

    vaccination_model = 'esr21_subject.vaccinationdetails'
    vaccination_history_model = 'esr21_subject.vaccinationhistory'
    onschedule_model = 'esr21_subject.onschedule'
    pregnancy_test_model = 'esr21_subject.pregnancytest'
    covid_19_results_model = 'esr21_subject.covid19results'

    eligibility_model = 'esr21_subject.eligibilityconfirmation'
    screening_eligibility_model = 'esr21_subject.screeningeligibility'
    vaccination_history_model = 'esr21_subject.vaccinationhistory'

    screenings = ScreeningStatistics.objects.all()

    @property
    def vaccination_history_model_cls(self):
        return django_apps.get_model(self.vaccination_history_model)

    @property
    def eligibility_model_cls(self):
        return django_apps.get_model(self.eligibility_model)

    @property
    def screening_eligibility_cls(self):
        return django_apps.get_model(self.screening_eligibility_model)

    doses = ['sinovac', 'pfizer', 'moderna', 'janssen', 'astrazeneca']

    @property
    def vaccination_model_cls(self):
        return django_apps.get_model(self.vaccination_model)

    @property
    def vaccination_history_cls(self):
        return django_apps.get_model(self.vaccination_history_model)

    @property
    def pregnancy_test_cls(self):
        return django_apps.get_model(self.pregnancy_test_model)

    @property
    def onschedule_model_cls(self):
        return django_apps.get_model(self.onschedule_model)

    @property
    def covid_19_results_cls(self):
        return django_apps.get_model(self.covid_19_results_model)

    @property
    def pregnant_enrollment(self):
        ids = self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose').values_list(
            'subject_visit__subject_identifier', flat=True).distinct()
        totals = []
        for site_id in range(40, 45):
            total = self.pregnancy_test_cls.objects.filter(
                result='POS', site_id=site_id,
                subject_visit__subject_identifier__in=ids).values_list(
                    'subject_visit__subject_identifier', flat=True).distinct().count()
            totals.append(total)

        return ['Pregnant Enrollment', sum(totals), *totals]

    @property
    def covid_positives(self):
        totals = []
        for site_id in range(40, 45):
            total = self.covid_19_results_cls.objects.filter(
                covid_result='POS',
                subject_visit__subject_identifier__startswith=f'150-0{site_id}').count()
            totals.append(total)

        return ['COVID Positives', sum(totals), *totals]

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

        return ['Second dose at enrollment', sum(totals), *totals]

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

        return ['Booster dose at enrollment', sum(totals), *totals]

    @property
    def screening_for_second_dose(self):
        # Screening for second dose enrolment
        dose1_ids = self.vaccination_history_model_cls.objects.filter(
            dose_quantity=1).exclude(
                dose1_product_name='azd_1222').values_list(
                    'subject_identifier', flat=True)
        totals = []
        for site_id in range(40, 45):
            total = self.screening_eligibility_cls.objects.filter(
                subject_identifier__in=dose1_ids, site_id=site_id
                ).distinct().count()
            totals.append(total)

        return ['Screening for second dose', sum(totals), *totals]

    @property
    def screening_for_booster_dose(self):
        # Screening for booster dose enrolment
        sites = Site.objects.all()
        dose2_ids = self.vaccination_history_model_cls.objects.filter(
            dose_quantity=2).exclude(Q(dose1_product_name='azd_1222') |
                                     Q(dose2_product_name='azd_1222')
                                     ).values_list('subject_identifier',
                                                   flat=True)
        totals = []
        for site in sites:
            total = self.screening_eligibility_cls.objects.filter(
                subject_identifier__in=dose2_ids, site_id=site.id).distinct().count()
            totals.append(total)

        return ['Screening for booster dose', sum(totals), *totals]

    @property
    def enrolled_participants(self):
        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='first_dose')).count()
        gaborone = self.get_enrolled_by_site('Gaborone').count()
        maun = self.get_enrolled_by_site('Maun').count()
        serowe = self.get_enrolled_by_site('Serowe').count()
        f_town = self.get_enrolled_by_site('Francistown').count()
        phikwe = self.get_enrolled_by_site('Phikwe').count()

        return [
            ['Enrolled', overall, gaborone, maun, serowe, f_town, phikwe],
            self.main_cohort_participants,
            self.sub_cohort_participants,
            self.pregnant_enrollment,
            self.covid_positives,
            self.second_dose_at_enrollment,
            self.booster_dose_at_enrollment,
        ]

    @property
    def received_two_doses(self):
        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='second_dose')).count()
        gaborone = self.get_vaccination_by_site('Gaborone', dose='second_dose')
        maun = self.get_vaccination_by_site('Maun', dose='second_dose')
        serowe = self.get_vaccination_by_site('Serowe', dose='second_dose')
        f_town = self.get_vaccination_by_site(
            'Francistown', dose='second_dose')
        phikwe = self.get_vaccination_by_site('Phikwe', dose='second_dose')

        return ['Second dose', overall, gaborone,
                maun, serowe, f_town, phikwe]

    @property
    def received_one_doses(self):
        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='first_dose')).count()
        gaborone = self.get_vaccination_by_site('Gaborone', dose='first_dose')
        maun = self.get_vaccination_by_site('Maun', dose='first_dose')
        serowe = self.get_vaccination_by_site('Serowe', dose='first_dose')
        f_town = self.get_vaccination_by_site('Francistown', dose='first_dose')
        phikwe = self.get_vaccination_by_site('Phikwe', dose='first_dose')

        return ['First dose', overall, gaborone,
                maun, serowe, f_town, phikwe]

    @property
    def received_booster_doses(self):
        totals = list()

        vaccinated = self.vaccination_model_cls.objects.values_list(
            'subject_visit__subject_identifier', flat=True).distinct()

        for site_id in range(40, 45):
            total_booster = self.vaccination_model_cls.objects.filter(
                received_dose_before='booster_dose', site_id=site_id,
                subject_visit__subject_identifier__in=vaccinated).values_list(
                    'subject_visit__subject_identifier', flat=True
                    ).distinct().count()
            totals.append(total_booster)

        return ['Booster dose', sum(totals), *totals]

    def cohort_participants(self, cohort=None):
        on_schedule = self.onschedule_model_cls.objects.filter(
            schedule_name=cohort).values_list(
                'subject_identifier', flat=True).distinct()

        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='first_dose')).values_list(
                'subject_visit__subject_identifier', flat=True)
        overall = [pid for pid in overall if pid in on_schedule]

        gaborone = self.get_enrolled_by_site('Gaborone')
        gaborone = [pid for pid in gaborone if pid in on_schedule]

        maun = self.get_enrolled_by_site('Maun')
        maun = [pid for pid in maun if pid in on_schedule]

        serowe = self.get_enrolled_by_site('Serowe')
        serowe = [pid for pid in serowe if pid in on_schedule]

        f_town = self.get_enrolled_by_site('Francistown')
        f_town = [pid for pid in f_town if pid in on_schedule]

        phikwe = self.get_enrolled_by_site('Phikwe')
        phikwe = [pid for pid in phikwe if pid in on_schedule]

        return [len(overall), len(gaborone), len(maun),
                len(serowe), len(f_town), len(phikwe)]

    @property
    def main_cohort_participants(self):
        totals = self.cohort_participants('esr21_enrol_schedule')
        return ['Main cohort', *totals]

    @property
    def sub_cohort_participants(self):
        totals = list()
        for site_id in range(40, 45):
            onschedule = self.onschedule_model_cls.objects.filter(
                schedule_name__startswith='esr21_sub', site_id=site_id).values_list(
                    'subject_identifier', flat=True).distinct()
            vacc = self.vaccination_model_cls.objects.filter(
                received_dose='Yes',
                subject_visit__subject_identifier__in=onschedule).values_list(
                    'subject_visit__subject_identifier').distinct().count()
            totals.append(vacc)

        return ['Sub cohort', sum(totals), *totals]

    def get_enrolled_by_site(self, site_name_postfix):
        site_id = self.get_site_id(site_name_postfix)
        if site_id:
            return self.vaccination_model_cls.objects.filter(
                received_dose_before='first_dose',
                site_id=site_id).values_list(
                'subject_visit__subject_identifier', flat=True)

    def get_site_id(self, site_name_postfix):
        try:
            return Site.objects.get(name__endswith=site_name_postfix).id
        except Site.DoesNotExist:
            pass

    def get_vaccination_by_site(self, site_name_postfix, dose=None):
        site_id = self.get_site_id(site_name_postfix)
        if site_id:
            return self.vaccination_model_cls.objects.filter(
                Q(received_dose_before=dose) &
                Q(site_id=site_id)).count()

    def second_dose_enrollments_elsewhere(self):
        total_doses = ['Second dose(first dose elsewhere)']
        for dose in self.doses:
            dose_ids = self.vaccination_history_cls.objects.filter(
                dose_quantity=1, dose1_product_name=dose).values_list(
                    'subject_identifier', flat=True)

            total = self.vaccination_model_cls.objects.filter(
                received_dose_before='second_dose',
                subject_visit__subject_identifier__in=dose_ids
                ).values_list('subject_visit__subject_identifier',
                              flat=True).distinct().count()
            total_doses.append(total)

        return total_doses

    def booster_enrollment_elsewhere(self):
        total_doses = ['Booster dose (second dose elsewhere)']
        for dose in self.doses:
            dose_ids = self.vaccination_history_cls.objects.filter(
                Q(dose_quantity=2) & (Q(dose1_product_name=dose)
                                      | Q(dose2_product_name=dose))
                ).values_list('subject_identifier', flat=True)

            total = self.vaccination_model_cls.objects.filter(
                received_dose_before='booster_dose',
                subject_visit__subject_identifier__in=dose_ids
                ).values_list('subject_visit__subject_identifier',
                              flat=True).distinct().count()
            total_doses.append(total)

        return total_doses

    @property
    def vaccination_details_preprocessor(self):
        return self.cache_preprocessor('vaccinated_statistics')

    @property
    def enrollment_details_preprocessor(self):
        return self.cache_preprocessor('enrolled_statistics')

    @property
    def total_screening(self):
        dose1_totals = 0
        dose2_totals = 0
        dose3_totals = 0
        for screening in self.screenings:
            dose1_totals += screening.dose1
            dose2_totals += screening.dose2
            dose3_totals += screening.dose3
        return dose1_totals, dose2_totals, dose3_totals

    @property
    def total_2nd_booster_enrollments(self):
        doses = VaccinationEnrollments.objects.all()
        total_doses = []
        for dose in doses:
            total = dose.sinovac+dose.pfizer+dose.astrazeneca
            +dose.moderna+dose.janssen
            total_doses.append([dose.variable, dose.sinovac, dose.pfizer,
                                dose.astrazeneca, dose.moderna, dose.janssen,
                                total])
        return total_doses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            enrolled_participants=self.enrollment_details_preprocessor,
            vaccinated_participants=self.vaccination_details_preprocessor,
            second_booster_enrollments=self.total_2nd_booster_enrollments,
            screened_participants=self.screend_participants,
            screenings=self.screenings,
            total_screening=self.total_screening
        )
        return context

    @property
    def screend_participants(self, dose=None):
        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before=dose)).distinct().count()
        gaborone = self.get_enrolled_by_site('Gaborone').count()
        maun = self.get_enrolled_by_site('Maun').count()
        serowe = self.get_enrolled_by_site('Serowe').count()
        f_town = self.get_enrolled_by_site('Francistown').count()
        phikwe = self.get_enrolled_by_site('Phikwe').count()

        return [
            ['Enrolled', overall, gaborone, maun, serowe, f_town, phikwe],
            self.main_cohort_participants,
            self.sub_cohort_participants,
            self.pregnant_enrollment,
            self.covid_positives,
            self.second_dose_at_enrollment,
            self.booster_dose_at_enrollment,
        ]
