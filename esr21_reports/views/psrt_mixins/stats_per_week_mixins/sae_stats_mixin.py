from django.apps import apps as django_apps


class SeriousAdverseEventStatsMixin:
    
    sae_model = 'esr21_subject.seriousadverseeventrecord'
    
    @property
    def sae_model_cls(self):
        return django_apps.get_model(self.sae_model)
    
    def weekly_saes_stats(self, start_week_date, end_week_date):
        stats = [f'{start_week_date} to {end_week_date}']
        overall_stats = self.count_overall_sae_stats_by_week(start_week_date, end_week_date)
        if overall_stats > 0:
            stats.append(overall_stats)
            for site_name in self.sites_names:
                    site_stats = self.count_sae_stats_by_week(site_name, start_week_date, end_week_date)
                    stats.append(site_stats)
            return stats
        return None
    
    def count_sae_stats_by_week(self, site_name_postfix, start_date, end_date):
        model_cls = 'sae_model_cls'
        return self.count_stats_by_week(model_cls, site_name_postfix, start_date, end_date)
    
    def count_overall_sae_stats_by_week(self, start_date, end_date):
        model_cls = 'sae_model_cls'
        return self.count_overall_stats_by_week(model_cls, start_date, end_date)
    
    @property
    def all_sae(self):
        return self.sae_model_cls.objects.count()
    
    @property
    def overall_sae_stats(self):
        overall_stats = []
        for week_date in self.weekly_dates:
            start_week_date =week_date[0]
            end_week_date = week_date[1]
            weekly_site_stats = self.weekly_saes_stats(start_week_date,end_week_date)
            if weekly_site_stats:
                overall_stats.append(weekly_site_stats)
                
        return overall_stats