import json
from django.apps import apps as django_apps
from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from esr21_reports.models import DashboardStatistics
from .adverse_events import (
    AdverseEventRecordViewMixin, SeriousAdverseEventRecordViewMixin)
from .site_helper_mixin import SiteHelperMixin

class PSRTView(SiteHelperMixin,
               AdverseEventRecordViewMixin,
               SeriousAdverseEventRecordViewMixin,
               NavbarViewMixin, EdcBaseViewMixin, TemplateView):
    template_name = 'esr21_reports/psrt_report.html'
    navbar_selected_item = 'PSRT Reports'
    navbar_name = 'esr21_reports'

   
    ae_model = 'esr21_subject.adverseeventrecord'
    sae_model = 'esr21_subject.seriousadverseeventrecord'
    siae_model = 'esr21_subject.specialinterestadverseeventrecord'
    offstudy_model = 'esr21_prn.subjectoffstudy'
    
    def cache_preprocessor(self, key):
        statistics = None
        
        try:
            dashboard_statistics = DashboardStatistics.objects.get(key=key)
        except DashboardStatistics.DoesNotExist:
            pass
        else:
            statistics =  json.loads(dashboard_statistics.value)
        
        return statistics



    @property
    def ae_cls(self):
        return django_apps.get_model(self.ae_model)

    @property
    def sae_cls(self):
        return django_apps.get_model(self.sae_model)

    @property
    def siae_cls(self):
        return django_apps.get_model(self.siae_model)

    @property
    def offstudy_cls(self):
        return django_apps.get_model(self.offstudy_model)

  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
