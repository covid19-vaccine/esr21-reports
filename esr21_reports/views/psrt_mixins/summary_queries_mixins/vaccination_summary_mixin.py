from django.apps import apps as django_apps
from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin

class VaccinationSummaryMixin(EdcBaseViewMixin):
    
    vaccination_details_model = 'esr21_subject.vaccinationdetails'
    
    @property
    def vaccination_details_cls(self):
        return django_apps.get_model(self.vaccination_details_model)

    @property
    def first_dose_second_dose_missing_statistics(self):
        """
        First dose missing and second dose not missing    
        """
        overall_missing_doses = []
        for site_id in self.site_ids:
            first_dose = self.vaccination_details_cls.objects.filter(
                        Q(received_dose_before='first_dose') &
                        Q(site_id=site_id)).distinct().values_list(
                            'subject_visit__subject_identifier', flat=True)
                        
            second_dose = self.vaccination_details_cls.objects.filter(
                        Q(received_dose_before='second_dose') &
                        Q(site_id=site_id) &
                       ~Q(subject_visit__subject_identifier__in=first_dose))
                        
            overall_missing_doses.append(second_dose.count())
        
        
        return ["First dose missing and second dose not missing", *overall_missing_doses, sum(overall_missing_doses)]
    
    
    @property
    def ineligible_vaccinated_participant_statistics(self):
        """
        participant vaccinated but ineligible    
        """
        not_eligible = []
        screening_identifiers = self.eligibility_confirmation_cls.objects.filter(
            is_eligible=False).values_list('screening_identifier', flat=True)
        
        consented_ineligible = self.consent_model_cls.objects.filter(
            screening_identifier__in=screening_identifiers).values_list('subject_identifier', flat=True)
                
        for site_id in self.site_ids:
            vaccinated_count = self.vaccination_details_cls.objects.filter(
                Q(site_id=site_id) & 
                Q(subject_visit__subject_identifier__in=consented_ineligible)).count()
            not_eligible.append(vaccinated_count)

        return ['Participant vaccinated but ineligible', *not_eligible, sum(not_eligible)]   

    # @property
    # def vaccinated_no_icf_statistics(self):
    #     """
    #     subject_identifier is found in vaccination form but all of the following are missing: eligibility confirmation, informed consent and screening confirmation    
    #     """
    #     return ["subject_identifier is found in vaccination form but all of the following are missing: eligibility confirmation, informed consent and screening confirmation", 0, 0, 0, 0, 0, 0]
    #

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            first_dose_second_dose_stats = self.first_dose_second_dose_missing_statistics,
            ineligible_vaccinated_participants_stats = self.ineligible_vaccinated_participant_statistics)
        return context