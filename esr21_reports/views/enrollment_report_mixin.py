import orjson as json
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin

from esr21_reports.models.dashboard_statistics import DashboardStatistics
from ..models import VaccinationStatistics, EnrollmentStatistics

class EnrollmentReportMixin(EdcBaseViewMixin):
    
    vaccination_model =  'esr21_subject.vaccinationdetails'
    onschedule_model = 'esr21_subject.onschedule'


    @property
    def vaccination_model_cls(self):
        return django_apps.get_model(self.vaccination_model)

    @property
    def onschedule_model_cls(self):
        return django_apps.get_model(self.onschedule_model)

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
            self.sub_cohort_participants
            ]

    @property
    def received_two_doses(self):
        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='second_dose')).count()
        gaborone = self.get_vaccination_by_site('Gaborone', dose='second_dose')
        maun = self.get_vaccination_by_site('Maun', dose='second_dose')
        serowe = self.get_vaccination_by_site('Serowe', dose='second_dose')
        f_town = self.get_vaccination_by_site('Francistown', dose='second_dose')
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
        overall = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='booster_dose')).count()
        gaborone = self.get_vaccination_by_site('Gaborone', dose='booster_dose')
        maun = self.get_vaccination_by_site('Maun', dose='booster_dose')
        serowe = self.get_vaccination_by_site('Serowe', dose='booster_dose')
        f_town = self.get_vaccination_by_site('Francistown', dose='booster_dose')
        phikwe = self.get_vaccination_by_site('Phikwe', dose='booster_dose')

        return ['Booster dose', overall, gaborone,
                maun, serowe, f_town, phikwe]

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
        totals = self.cohort_participants('esr21_sub_enrol_schedule')
        return ['Sub cohort', *totals]

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
            
            
    @property        
    def vaccination_details_preprocessor(self):
        return self.cache_preprocessor('vaccinated_statistics')
    
    @property
    def enrollment_details_preprocessor(self):
        return self.cache_preprocessor('enrolled_statistics')
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            enrolled_participants=self.enrollment_details_preprocessor,
            vaccinated_participants=self.vaccination_details_preprocessor
        )
        return context
