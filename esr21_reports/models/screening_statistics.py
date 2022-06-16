from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class ScreeningStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class ScreeningStatistics(BaseUuidModel):

    objects = ScreeningStatisticsManager()

    site = models.CharField(
        verbose_name='Site',
        max_length=150,
        unique=True
    )

    passed = models.PositiveIntegerField(
        verbose_name='Passed Screening',
        default=0
    )

    failed = models.PositiveIntegerField(
        verbose_name='Failed Screening',
        default=0
    )
