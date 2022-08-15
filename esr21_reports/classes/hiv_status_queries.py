from django.apps import apps as django_apps
from django.db.models import Q
from edc_constants.constants import NEG, YES, OPEN

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

        for enrol in self.overall_enrols:
            assign = self.site_issue_assign_opts.get(enrol.site.id)
            hiv_test = self.rapid_hiv_status_cls.objects.filter(
                Q(hiv_testing_consent=YES) | Q(prev_hiv_test=YES),
                subject_visit=enrol.subject_visit,
                hiv_result__isnull=True,
                rapid_test_result__isnull=True)
            if hiv_test:
                self.create_action_item(
                    site=enrol.site,
                    subject_identifier=enrol.subject_visit.subject_identifier,
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
                   'medical history form at visit %(visits)s. This needs '
                   'to be corrected/recaptured on the system')
        query = self.create_query_name(
            query_name='Participant\'s HIV test result is missing.')

        hiv_neg = self.rapid_hiv_status_cls.objects.filter(
            Q(hiv_result=NEG) | Q(rapid_test_result=NEG),
            site_id=self.site_id)

        neg_art = {}

        for test in hiv_neg:
            medical_history = self.medical_history_cls.objects.filter(
                subject_visit=test.subject_visit)

            med_hiv = medical_history.filter(comorbidities__name__in=['HIV'])

            if med_hiv:
                subject_identifier = med_hiv[0].subject_visit.subject_identifier
                visit_code = med_hiv[0].subject_visit.visit_code
                visit_code_sequence = med_hiv[0].subject_visit.visit_code_sequence

                art_visits = neg_art.get(subject_identifier, [])
                assign = self.site_issue_assign_opts.get(med_hiv[0].site.id)

                art_visits.append(f'{visit_code}.{visit_code_sequence}')
                neg_art.update({f'{subject_identifier}': art_visits})
                # create action item
                self.create_action_item(
                    site=med_hiv[0].site,
                    subject_identifier=subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    status=OPEN,
                    subject=subject,
                    comment=comment % {'visits': ', '.join(art_visits), })
            else:
                try:
                    latest_med = medical_history.latest('report_datetime')
                except self.medical_history_cls.DoesNotExist:
                    pass
                else:
                    med_art = latest_med.medicaldiagnosis_set.filter(
                        rel_conc_meds__icontains='ARV')
                    if med_art:
                        subject_identifier = latest_med.subject_visit.subject_identifier
                        visit_code = latest_med.subject_visit.visit_code
                        visit_code_sequence = latest_med.subject_visit.visit_code_sequence
                        art_visits.append(f'{visit_code}.{visit_code_sequence}')
                        neg_art.update({f'{subject_identifier}': art_visits})
                        # create action item
                        self.create_action_item(
                            site=latest_med.site,
                            subject_identifier=subject_identifier,
                            query_name=query.query_name,
                            assign=assign,
                            status=OPEN,
                            subject=subject,
                            comment=comment % {
                                'visits': ', '.join(art_visits)})
