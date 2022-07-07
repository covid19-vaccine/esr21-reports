
from edc_base.view_mixins import EdcBaseViewMixin
from .serious_adverse_event_mixin import SeriousAdverseEventRecordMixin


class SeriousAdverseEventRecordViewMixin(EdcBaseViewMixin,
                                         SeriousAdverseEventRecordMixin):
    
    
    @property
    def sae_statistics(self):
        return dict(
            sae_overall_count=self.sae_overall,
            aei_overall=self.aei_overall,
            sae_received_first_dose_plus_28=self.sae_received_first_dose_plus_28,
            sae_received_second_dose=self.sae_received_second_dose,
            sae_related_ip=self.sae_related_ip,
            sae_not_related_ip=self.sae_not_related_ip,
            sae_hiv_infected=self.sae_hiv_infected,
            sae_received_first_dose=self.sae_received_first_dose,
            sae_overral_adverse_events=self.sae_overral_adverse_events,
            sae_hiv_uninfected=self.sae_hiv_uninfected,
        )
    
    @property
    def sae_statistics_preprocessor(self):
        stats = self.cache_preprocessor('sae_statistics')
        if stats:
            return stats
        else:
            return dict()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            all_sae_records=self.all_sae_records,
             **self.sae_statistics
            )
        return context

