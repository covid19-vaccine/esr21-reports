from django.apps import apps as django_apps
from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin


class AdverseEventSummaryMixin(EdcBaseViewMixin):
    
    ae_model = 'esr21_subject.adverseeventrecord'
    
    @property
    def ae_model_cls(self):
        return django_apps.get_model(self.ae_model)
    
    @property
    def ae_statistics(self):
        """
        AE start date is before first dose    
        """
        ae_stats = []
        for site_id in self.site_ids:
            site_aes = 0
            aes = self.ae_model_cls.objects.filter(site_id=site_id).values_list(
                'adverse_event__subject_visit__subject_identifier','start_date')
            for ae in aes:
                subject_identifier = ae[0]
                ae_start_date = ae[1]
                try:
                    self.vaccination_details_cls.objects.get(
                        Q(received_dose_before='first_dose') &
                        Q(subject_visit__subject_identifier=subject_identifier) &
                        Q(vaccination_date__date__gt=ae_start_date))
                except self.vaccination_details_cls.DoesNotExist:
                    pass
                else:
                    site_aes += 1
            ae_stats.append(site_aes)
              
        return ["AE start date is before first dose", *ae_stats, sum(ae_stats)]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            ae_stats = self.ae_statistics)
        return context