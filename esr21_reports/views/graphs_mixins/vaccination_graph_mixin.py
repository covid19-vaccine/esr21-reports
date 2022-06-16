from django.apps import apps as django_apps
from edc_base.view_mixins import EdcBaseViewMixin


class VaccinationGraphMixin(EdcBaseViewMixin):
    vaccination_details_model = 'esr21_subject.vaccinationdetails'
    vaccination_stats_model = 'esr21_reports.vaccinationstatistics'

    @property
    def vaccination_details_cls(self):
        return django_apps.get_model(self.vaccination_details_model)

    @property
    def vaccination_stats_cls(self):
        return django_apps.get_model(self.vaccination_stats_model)

    def site_dose_vaccination(self, site_id=None,  dose=None):
        site_vaccination = self.vaccination_details_cls.objects.filter(
            site_id=site_id,
            received_dose_before=dose,
            ).values_list(
                'subject_visit__subject_identifier',
                flat=True).distinct().count()
        return self.get_percentage(site_vaccination)

    def overal_site_dose_vaccination(self, site_id=None):
        site_vaccination = self.vaccination_details_cls.objects.filter(
            site_id=site_id,
            ).values_list(
                'subject_visit__subject_identifier',
                flat=True).distinct().count()
        return self.get_percentage(site_vaccination)

    @property
    def vaccines(self):
        vaccines = self.vaccination_stats_cls.objects.all()
        site_names = []
        first_dose = []
        second_dose = []
        booster_dose = []
        overall = []
        for vaccine in vaccines:
            site_names.append(vaccine.site)
            first_dose.append(vaccine.dose_1_percent)
            second_dose.append(vaccine.dose_2_percent)
            booster_dose.append(vaccine.dose_3_percent)
            overall.append(vaccine.overall_percent)
        return site_names, first_dose, second_dose, booster_dose, overall

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_names, first_dose, second_dose, booster_dose, overall = self.vaccines
        sites_first_doses = sum(first_dose)
        sites_second_doses = sum(second_dose)
        sites_booster_doses = sum(booster_dose)
        context.update(
            vac_details_labels=site_names,
            vac_details_first=first_dose,
            vac_details_second=second_dose,
            booster_dose_count=booster_dose,
            all_sites_dose=[sites_first_doses,
                            sites_second_doses,
                            sites_booster_doses],
        )
        return context

    def get_percentage(self, dose_count):
        site_vaccines = self.vaccination_details_cls.objects.values_list(
                'subject_visit__subject_identifier',
                flat=True).distinct().count()
        percentage = dose_count / site_vaccines * 100
        return round(percentage, 1)
