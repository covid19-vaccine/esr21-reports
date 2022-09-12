from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_model_wrapper import ModelWrapper
from edc_base.utils import get_utcnow

from esr21_subject.models import VaccinationDetails


class AeModelWrapper(ModelWrapper):

    model = 'esr21_subject.adverseeventrecord'
    next_url_attrs = ['subject_identifier']
    next_url_name = 'esr21_ae_reports_url'

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def consent_model_obj(self):
        """Returns a consent model instance or None.
        """
        consent_model_cls = django_apps.get_model(self.consent_model_wrapper_cls.model)
        try:
            return consent_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def gender(self):
        return self.consent_model_obj.gender

    @property
    def age(self):
        today = get_utcnow().now().date()
        born = self.consent_model_obj.dob
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @property
    def first_dose(self):
        """Return the first dose form instance
        """
        try:
            vaccination = VaccinationDetails.objects.get(
                subject_visit__subject_identifier=self.subject_identifier,
                received_dose_before='first_dose')
        except VaccinationDetails.DoesNotExist:
            return None
        else:
            return vaccination

    @property
    def second_dose(self):
        """Return the second dose form instance
        """
        try:
            vaccination = VaccinationDetails.objects.get(
                subject_visit__subject_identifier=self.subject_identifier,
                received_dose_before='second_dose')
        except VaccinationDetails.DoesNotExist:
            return None
        else:
            return vaccination

    @property
    def first_dose_date(self):
        if self.first_dose:
            return self.first_dose.vaccination_date
        return None

    @property
    def second_dose_date(self):
        if self.first_dose:
            return self.second_dose.vaccination_date
        return None
