
from django.apps import apps as django_apps
from django.db.models import Q
from django.contrib.sites.models import Site
from edc_base.view_mixins import EdcBaseViewMixin


class ScreeningReportsViewMixin(EdcBaseViewMixin):

    subject_screening_model = 'esr21_subject.eligibilityconfirmation'
    screening_eligibility_model = 'esr21_subject.screeningeligibility'
    eligibility_model = 'esr21_subject.eligibilityconfirmation'
    consent_model = 'esr21_subject.informedconsent'
    vaccination_model = 'esr21_subject.vaccinationdetails'
    screening_eligibility_model = 'esr21_subject.screeningeligibility'
    pregnancy_test_model = 'esr21_subject.pregnancytest'
    onschedule_model = 'esr21_subject.onschedule'

    @property
    def subject_screening_cls(self):
        return django_apps.get_model(self.subject_screening_model)

    @property
    def screening_eligibility_cls(self):
        return django_apps.get_model(self.screening_eligibility_model)

    @property
    def eligibility_model_cls(self):
        return django_apps.get_model(self.eligibility_model)

    @property
    def consent_model_cls(self):
        return django_apps.get_model(self.consent_model)

    @property
    def vaccination_model_cls(self):
        return django_apps.get_model(self.vaccination_model)

    @property
    def pregnancy_test_cls(self):
        return django_apps.get_model(self.pregnancy_test_model)

    @property
    def onschedule_model_cls(self):
        return django_apps.get_model(self.onschedule_model)

    @property
    def total_screened_participants(self):
        overall = self.eligibility_model_cls.objects.all().count()
        gaborone = self.get_screened_by_site('Gaborone')
        maun = self.get_screened_by_site('Maun')
        serowe = self.get_screened_by_site('Serowe')
        f_town = self.get_screened_by_site('Francistown')
        phikwe = self.get_screened_by_site('Phikwe')

        return [
            'Total screened', overall, gaborone, maun, serowe, f_town, phikwe]

    @property
    def total_screened(self):
        eligible_identifier = self.eligibility_model_cls.objects.filter(
            is_eligible=True).values_list('screening_identifier', flat=True)
        eligible_identifier = list(set(eligible_identifier))

        consent_screening_ids = self.consent_model_cls.objects.all().values_list(
            'screening_identifier', flat=True)
        consent_screening_ids = list(set(consent_screening_ids))
        no_consent_screenigs = list(set(eligible_identifier) - set(consent_screening_ids))

        total_screened = self.eligibility_model_cls.objects.filter(
            ~Q(screening_identifier__in=no_consent_screenigs))
        return total_screened

    @property
    def screening_failure(self):
        all_screening_ids = self.total_screened.values_list(
            'screening_identifier', flat=True)
        all_screening_ids = list(set(all_screening_ids))

        vaccination = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='first_dose') |
            Q(received_dose_before='second_dose')).values_list(
                'subject_visit__subject_identifier', flat=True)
        vaccination = list(set(vaccination))

        passed_screening = self.consent_model_cls.objects.filter(
            subject_identifier__in=vaccination).values_list(
                'screening_identifier', flat=True)
        passed_screening = list(set(passed_screening))

        failed = self.total_screened.filter(
            ~Q(screening_identifier__in=passed_screening)).count()

        gaborone = self.total_screened.filter(
            ~Q(screening_identifier__in=passed_screening) &
            Q(site_id=self.get_site_id('Gaborone'))).count()

        maun = self.total_screened.filter(
            ~Q(screening_identifier__in=passed_screening) &
            Q(site_id=self.get_site_id('Maun'))).count()

        serowe = self.total_screened.filter(
            ~Q(screening_identifier__in=passed_screening) &
            Q(site_id=self.get_site_id('Serowe'))).count()

        francistown = self.total_screened.filter(
            ~Q(screening_identifier__in=passed_screening) &
            Q(site_id=self.get_site_id('Francistown'))).count()

        phikwe = self.total_screened.filter(
            ~Q(screening_identifier__in=passed_screening)
            & Q(site_id=self.get_site_id('Phikwe'))).count()

        data = ['Screening failure', failed, gaborone, maun, serowe,
                francistown, phikwe]
        return data

    @property
    def screening_failure_reasons(self):
        all_screening_ids = self.total_screened.values_list(
            'screening_identifier', flat=True)
        all_screening_ids = list(set(all_screening_ids))

        vaccination = self.vaccination_model_cls.objects.filter(
            Q(received_dose_before='first_dose') |
            Q(received_dose_before='second_dose')).values_list(
                'subject_visit__subject_identifier', flat=True)
        vaccination = list(set(vaccination))

        passed_screening = self.consent_model_cls.objects.filter(
            subject_identifier__in=vaccination).values_list(
                'screening_identifier', flat=True)
        passed_screening = list(set(passed_screening))
        failed = self.total_screened.filter(
            ~Q(screening_identifier__in=passed_screening))

        data = []
        for fail in failed:
            if not fail.is_eligible:
                data.append([fail.site_id, fail.ineligibility])
            else:
                try:
                    consent = self.consent_model_cls.objects.get(
                        screening_identifier=fail.screening_identifier)
                except self.consent_model_cls.DoesNotExist:
                    print('Mising consent ****************')
                else:
                    try:
                        second_screening = self.screening_eligibility_cls.objects.get(
                            subject_identifier=consent.subject_identifier)
                    except self.screening_eligibility_cls.DoesNotExist:
                        pass
                    else:
                        if not second_screening.is_eligible:
                            data.append([fail.site_id, second_screening.ineligibility])
                        else:
                            if second_screening.symptomatic_infections_experiences == 'Yes':
                                data.append([fail.site_id, 'symptomatic infections experiences'])
                            try:
                                self.pregnancy_test_cls.objects.get(
                                    subject_visit__subject_identifier=second_screening.subject_identifier,
                                    result='POS')
                            except self.pregnancy_test_cls.DoesNotExist:
                                pass
                            else:
                                data.append([fail.site_id, 'Pregnant'])
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            screening_data=self.total_screened_participants,
        )
        return context

    def get_site_id(self, site_name_postfix):
        try:
            return Site.objects.get(name__endswith=site_name_postfix).id
        except Site.DoesNotExist:
            pass

    def get_screened_by_site(self, site_name_postfix):
        site_id = self.get_site_id(site_name_postfix)
        if site_id:
            return self.subject_screening_cls.objects.filter(site_id=site_id).count()

    def get_enrolled_by_site(self, site_name_postfix):
        site_id = self.get_site_id(site_name_postfix)
        if site_id:
            return self.vaccination_model_cls.objects.filter(
                received_dose_before='first_dose',
                site_id=site_id).values_list(
                'subject_visit__subject_identifier', flat=True)
