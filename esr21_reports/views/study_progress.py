from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin


class StudyProgressView(NavbarViewMixin, EdcBaseViewMixin, TemplateView):
    template_name = 'esr21_reports/study_progress_report.html'
    navbar_selected_item = 'Study Progress'
    navbar_name = 'esr21_reports'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
