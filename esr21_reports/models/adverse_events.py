from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class AdverseEventsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class AdverseEvents(BaseUuidModel):

    objects = AdverseEventsManager()

    site = models.CharField(
        verbose_name='Site',
        max_length=150,
        unique=True
    )

    ae = models.PositiveIntegerField(
        verbose_name='Adverse Event',
        default=0
    )

    serious_ae = models.PositiveIntegerField(
        verbose_name='Serious Adverse Event',
        default=0
    )

    special_ae = models.PositiveIntegerField(
        verbose_name='Special Interest Adverse Event',
        default=0
    )

    total = models.PositiveIntegerField(
        verbose_name='Total Adverse Events',
        default=0
    )

    series = models.CharField(
        verbose_name='Series',
        max_length=150,
    )
