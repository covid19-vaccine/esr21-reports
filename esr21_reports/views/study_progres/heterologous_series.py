from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import YES


class HeterologousSeries(EdcBaseViewMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            heterologous_enrollments=self.enrollments,
            heterologous_vaccinations=self.vaccinations
        )
        return context

    @property
    def enrollments(self):
        enrolled, main_cohort, sub_cohort = self.cohort
        return [
            main_cohort,
            sub_cohort,
            enrolled
        ]

    @property
    def cohort(self):
        esr21_sub = []
        esr21_main = []
        total_enrollment = []

        for site_id in self.sites_ids:
            screenings = self.vaccination_history_cls.objects.filter(
                site_id=site_id).exclude(Q(dose1_product_name='azd_1222') | Q(
                    dose2_product_name='azd_1222')).values_list(
                        'subject_identifier', flat=True).distinct()

            esr21_sub_enrols = self.vaccination_model_cls.objects.filter(
                received_dose=YES,
                subject_visit__subject_identifier__in=screenings,
                subject_visit__schedule_name__startswith='esr21_sub',
                ).values_list('subject_visit__subject_identifier').distinct().count()

            esr21_main_enrols = self.vaccination_model_cls.objects.filter(
                Q(subject_visit__schedule_name__startswith='esr21_enrol') | Q(
                    subject_visit__schedule_name__startswith='esr21_fu') | Q(
                        subject_visit__schedule_name__startswith='esr21_boost'),
                subject_visit__subject_identifier__in=screenings
                ).values_list('subject_visit__subject_identifier').distinct().count()

            enrolled = self.vaccination_model_cls.objects.filter(
                subject_visit__subject_identifier__in=screenings
                ).values_list('subject_visit__subject_identifier').distinct().count()
            total_enrollment.append(enrolled)

            esr21_sub.append(esr21_sub_enrols)
            esr21_main.append(esr21_main_enrols)

        # calculate totals for main and sub cohort enrollments
        esr21_sub.append(sum(esr21_sub))
        esr21_main.append(sum(esr21_main))
        total_enrollment.append(sum(total_enrollment))

        return total_enrollment, esr21_main, esr21_sub

    @property
    def vaccinations(self):
        second_dose_dict = {}
        booster_dose_dict = {}
        product_names = ['sinovac', 'pfizer', 'astrazeneca', 'moderna', 'janssen']

        for name in product_names:
            dose2_screenings = self.vaccination_history_cls.objects.filter(
                dose_quantity='1', dose1_product_name=name).values_list(
                        'subject_identifier', flat=True).distinct()

            dose2 = self.vaccination_model_cls.objects.filter(
                received_dose_before='second_dose',
                subject_visit__subject_identifier__in=dose2_screenings
                ).values_list('subject_visit__subject_identifier').distinct().count()

            booster_screenings = self.vaccination_history_cls.objects.filter(
                Q(dose1_product_name=name) | Q(dose2_product_name=name),
                dose_quantity='2').values_list(
                    'subject_identifier', flat=True).distinct()

            booster_dose = self.vaccination_model_cls.objects.filter(
                received_dose_before='booster_dose',
                subject_visit__subject_identifier__in=booster_screenings
                ).values_list('subject_visit__subject_identifier').distinct().count()

            second_dose_dict.update({f'{name}': dose2})
            booster_dose_dict.update({f'{name}': booster_dose})
        second_dose_dict.update(totals=sum(second_dose_dict.values()))
        booster_dose_dict.update(totals=sum(booster_dose_dict.values()))
        return [second_dose_dict, booster_dose_dict]
