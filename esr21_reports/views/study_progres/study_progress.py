from django.apps import apps as django_apps
from django.db.models import Q
from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
from .homologous_series import HomologousSeries
from .heterologous_series import HeterologousSeries
from ..site_helper_mixin import SiteHelperMixin


class StudyProgressView(NavbarViewMixin, TemplateView,
                        HomologousSeries, HeterologousSeries,
                        SiteHelperMixin):
    template_name = 'esr21_reports/study_progress_report.html'
    navbar_selected_item = 'Study Progress'
    navbar_name = 'esr21_reports'

    vaccination_model = 'esr21_subject.vaccinationdetails'
    vaccination_history_model = 'esr21_subject.vaccinationhistory'
    onschedule_model = 'esr21_subject.onschedule'
    informed_consent_model = 'esr21_subject.informedconsent'
    rapid_hiv_testing_model = 'esr21_subject.rapidhivtesting'
    pregnancy_model = 'esr21_subject.pregnancytest'
    medical_history_Model = 'esr21_subject.medicalhistory'
    ae_record_model = 'esr21_subject.adverseeventrecord'
    sae_record_model = 'esr21_subject.seriousadverseeventrecord'
    aei_record_model = 'esr21_subject.specialinterestadverseeventrecord'

    @property
    def vaccination_model_cls(self):
        return django_apps.get_model(self.vaccination_model)

    @property
    def vaccination_history_cls(self):
        return django_apps.get_model(self.vaccination_history_model)

    @property
    def informed_consent_cls(self):
        return django_apps.get_model(self.informed_consent_model)

    @property
    def rapid_hiv_testing_cls(self):
        return django_apps.get_model(self.rapid_hiv_testing_model)

    @property
    def pregnancy_model_cls(self):
        return django_apps.get_model(self.pregnancy_model)

    @property
    def medical_history_cls(self):
        return django_apps.get_model(self.medical_history_Model)

    @property
    def onschedule_model_cls(self):
        return django_apps.get_model(self.onschedule_model)

    @property
    def sae_record_cls(self):
        return django_apps.get_model(self.sae_record_model)

    @property
    def aei_record_cls(self):
        return django_apps.get_model(self.aei_record_model)

    @property
    def ae_record_cls(self):
        return django_apps.get_model(self.ae_record_model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            total_stats=self.total_stats,
            sites_names=self.sites_names
        )
        return context

    def total_stats(self):
        first_dose = self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose').count()
        second_dose = self.vaccination_model_cls.objects.filter(
            received_dose_before='second_dose').count()
        booster_dose = self.vaccination_model_cls.objects.filter(
            received_dose_before='booster_dose').count()
        overall_enrollment = first_dose+self.second_dose_enrollment+self.booster_dose_enrollment

        return [
            overall_enrollment,
            first_dose,
            second_dose,
            booster_dose
        ]

    @property
    def second_dose_enrollment(self):
        ids = self.vaccination_history_cls.objects.filter(Q(dose_quantity=1)).exclude(
            Q(dose1_product_name='azd_1222')).values_list('subject_identifier',flat=True)
        total = self.vaccination_model_cls.objects.filter(
                received_dose_before='second_dose',
                subject_visit__subject_identifier__in=ids).values_list(
                    'subject_visit__subject_identifier', flat=True).distinct().count()
        return total

    @property
    def booster_dose_enrollment(self):
        ids = self.vaccination_history_cls.objects.filter(
            dose_quantity=2).exclude(
                Q(dose1_product_name='azd_1222') |
                Q(dose2_product_name='azd_1222')).values_list(
                    'subject_identifier', flat=True)

        total = self.vaccination_model_cls.objects.filter(
            received_dose_before='booster_dose',
            subject_visit__subject_identifier__in=ids).values_list(
                'subject_visit__subject_identifier',
                flat=True).distinct().count()
        return total
