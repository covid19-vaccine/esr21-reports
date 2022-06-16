from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class EnrollmentStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class EnrollmentStatistics(BaseUuidModel):

    objects = EnrollmentStatisticsManager()

    site = models.CharField(
        verbose_name='Site',
        max_length=150,
        unique=True
    )

    total = models.PositiveIntegerField(
        verbose_name='Site Total Enrollment',
        default=0
    )

    male = models.PositiveIntegerField(
        verbose_name='Site Total Males',
        default=0
    )

    female = models.PositiveIntegerField(
        verbose_name='Site Total Females',
        default=0
    )
