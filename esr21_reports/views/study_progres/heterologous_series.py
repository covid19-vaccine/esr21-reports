from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import YES


class HeterologousSeries(EdcBaseViewMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            heterologous_enrollments=self.enrollments.filter(series='heterologous'),
            heterologous_vaccinations=self.vaccinations_per_product,
            heterologous_demographics=self.demographics.filter(series='heterologous'),
            heterologous_aes=self.adverse_events.filter(series='heterologous'),
        )
        return context

    def enrollments(self, site_id=None):
        enrolled, main_cohort, sub_cohort = self.cohort(site_id=site_id)
        return [
            ['Main Cohort', main_cohort],
            ['Sub Cohort', sub_cohort],
            ['Totals', enrolled]
        ]

    def cohort(self, site_id=None):

        esr21_sub_enrols = self.vaccination_model_cls.objects.filter(
            received_dose=YES,
            subject_visit__subject_identifier__in=self.heterologous_enrols,
            subject_visit__schedule_name__startswith='esr21_sub',
            ).values_list('subject_visit__subject_identifier').distinct().count()

        esr21_main_enrols = self.vaccination_model_cls.objects.filter(
            Q(subject_visit__schedule_name__startswith='esr21_enrol') | Q(
                subject_visit__schedule_name__startswith='esr21_fu') | Q(
                    subject_visit__schedule_name__startswith='esr21_boost'),
            subject_visit__subject_identifier__in=self.heterologous_enrols
            ).values_list('subject_visit__subject_identifier').distinct().count()

        enrolled = self.vaccination_model_cls.objects.filter(
            subject_visit__subject_identifier__in=self.heterologous_enrols
            ).values_list('subject_visit__subject_identifier').distinct().count()

        return esr21_main_enrols, esr21_sub_enrols, enrolled

    @property
    def vaccinations_per_product(self):
        second_dose_dict = {}
        booster_dose_dict = {}
        product_names = ['sinovac', 'pfizer', 'astrazeneca', 'moderna', 'janssen']

        for name in product_names:
            dose2_counts = []
            booster_counts = []
            dose2_screenings = self.vaccination_history_cls.objects.filter(
                dose_quantity='1', dose1_product_name=name).values_list(
                    'subject_identifier', flat=True).distinct()

            booster1_screenings = self.vaccination_history_cls.objects.filter(
                dose_quantity='2', dose1_product_name=name).values_list(
                    'subject_identifier', flat=True).distinct()

            booster2_screenings = self.vaccination_history_cls.objects.filter(
                dose_quantity='2', dose2_product_name=name).values_list(
                    'subject_identifier', flat=True).distinct()

            for site_id in self.sites_ids:
                dose2 = self.vaccination_model_cls.objects.filter(
                    received_dose_before='second_dose',
                    subject_visit__subject_identifier__in=dose2_screenings,
                    site_id=site_id
                ).values_list('subject_visit__subject_identifier').distinct().count()
                dose2_counts.append(dose2)

                booster1_dose = self.get_booster_vaccinations(
                    sidxs=booster1_screenings, site_id=site_id)

                booster2_dose = self.get_booster_vaccinations(
                    sidxs=booster2_screenings, site_id=site_id)
                booster_counts.append([booster1_dose, booster2_dose])

            dose2_counts.append(sum(dose2_counts))
            second_dose_dict.update({f'{name}': dose2_counts})

            booster_counts.append([sum(d) for d in zip(*booster_counts)])
            booster_dose_dict.update({f'{name}': booster_counts})
        second_dose_dict.update(totals=[sum(d) for d in zip(*second_dose_dict.values())])
#         booster_dose_dict.update(totals=[sum(d) for d in zip(*booster_dose_dict.values())])
        return [second_dose_dict, booster_dose_dict]

    def get_booster_vaccinations(self, sidxs=[], site_id=40):
        return self.vaccination_model_cls.objects.filter(
            received_dose_before='booster_dose',
            subject_visit__subject_identifier__in=sidxs,
            site_id=site_id
            ).values_list('subject_visit__subject_identifier').distinct().count()

    @property
    def heterologous_enrols(self):
        screenings = self.vaccination_history_cls.objects.exclude(
            (Q(dose1_product_name='azd_1222') & Q(dose_quantity=1)) |
            (Q(dose1_product_name='azd_1222') & Q(dose2_product_name='azd_1222') & Q(dose_quantity=2)) |
            (Q(dose1_product_name='azd_1222') & Q(dose2_product_name='azd_1222') & Q(dose3_product_name='azd_1222') & Q(dose_quantity=3))
            ).values_list('subject_identifier').distinct()

        return self.vaccination_model_cls.objects.filter(
            received_dose=YES,
            subject_visit__subject_identifier__in=screenings).values_list(
                'subject_visit__subject_identifier', flat=True).distinct()
