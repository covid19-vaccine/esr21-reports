from django.contrib import admin
from django.urls import path

from .views import (HomeView, PSRTView, GraphsView, LabView)

from .views import line_chart, line_chart_json


app_name = 'esr21_reports'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='esr21_reports_home_url'),
    path('psrt', PSRTView.as_view(), name='esr21_psrt_report_url'),
    path('graphs', GraphsView.as_view(), name='esr21_graphs_report_url',),
    path('lab', LabView.as_view(), name='esr21_lab_report_url'),
    path('chart', line_chart, name='line_chart_url'),
    path('chartJSON', line_chart_json, name='line_chart_json_url'),    

]
