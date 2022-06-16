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

    dose_1_percent = models.FloatField(
        verbose_name='First Dose Percentage',
        default=0
    )

    dose_2_percent = models.FloatField(
        verbose_name='Second Dose Percentage',
        default=0
    )

    dose_3_percent = models.FloatField(
        verbose_name='Booster Dose Percentage',
        default=0
    )

    overall_percent = models.FloatField(
        verbose_name='Overall Percentage',
        default=0
    )
