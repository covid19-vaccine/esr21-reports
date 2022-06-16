from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class GraphStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class GraphStatistics(BaseUuidModel):

    category = models.CharField(
        verbose_name='Category',
        max_length=150,
    )

    variable = models.CharField(
        verbose_name='Variable',
        max_length=150,
    )

    category = models.PositiveIntegerField(
        verbose_name='overall',
    )

    gaborone = models.PositiveIntegerField(
        verbose_name='Gaborone',
    )

    maun = models.PositiveIntegerField(
        verbose_name='Maun',
    )

    serowe = models.PositiveIntegerField(
        verbose_name='Serowe',
    )

    phikwe = models.PositiveIntegerField(
        verbose_name='Phikwe',
    )

    f_town = models.PositiveIntegerField(
        verbose_name='Francistown',
    )
