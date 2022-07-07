
from django.apps import apps as django_apps
from edc_base.view_mixins import EdcBaseViewMixin
from django.contrib.sites.models import Site
from django.db.models import Q
from edc_constants.constants import YES


class ScreeningGraphMixin(EdcBaseViewMixin):

    subject_screening_model = 'esr21_subject.eligibilityconfirmation'
    vaccination_model = 'esr21_subject.vaccinationdetails'
    vaccination_history_model = 'esr21_subject.vaccinationhistory'
    consent_model = 'esr21_subject.informedconsent'
    screening_stats_model = 'esr21_reports.screeningstatistics'
    second_screening_model = 'esr21_subject.screeningeligibility'

    @property
    def subject_screening_cls(self):
        return django_apps.get_model(self.subject_screening_model)

    @property
    def vaccination_model_cls(self):
        return django_apps.get_model(self.vaccination_model)

    @property
    def vaccination_history_cls(self):
        return django_apps.get_model(self.vaccination_history_model)

    @property
    def screening_eligibiliby_cls(self):
        return django_apps.get_model(self.second_screening_model)

    @property
    def screening_stats_model_cls(self):
        return django_apps.get_model(self.screening_stats_model)

    @property
    def consent_model_cls(self):
        return django_apps.get_model(self.consent_model)

    @property
    def site_screenings(self):
        site_screenings = []
        for site in self.sites_names:
            site_screenings.append([
                site, self.get_screened_by_site(site_name_postfix=site)])
        return site_screenings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        screening_stats = self.screening_stats_model_cls.objects.all()
        first_dose_total = 0
        second_dose_total = 0
        booster_dose_total = 0
        sites = []
        first_doses = []
        second_doses = []
        booster_doses = []

        for stats in screening_stats:
            first_dose_total += stats.dose1
            second_dose_total += stats.dose2
            booster_dose_total += stats.dose3
            sites.append(stats.site)
            first_doses.append(stats.dose1)
            second_doses.append(stats.dose2)
            booster_doses.append(stats.dose3)

        overall_site_screenings = [
            first_dose_total, second_dose_total,
            booster_dose_total]

        context.update(
            site_screenings=screening_stats,
            overall_screened=overall_site_screenings,
            sites=sites,
            first_doses=first_doses,
            second_doses=second_doses,
            booster_doses=booster_doses,
        )
        return context

    @property
    def all_screened_participants(self):
        return self.subject_screening_cls.objects.count()

    def first_dose_screening(self, site_id=None):
        screening = self.screening_eligibiliby_cls.objects.filter(
            site_id=site_id).distinct().count()
        total = self.second_dose_screening(site_id) + self.booster_dose_screening(site_id)
        overall = screening - total
        return overall

    def second_dose_screening(self, site_id=None):
        pids = self.vaccination_history_cls.objects.filter(
            received_vaccine=YES,
            dose_quantity=1
        ).exclude(dose1_product_name='azd_1222').values_list(
            'subject_identifier', flat=True).distinct()
        screening = self.screening_eligibiliby_cls.objects.filter(
            subject_identifier__in=pids, site_id=site_id).distinct().count()
        return screening

    def booster_dose_screening(self, site_id=None):
        pids = self.vaccination_history_cls.objects.filter(
            received_vaccine=YES,
            dose_quantity=2
        ).exclude(Q(dose1_product_name='azd_1222') | Q(dose2_product_name='azd_1222')).values_list('subject_identifier', flat=True).distinct()
        screening = self.screening_eligibiliby_cls.objects.filter(
            subject_identifier__in=pids, site_id=site_id).distinct().count()
        return screening
