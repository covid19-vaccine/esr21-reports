from edc_base.view_mixins import EdcBaseViewMixin

from .adverse_event_mixin import AdverseEventRecordMixin

class AdverseEventRecordViewMixin(EdcBaseViewMixin, AdverseEventRecordMixin):
    
    
    @property
    def ae_statistics(self):
        return dict(
            ae_overall_count=self.ae_overall,
            overral_adverse_events=self.overral_adverse_events,
            hiv_uninfected=self.hiv_uninfected,
            hiv_infected=self.hiv_infected,
            received_first_dose=self.received_first_dose,
            received_second_dose=self.received_second_dose,
            related_ip=self.related_ip,
            not_related_ip=self.not_related_ip,
            received_first_dose_plus_28=self.received_first_dose_plus_28,
    )
    
    @property
    def ae_statistics_preprocessor(self):
        stats = self.cache_preprocessor('ae_statistics')
        if stats:
            return stats
        else:
            return dict()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
           # all_ae=self.all_ae_records,
            **self.ae_statistics_preprocessor,
            # ae_overall_count=self.ae_overall
        )
        return context
