from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class EnrollmentStatisticsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class EnrollmentStatistics(BaseUuidModel):

    objects = EnrollmentStatisticsManager()

    site_series = models.CharField(
        verbose_name='Site Series',
        max_length=150,
        unique=True
    )

    site = models.CharField(
        verbose_name='Site',
        max_length=150,
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

    main_cohort = models.CharField(
        verbose_name='Cohort',
        max_length=150,
    )

    sub_cohort = models.CharField(
        verbose_name='Cohort',
        max_length=150,
    )

    series = models.CharField(
        verbose_name='Series',
        max_length=150,
    )

    months = models.TextField()
