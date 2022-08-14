import collections
from datetime import datetime

from django.apps import apps as django_apps
from django.contrib.sites.models import Site


from edc_base.view_mixins import EdcBaseViewMixin


class EnrollmentOvertimeMixin(EdcBaseViewMixin):

    vaccine_model = 'esr21_subject.vaccinationdetails'

    @property
    def vaccine_model_cls(self):
        return django_apps.get_model(self.vaccine_model)

    @property
    def months(self):
        vaccinations_details = self.vaccine_model_cls.objects.all().values_list(
            'vaccination_date', flat=True)
        months = [vd.strftime("%B %Y") for vd in vaccinations_details if vd]
        months = list(set(months))
        months.sort(key=lambda date: datetime.strptime(date, "%B %Y"))
        return months
    
    @property
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return self.months

    @property
    def homologous_first_dose_idnt(self):
        vaccinations_details = self.vaccine_model_cls.objects.filter(
            received_dose_before='first_dose'
        ).values_list('subject_visit__subject_identifier', flat=True)
        return list(set(vaccinations_details))

    @property
    def first_dose_overtime(self):
        vaccinations_details = self.vaccine_model_cls.objects.filter(
            received_dose_before='first_dose'
        ).values_list('vaccination_date', flat=True)
        months = [vd.strftime("%B %Y") for vd in vaccinations_details if vd]
        frequency = collections.Counter(months)
        frequency_data = sorted(frequency.items(), key = lambda x:datetime.strptime(x[0], '%B %Y'))
        return dict(frequency_data)
    
    @property
    def second_dose_overtime(self):
        vaccinations_details = self.vaccine_model_cls.objects.filter(
            received_dose_before='second_dose',
            subject_visit__subject_identifier__in=self.homologous_first_dose_idnt,
        ).values_list('vaccination_date', flat=True)
        months = [vd.strftime("%B %Y") for vd in vaccinations_details if vd]
        frequency = {}
        for label in self.get_labels:
            # checking the element in dictionary
            frequency[label] = months.count(label)
        frequency_data = sorted(frequency.items(), key = lambda x:datetime.strptime(x[0], '%B %Y'))
        return dict(frequency_data)

    @property
    def booster_dose_overtime(self):
        vaccinations_details = self.vaccine_model_cls.objects.filter(
            received_dose_before='booster_dose',
            subject_visit__subject_identifier__in=self.homologous_first_dose_idnt,
        ).values_list('vaccination_date', flat=True)
        months = [vd.strftime("%B %Y") for vd in vaccinations_details if vd]
        frequency = {}
        for label in self.get_labels:
            # checking the element in dictionary
            frequency[label] = months.count(label)
        frequency_data = sorted(frequency.items(), key = lambda x:datetime.strptime(x[0], '%B %Y'))
        return dict(frequency_data)

    @property
    def get_data(self):
        data_dict = {}
        data = []
        return data
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        homo_first_dose_overtime = list(self.first_dose_overtime.values())
        home_second_dose_overtime = list(self.second_dose_overtime.values())
        homo_booster_dose_overtime = list(self.booster_dose_overtime.values())
        context.update(
            months=self.get_labels,
            homo_first_dose_overtime=homo_first_dose_overtime,
            home_second_dose_overtime=home_second_dose_overtime,
            homo_booster_dose_overtime=homo_booster_dose_overtime
            )
        return context