from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class TotalStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class TotalStatistics(BaseUuidModel):

    screening = models.CharField(
        verbose_name='Screening totals',
        max_length=150,
    )

    first_dose = models.PositiveIntegerField(
        verbose_name='First dose totals',
    )

    second_dose = models.PositiveIntegerField(
        verbose_name='Second dose totals',
    )

    booster_dose = models.PositiveIntegerField(
        verbose_name='Booster dose totals',
    )

    adverse_event = models.PositiveIntegerField(
        verbose_name='Adverse event totals',
    )

    serious_adverse_event = models.PositiveIntegerField(
        verbose_name='Serious adverse event totals',
    )

    ae_special_interest = models.PositiveIntegerField(
        verbose_name='AE special interest totals',
    )
