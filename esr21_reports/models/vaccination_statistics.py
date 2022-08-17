from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class VaccinationStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class VaccinationStatistics(BaseUuidModel):

    objects = VaccinationStatisticsManager()

    site = models.CharField(
        verbose_name='Site',
        max_length=150,
        unique=True
    )

    dose_1 = models.PositiveIntegerField(
        verbose_name='First dose total',
        default=0
    )

    dose_2 = models.PositiveIntegerField(
        verbose_name='Second dose total',
        default=0
    )

    dose_3 = models.PositiveIntegerField(
        verbose_name='Booster dose total',
        default=0
    )

    overall = models.PositiveIntegerField(
        verbose_name='Overall',
        default=0
    )

    series = models.CharField(
        verbose_name='Series',
        max_length=150,
    )
