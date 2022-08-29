from django.db import models
from edc_search.model_mixins import SearchSlugManager
from edc_base.model_mixins import BaseUuidModel


class VaccinationEnrollmentsManager(SearchSlugManager, models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class VaccinationEnrollments(BaseUuidModel):

    objects = VaccinationEnrollmentsManager()

    site_series = models.CharField(
        verbose_name='Site Series',
        max_length=150,
        unique=True
    )

    variable = models.CharField(
        verbose_name='Variable',
        max_length=150,
    )

    janssen = models.PositiveIntegerField(
        verbose_name='Janssen Enrollments',
        default=0
    )

    sinovac = models.PositiveIntegerField(
        verbose_name='Sinovac Enrollments',
        default=0
    )

    pfizer = models.PositiveIntegerField(
        verbose_name='Pfizer Enrollments',
        default=0
    )

    moderna = models.PositiveIntegerField(
        verbose_name='Moderna Enrollments',
        default=0
    )

    astrazeneca = models.PositiveIntegerField(
        verbose_name='Astrazeneca Enrollments',
        default=0
    )

    months = models.TextField()

    totals = models.PositiveIntegerField(
        verbose_name='Total dose screening',)

    series = models.CharField(
        verbose_name='Series',
        max_length=150,
    )
