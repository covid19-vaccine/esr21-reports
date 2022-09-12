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
        unique=True,
    )

    dose1 = models.PositiveIntegerField(
        verbose_name='First dose screening',
    )

    dose2 = models.PositiveIntegerField(
        verbose_name='Second dose screening',
    )

    dose3 = models.PositiveIntegerField(
        verbose_name='Booster dose screening',
    )

    totals = models.PositiveIntegerField(
        verbose_name='Total dose screening',)
