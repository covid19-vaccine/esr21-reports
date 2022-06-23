import configparser
from datetime import datetime, timezone
import json
import threading
from django.core.management import call_command
from django.core.mail import send_mail
from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
from django.conf import settings
from esr21_reports.models import DashboardStatistics
from .enrollment_report_mixin import EnrollmentReportMixin
from .site_helper_mixin import SiteHelperMixin
from .adverse_events import (
    AdverseEventRecordViewMixin,
    SeriousAdverseEventRecordViewMixin)
from .psrt_mixins import (
    DemographicsMixin,
    ScreeningReportsViewMixin)


class HomeView(
            AdverseEventRecordViewMixin,
            SeriousAdverseEventRecordViewMixin,
            SiteHelperMixin,
            ScreeningReportsViewMixin,
            EnrollmentReportMixin,
            DemographicsMixin,
            NavbarViewMixin,
            EdcBaseViewMixin,
            TemplateView):
    template_name = 'esr21_reports/home.html'
    navbar_selected_item = 'Reports'
    navbar_name = 'esr21_reports'
    lock = threading.Lock()
    is_loading = False
    user_generation_data = None
    message = ''
    
    # @staticmethod
    def generate_reports(self):
        
        if HomeView.lock.locked():
            return
        
        HomeView.lock.acquire()
        HomeView.is_loading = True
        HomeView.user_generation_data = self.request.user.username
        call_command('populate_graphs')
        
        config = configparser.ConfigParser()
        config.read('/etc/esr21/esr21.ini')
        
        send_mail(
            subject="Report generation notification",
            message=f"""\
                Good day,
                
                Report generation you initiated has been completed successfully.
                
                Click here to access the reports {self.request.path_info}
                
                Best regards
                
                Esr21Bot
                
                """,
                recipient_list= [self.request.user.email,],
                from_email=config['email_conf'].get('email_user')
        )
        

        
        HomeView.lock.release()
    
    
    def post(self, request, *args, **kwargs):
        generate = request.POST.get('generate', None)
        
        updated_time_difference = datetime.now(timezone.utc) -  self.last_updated_at
        
        if generate and updated_time_difference.seconds > 10:
            thread = threading.Thread(target=self.generate_reports, daemon=True)
            thread.start()
        
        return super().get(request, *args, **kwargs)

    def cache_preprocessor(self, key):
        statistics = None
        try:
            dashboard_statistics = DashboardStatistics.objects.get(key=key)
        except DashboardStatistics.DoesNotExist:
            pass
        else:
            statistics = json.loads(dashboard_statistics.value)
        return statistics

    @property
    def last_updated_at(self):
        try:
            dashboard_statistics = DashboardStatistics.objects.latest('modified')
        except DashboardStatistics.DoesNotExist:
            pass
        else:
            return dashboard_statistics.modified

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update(
            updated_at=self.last_updated_at,
            is_loading = HomeView.lock.locked(), 
            user_generation_data = HomeView.user_generation_data
        )
        return context
