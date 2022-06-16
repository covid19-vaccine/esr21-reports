from django.apps import apps as django_apps


class AdverseEventStatsMixin:
    
    ae_model = 'esr21_subject.adverseeventrecord'
    
    @property
    def ae_model_cls(self):
        return django_apps.get_model(self.ae_model)
    
    def weekly_aes_stats(self, start_week_date, end_week_date):
        stats = [f'{start_week_date} to {end_week_date}']
        overall_stats = self.count_overall_aes_stats_by_week(start_week_date, end_week_date)
        if overall_stats > 0:
            stats.append(overall_stats)
            for site_name in self.sites_names:
                    site_stats = self.count_aes_stats_by_week(site_name, start_week_date, end_week_date)
                    stats.append(site_stats)
            return stats
        return None

    def count_aes_stats_by_week(self, site_name_postfix, start_date, end_date):
        model_cls = 'ae_model_cls'
        return self.count_stats_by_week(model_cls, site_name_postfix, start_date, end_date)

    def count_overall_aes_stats_by_week(self, start_date, end_date):
        model_cls = 'ae_model_cls'
        return self.count_overall_stats_by_week(model_cls, start_date, end_date)

    @property
    def overall_ae_stats(self):
        overall_stats = []
        for week_date in self.weekly_dates:
            start_week_date =week_date[0]
            end_week_date = week_date[1]
            weekly_site_stats = self.weekly_aes_stats(start_week_date,end_week_date)
            if weekly_site_stats:
                overall_stats.append(weekly_site_stats)
        return overall_stats

    @property
    def all_ae(self):
        return self.ae_model_cls.objects.count()
