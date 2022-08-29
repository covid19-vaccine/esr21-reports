from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class DemographicsStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class DemographicsStatistics(BaseUuidModel):

    objects = DemographicsStatisticsManager()

    site_series = models.CharField(
        verbose_name='Site Series',
        max_length=150,
        unique=True
    )

    site = models.CharField(
        verbose_name='Site',
        max_length=150,
    )

    male = models.PositiveIntegerField(
        verbose_name='Male totals',
    )

    female = models.PositiveIntegerField(
        verbose_name='Female totals',
    )

    hiv_pos = models.PositiveIntegerField(
        verbose_name='HIV positive totals',
    )

    hiv_neg = models.PositiveIntegerField(
        verbose_name='HIV negative totals',
    )

    hiv_ind = models.PositiveIntegerField(
        verbose_name='HIV indeterminate totals',)

    pos_preg = models.PositiveIntegerField(
        verbose_name='Positive pregnancy',)

    pos_covid = models.PositiveIntegerField(
        verbose_name='Positive covid totals',)

    pos_diabetes = models.PositiveIntegerField(
        verbose_name='Positive diabetes',)

    series = models.CharField(
        verbose_name='Series',
        max_length=150,
    )
