from edc_base.view_mixins import EdcBaseViewMixin
from django.db.models import Q
from edc_constants.constants import YES

from django.apps import apps as django_apps


class PregnancySummaryMixin(EdcBaseViewMixin):
    
    pregnancy_test_model = 'esr21_subject.pregnancytest'
    vaccination_details_model = 'esr21_subject.vaccinationdetails'
    pregnancy_outcome_model = 'esr21_subject.pregoutcome'
    
    @property
    def pregnancy_outcome_model_cls(self):
        return django_apps.get_model(self.pregnancy_outcome_model)
    
    @property
    def vaccination_details_model_cls(self):
        return django_apps.get_model(self.vaccination_details_model)
    
    @property
    def pregnancy_test_model_cls(self):
        return django_apps.get_model(self.pregnancy_test_model)
    
    @property
    def no_preg_results_statistics(self):
        """
        No pregnancy result and F and child bearing potential    
        """
        
        no_pregnancy_test = []
        female_consents = self.consent_model_cls.objects.filter(
            gender='F').values_list('subject_identifier', flat=True)
        for site_id in self.site_ids:
            screening_eligibility = self.screening_eligibility_cls.objects.filter(
                Q(subject_identifier__in=female_consents) &
                Q(childbearing_potential=YES) &
                Q(site_id=site_id)).values_list('subject_identifier', flat=True)
                
            pregnancy = self.pregnancy_test_model_cls.objects.filter(
                Q(subject_visit__subject_identifier__in=screening_eligibility) &
                Q(site_id=site_id)
                ).values_list('subject_visit__subject_identifier', flat=True)
                
                
            no_pregnancy = list(set(screening_eligibility) - set(pregnancy))
                
            
            no_pregnancy_test.append(len(no_pregnancy))
            
    
        return ['No pregnancy result and F and child bearing potential', 
                *no_pregnancy_test, sum(no_pregnancy_test)]
        
    @property  
    def total_pregnancies(self):
        totals = []
        for site_id in range(40,45):
            total = self.pregnancy_test_model_cls.objects.filter(
                result='POS', site_id=site_id).values_list('subject_visit__subject_identifier').count()
            totals.append(total)
        
        return ['Total Pregnancies', sum(totals), *totals]
    
    @property
    def pregnancies_with_first_dose(self):
        totals = []
        # Pregnancy after 1st dose vaccination
        ids = self.vaccination_details_model_cls.objects.filter(received_dose_before='first_dose').values_list('subject_visit__subject_identifier', flat=True).distinct()
        for site_id in range(40,45):
            total = self.pregnancy_test_model_cls.objects.filter(result='POS',site_id=site_id, subject_visit__subject_identifier__in=ids).values_list('subject_visit__subject_identifier', flat=True).distinct().count()
            totals.append(total)
            
        return ['Total Pregnancies after 1st dose', sum(totals), *totals]
    
    @property
    def pregnacy_outcome(self):
        totals = []
        ids = self.vaccination_details_model_cls.objects.filter(received_dose_before='first_dose').values_list('subject_visit__subject_identifier', flat=True).distinct()

        for site_id in range(40,45):
            total = self.pregnancy_outcome_model_cls.objects.filter(site_id=site_id, subject_visit__subject_identifier__in=ids).values_list('subject_visit__subject_identifier', flat=True).distinct().count()
            totals.append(total)
            
        return ['Pregnancy Outcomes', sum(totals), *totals]
    
    @property
    def pregnancy_statistics(self):
        return [
            self.total_pregnancies,
            self.pregnancies_with_first_dose,
            self.pregnacy_outcome
        ]
    
    @property
    def pregnancy_statistics_preprocessor(self):
        statistics =  self.cache_preprocessor('pregnancy_statistics')
        
        if statistics:
            return statistics
        else:
            return list()

                
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        breakpoint()

        context.update(
            no_preg_results_stats = self.no_preg_results_statistics,
            pregnancy_statistics = self.pregnancy_statistics_preprocessor
        )

        return context
        