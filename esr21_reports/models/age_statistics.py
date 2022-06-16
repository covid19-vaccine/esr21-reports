from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class AgeStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class AgeStatistics(BaseUuidModel):

    objects = AgeStatisticsManager()

    site = models.CharField(
        verbose_name='Site',
        max_length=150,
        unique=True
    )

    min = models.PositiveIntegerField(
        verbose_name='min',
        default=0
    )

    lowerquartile = models.PositiveIntegerField(
        verbose_name='Lowerquartile',
        default=0
    )

    median = models.PositiveIntegerField(
        verbose_name='Median',
        default=0
    )

    upperquartile = models.PositiveIntegerField(
        verbose_name='Upperquartile',
        default=0
    )

    max = models.PositiveIntegerField(
        verbose_name='Max',
        default=0
    )

    outlier = models.PositiveIntegerField(
        verbose_name='Outliers',
        default=0
    )
