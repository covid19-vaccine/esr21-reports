import pandas as pd
from edc_base.view_mixins import EdcBaseViewMixin
from datetime import datetime,timedelta
from django.db.models import Q
from .stats_per_week_mixins import (EnrollmentStatsMixin,
                                    PregnancyStatsMixin,
                                    SecondDoseStatsMixins,
                                    SeriousAdverseEventStatsMixin,
                                    AESpecialInterestStatsMixin,
                                    AdverseEventStatsMixin)


class StatsPerWeekMixin(EnrollmentStatsMixin,
                        PregnancyStatsMixin,
                        AdverseEventStatsMixin,
                        SecondDoseStatsMixins,
                        SeriousAdverseEventStatsMixin,
                        AESpecialInterestStatsMixin,
                        EdcBaseViewMixin):
    @property
    def weekly_dates(self):
        vaccination = self.vaccination_model_cls.objects.filter(
            received_dose_before='first_dose').earliest('created')
        vaccination_date = vaccination.vaccination_date
        
        study_current_datetime = datetime.now().date()
            
        study_open_datetime = vaccination_date.date()        
        
        week_pair_dates = []
        while study_open_datetime != study_current_datetime:
            study_open_datetime += timedelta(days=1)
            if study_open_datetime.weekday() == 6:
                start_week = study_open_datetime - timedelta(days=6)
                end_week = study_open_datetime
                week_pair_dates.append((start_week,end_week))      
        return week_pair_dates
    
    
    def count_stats_by_week(self, model_cls, site_name_postfix, start_date, end_date):
        model_cls = getattr(self, model_cls)
        site_id = self.get_site_id(site_name_postfix)
        if site_id:
            aes = model_cls.objects.filter(
                 Q(start_date__lte=end_date) & Q(start_date__gte=start_date)
                 & Q(site_id=site_id))
        return aes.count()
    
    def count_overall_stats_by_week(self, model_cls, start_date, end_date):
        model_cls = getattr(self, model_cls)
        overall = model_cls.objects.filter(
                Q(start_date__lte=end_date) & Q(start_date__gte=start_date))
        return overall.count()

    @property
    def monthly_dates(self):
        weekly_dates = [_date.strftime('%Y/%m/%d') for week_pair_dates in self.weekly_dates for _date in week_pair_dates[:1]]
        s = pd.to_datetime(pd.Series(weekly_dates))
        s.index = s.dt.to_period('m')
        s = s.groupby(level=0).size()
        return s.items()
    
    def group_weekly_dates_by_month(self):
        pass


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            sites=self.sites_names,
            overall_enrollment_stats=self.overall_enrollment_stats,
            overall_pregnancy_stats=self.overall_pregnancy_stats,
            overall_ae_stats=self.overall_ae_stats,
            overall_sae_stats=self.overall_sae_stats,
            overall_aesi_stats=self.overall_aesi_stats,
            overall_second_dose_stats=self.overall_second_dose_stats,
            monthly_dates=self.monthly_dates,
            all_ae=self.all_ae,
            all_sae=self.all_sae,
            all_aesi=self.all_aesi,
        )
        return context
