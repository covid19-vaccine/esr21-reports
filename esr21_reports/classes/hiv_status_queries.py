from django.apps import apps as django_apps
from django.db.models import Q
from edc_constants.constants import POS, YES, OPEN

from .query_generation import QueryGeneration


class HIVStatusQueries(QueryGeneration):

    rapid_hiv_status_model = 'esr21_subject.rapidhivtesting'

    @property
    def rapid_hiv_status_cls(self):
        return django_apps.get_model(self.rapid_hiv_status_model)

    def missing_hiv_test_results(self):
        """
        Participant's HIV test result status missing, i.e. rapid HIV test not
        performed and/or previous HIV status not keyed...
        """
        subject = 'Participant\'s HIV test result is missing.',
        comment = ('Participant\'s HIV test status is missing. This needs to '
                   'be corrected/recaptured on the system')
        query = self.create_query_name(
            query_name='Participant\'s HIV test result is missing.')

        for idx in self.overall_enrols:
            enrol_visit = self.subject_visit_cls.objects.filter(
                subject_identifier=idx, ).earliest(
                    'report_datetime')
            assign = self.site_issue_assign_opts.get(enrol_visit.site.id)
            hiv_test = self.rapid_hiv_status_cls.objects.filter(
                Q(hiv_testing_consent=YES) | Q(prev_hiv_test=YES),
                subject_visit=enrol_visit,
                hiv_result__isnull=True,
                rapid_test_result__isnull=True)
            if hiv_test:
                self.create_action_item(
                    site=enrol_visit.site,
                    subject_identifier=idx,
                    query_name=query.query_name,
                    assign=assign,
                    status=OPEN,
                    subject=subject,
                    comment=comment)

    def neg_hiv_status_on_art(self):
        """
        Participant's HIV status is negative, but is on ART.
        """
        subject = 'Participant has negative HIV test status, but is on ART.',
        comment = ('Participant\'s HIV test status is negative, but has ART '
                   'medication or HIV selected on the comorbidities for the '
                   'medical history form at visit %(visit)s. This needs to be '
                   'corrected/recaptured on the system')
        query = self.create_query_name(
            query_name='Participant\'s HIV test result is missing.')

        hiv_pos = self.rapid_hiv_status_cls.objects.filter(
            Q(hiv_result=POS) | Q(rapid_test_result=POS),
            site_id=self.site_id).values_list(
                'subject_visit__subject_identifier', flat=True).distinct()

        medical_history = self.medical_history_cls.objects.filter(
                comorbidities__name__in=['HIV']).exclude(
                    subject_visit__subject_identifier__in=hiv_pos)

        for history in medical_history:
            subject_identifier = history.subject_visit.subject_identifier

            assign = self.site_issue_assign_opts.get(history.site.id)

            # create action item
            self.create_action_item(
                site=history.site,
                subject_identifier=subject_identifier,
                query_name=query.query_name,
                assign=assign,
                status=OPEN,
                subject=subject,
                comment=comment % {'visit': history.subject_visit.visit_code})
