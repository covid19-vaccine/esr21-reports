from django.conf import settings

from edc_navbar import NavbarItem, site_navbars, Navbar

esr21_reports = Navbar(name='esr21_reports')

no_url_namespace = True if settings.APP_NAME == 'esr21_reports' else False

esr21_reports.append_item(
    NavbarItem(name='Reports',
               label='Reports',
               fa_icon='fa-home',
               url_name='esr21_reports:esr21_reports_home_url'))

esr21_reports.append_item(
    NavbarItem(name='Study Progress Reports',
               label='Study Progress Reports',
               fa_icon='fa-chart-pie',
               url_name='esr21_reports:esr21_study_progress_report_url'))

esr21_reports.append_item(
    NavbarItem(name='Graphs Reports',
               label='Graphs Reports',
               fa_icon='fa-chart-bar',
               url_name='esr21_reports:esr21_graphs_report_url'))

esr21_reports.append_item(
    NavbarItem(name='Lab Reports',
               label='Lab Reports',
               fa_icon='fa-flask',
               url_name='esr21_reports:esr21_lab_report_url'))

esr21_reports.append_item(
    NavbarItem(name='PSRT Reports',
               label='PSRT Reports',
               fa_icon='fa-file',
               url_name='esr21_reports:esr21_psrt_report_url'))

site_navbars.register(esr21_reports)
