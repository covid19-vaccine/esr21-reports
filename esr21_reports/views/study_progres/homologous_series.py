from edc_base.view_mixins import EdcBaseViewMixin
from esr21_reports.models import adverse_events


class HomologousSeries(EdcBaseViewMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            homologous_enrollments=self.enrollments,
            homologous_vaccinations=self.vaccination,
            # demographics_data=self.site_demographics(subject_identifiers=self.homologous_list),
            adverse_events=self.adverse_events,
        )
        return context

    @property
    def homologous_list(self):
        return self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='first_dose') & Q(received_dose_before='_dose')
            ).values_list('subject_visit__subject_identifier').distinct()

    @property
    def homologous_enrollments(self):
        enrolled, main_cohort, sub_cohort = self.cohort_participants
        return [
            ['Main Cohort', main_cohort],
            ['Sub Cohort', sub_cohort],
            ['Totals', enrolled]
        ]

    def cohort_participants(self, site_id=None):
        esr21_sub_onschedule = self.onschedule_model_cls.objects.filter(
            schedule_name__startswith='esr21_sub',
            subject_identifier__startswith=f'150-0{site_id}',
            ).values_list('subject_identifier', flat=True).distinct()

        esr21_sub_vacc = self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose',
            subject_visit__subject_identifier__in=esr21_sub_onschedule
            ).values_list('subject_visit__subject_identifier').distinct().count()

        esr21_main_onschedule = self.onschedule_model_cls.objects.filter(
            schedule_name__startswith='esr21_enrol_schedule',
            subject_identifier__startswith=f'150-0{site_id}',
            ).values_list('subject_identifier', flat=True).distinct()

        esr21_main_vacc = self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose',
            subject_visit__subject_identifier__in=esr21_main_onschedule
            ).values_list('subject_visit__subject_identifier').distinct().count()

        onschedule = self.onschedule_model_cls.objects.filter(
            subject_identifier__startswith=f'150-0{site_id}',
            ).values_list(
                'subject_identifier', flat=True).distinct()

        enrolled = self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose',
            subject_visit__subject_identifier__in=onschedule
            ).values_list('subject_visit__subject_identifier').distinct().count()

        return esr21_sub_vacc, esr21_main_vacc, enrolled

    def homologous_vaccinations(self, site_id):
        dose_1 = self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose', site_id=site_id
            ).values_list('subject_visit__subject_identifier').distinct()

        dose_2 = self.vaccination_model_cls.objects.filter(
            received_dose_before='second_dose',
            site_id=site_id,
            subject_visit__subject_identifier__in=dose_1
            ).values_list('subject_visit__subject_identifier').distinct().count()

        dose_3 = self.vaccination_model_cls.objects.filter(
            received_dose_before='booster_dose',
            site_id=site_id,
            subject_visit__subject_identifier__in=dose_1
            ).values_list('subject_visit__subject_identifier').distinct().count()

        dose_1 = dose_1.count()

        total = dose_1 + dose_2 + dose_3

        return [
            dose_1, dose_2, dose_3, total
        ]
