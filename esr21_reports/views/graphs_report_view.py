from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from .graphs_mixins import ScreeningGraphMixin, AgeDistributionGraphMixin, \
    EnrollmentGraphMixin, VaccinationGraphMixin, Missed2ndDoseGraphMixin

from .site_helper_mixin import SiteHelperMixin


class GraphsView(
    SiteHelperMixin,
    ScreeningGraphMixin,
    AgeDistributionGraphMixin,
    EnrollmentGraphMixin,
    VaccinationGraphMixin,
    NavbarViewMixin,
    EdcBaseViewMixin,
    TemplateView):

    template_name = 'esr21_reports/graphs_report.html'
    navbar_selected_item = 'Graphs Reports'
    navbar_name = 'esr21_reports'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
