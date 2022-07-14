from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import POS, NEG, YES, IND


class HomologousSeries(EdcBaseViewMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            homologous_enrollments=self.site_enrollments,
            homologous_vaccinations=self.site_vaccinations,
            demographics_data=self.site_demographics,
            adverse_events=self.site_adverse_events,
        )
        return context

    @property
    def homologous_list(self):
        return self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose'
            ).values_list('subject_visit__subject_identifier').distinct()

    @property
    def site_enrollments(self):
        enrolled, main_cohort, sub_cohort = self.cohort_participants
        return [
            main_cohort,
            sub_cohort,
            enrolled
        ]

    @property
    def cohort_participants(self):
        esr21_sub = []
        esr21_main = []
        total_enrollment = []

        for site_id in self.sites_ids:
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
            total_enrollment.append(enrolled)

            esr21_sub.append(esr21_sub_vacc)
            esr21_main.append(esr21_main_vacc)

        # calculate totals for main and sub cohort enrollments
        esr21_sub.append(sum(esr21_sub))
        esr21_main.append(sum(esr21_main))
        total_enrollment.append(sum(total_enrollment))

        return total_enrollment, esr21_main, esr21_sub

    @property
    def site_vaccinations(self):
        first_dose = []
        second_dose = []
        booster_dose = []

        for site_id in self.sites_ids:
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

            first_dose.append(len(dose_1))
            second_dose.append(dose_2)
            booster_dose.append(dose_3)

        first_dose.append(sum(first_dose))
        second_dose.append(sum(second_dose))
        booster_dose.append(sum(booster_dose))

        return [
            first_dose, second_dose, booster_dose
        ]

    @property
    def site_demographics(self):
        males = []
        females = []
        hiv_pos = []
        hiv_neg = []
        hiv_unknown = []
        pos_preg = []
        diabetes = []
        for site_id in self.sites_ids:
            site_male = self.informed_consent_cls.objects.filter(
                gender='M', subject_identifier__startswith=f'150-0{site_id}',
                subject_identifier__in=self.homologous_list
                ).values_list('subject_identifier', flat=True).distinct().count()

            site_female = self.informed_consent_cls.objects.filter(
                gender='F', subject_identifier__startswith=f'150-0{site_id}',
                subject_identifier__in=self.homologous_list
                ).values_list('subject_identifier', flat=True).count()

            males.append(site_male)
            females.append(site_female)

            site_hiv_pos = self.rapid_hiv_testing_cls.objects.filter(
                Q(hiv_result=POS) | Q(hiv_result=POS),
                subject_visit__subject_identifier__startswith=f'150-0{site_id}',
                subject_visit__subject_identifier__in=self.homologous_list
                ).values_list('subject_visit__subject_identifier', flat=True).distinct().count()

            site_hiv_neg = self.rapid_hiv_testing_cls.objects.filter(
                (Q(hiv_result=NEG) | Q(rapid_test_result=NEG)),
                subject_visit__subject_identifier__startswith=f'150-0{site_id}',
                subject_visit__subject_identifier__in=self.homologous_list
                ).values_list('subject_visit__subject_identifier', flat=True).distinct().count()

            site_hiv_unknown = self.rapid_hiv_testing_cls.objects.filter(
                (Q(hiv_result=IND) | Q(rapid_test_result=IND)),
                subject_visit__subject_identifier__startswith=f'150-0{site_id}',
                subject_visit__subject_identifier__in=self.homologous_list
                ).values_list('subject_visit__subject_identifier', flat=True).distinct().count()

            hiv_pos.append(site_hiv_pos)
            hiv_neg.append(site_hiv_neg)
            hiv_unknown.append(site_hiv_unknown)

            site_pos_preg = self.pregnancy_model_cls.objects.filter(
                subject_visit__subject_identifier__in=self.homologous_list,
                result=POS,
                subject_visit__subject_identifier__startswith=f'150-0{site_id}',
            ).distinct().count()
            pos_preg.append(site_pos_preg)

            site_diabetes = self.medical_history_cls.objects.filter(
                subject_visit__subject_identifier__in=self.homologous_list,
                diabetes=YES,
                subject_visit__subject_identifier__startswith=f'150-0{site_id}',
                ).count()
            diabetes.append(site_diabetes)

        males.append(sum(males))
        females.append(sum(females))
        hiv_pos.append(sum(hiv_pos))
        hiv_neg.append(sum(hiv_neg))
        hiv_unknown.append(sum(hiv_unknown))
        pos_preg.append(sum(pos_preg))
        diabetes.append(sum(diabetes))

        return [
            males,
            females,
            hiv_pos,
            hiv_neg,
            hiv_unknown,
            pos_preg,
            diabetes
        ]

    @property
    def site_adverse_events(self):
        aes = []
        saes = []
        aesi = []
        for site_id in self.sites_ids:
            site_ae = self.ae_record_cls.objects.filter(
                adverse_event__subject_visit__subject_identifier__in=self.homologous_list,
                adverse_event__subject_visit__subject_identifier__startswith=f'150-0{site_id}',
            ).distinct().count()
            site_sae = self.sae_record_cls.objects.filter(
                serious_adverse_event__subject_visit__subject_identifier__in=self.homologous_list,
                serious_adverse_event__subject_visit__subject_identifier__startswith=f'150-0{site_id}',
            ).distinct().count()
            site_aesi = self.aei_record_cls.objects.filter(
                special_interest_adverse_event__subject_visit__subject_identifier__in=self.homologous_list,
                special_interest_adverse_event__subject_visit__subject_identifier__startswith=f'150-0{site_id}',
            ).distinct().count()

            aes.append(site_ae)
            saes.append(site_sae)
            aesi.append(site_aesi)

        aes.append(sum(aes))
        saes.append(sum(saes))
        aesi.append(sum(aesi))

        return [aes, saes, aesi]
