from edc_base.view_mixins import EdcBaseViewMixin
from django.apps import apps as django_apps
from django.db.models import Q


class DemographicsReportViewMixin(EdcBaseViewMixin):

    pregnancy_test_model = 'esr21_subject.pregnancytest'

    @property
    def pregnancy_test_cls(self):
        return django_apps.get_model(self.pregnancy_test_model)

    @property
    def received_two_doses(self):
        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='first_dose') &
            Q(received_dose_before='second_dose')).count()
        gaborone = self.get_vaccination_by_site('Gaborone')
        maun = self.get_vaccination_by_site('Maun')
        serowe = self.get_vaccination_by_site('Serowe')
        f_town = self.get_vaccination_by_site('Francistown')
        phikwe = self.get_vaccination_by_site('Phikwe')

        return ['Participants with two doses', overall, gaborone,
                maun, serowe, f_town, phikwe]

    @property
    def male_gender_by_site(self):
        overall_male = self.consent_model_cls.objects.filter(
            Q(gender='M')).count()
        gaborone = self.get_gender_by_site('Gaborone',gender='M')
        maun = self.get_gender_by_site('Maun', gender='M')
        serowe = self.get_gender_by_site('Serowe', gender='M')
        f_town = self.get_gender_by_site('Francistown', gender='M')
        phikwe = self.get_gender_by_site('Phikwe', gender='M')

        return [
            ['Males', overall_male, gaborone, maun, serowe, f_town, phikwe]
        ]

    @property
    def female_gender_by_site(self):
        overall_female = self.vaccination_model_cls.objects.filter(
            Q(gender='F')).count()
        gaborone = self.get_gender_by_site('Gaborone')
        maun = self.get_gender_by_site('Maun')
        serowe = self.get_gender_by_site('Serowe')
        f_town = self.get_gender_by_site('Francistown')
        phikwe = self.get_gender_by_site('Phikwe')

        return [
            ['Males', overall_female, gaborone, maun, serowe, f_town, phikwe]
        ]

    def get_vaccination_by_site(self, site_name_postfix):
        site_id = self.get_site_id(site_name_postfix)
        if site_id:
            return self.vaccination_model_cls.objects.filter(
                Q(received_dose_before='first_dose') &
                Q(received_dose_before='second_dose') &
                Q(site_id=site_id)).count()

    def get_gender_by_site(self, site_name_postfix, gender):
        site_id = self.get_site_id(site_name_postfix)
        if site_id:
            enrolled = self.vaccination_model_cls.objects.filter(
                received_dose_before='first_dose'
            ).values_list('subject_visit__subject_identifier', flat=True)
            return self.consent_model_cls.objects.filter(
                gender=gender,
                subject_identifier__in=enrolled).count()
