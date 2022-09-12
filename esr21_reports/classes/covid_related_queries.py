from django.apps import apps as django_apps
from edc_constants.constants import NO, YES, OPEN

from .query_generation import QueryGeneration


class COVIDRelatedQueries(QueryGeneration):

    covid19infections_model = 'esr21_subject.covid19symptomaticinfections'
    covid_results_model = 'esr21_subject.covid19results'

    @property
    def covid19infections_cls(self):
        return django_apps.get_model(self.covid19infections_model)

    @property
    def covid19_results_cls(self):
        return django_apps.get_model(self.covid_results_model)

    def symptomaticinfections_missing(self):
        """
        Participant has covid19 results captured, but missing symptomatic
        infections form or did not experience any symptomatic infections; i.e.
        'symptomatic_experiences' => No.
        """

        """
        NOTE: exclude results from enrolment visits.
        """
        subject = 'Missing symptomatic infections data, but has PCR results. ',
        comment = ('Participant has PCR results and %(issue_description)s at '
                   'visit(s) %(visits)s. This needs to be corrected/recaptured'
                   ' on the system.')
        query = self.create_query_name(
            query_name='Missing symptomatic infections data, but has PCR results.')
        pcr_results = self.covid19_results_cls.objects.filter(site_id=self.site_id)

        enrol_visits = [enrol.subject_visit.id for enrol in self.overall_enrols]

        missing_infections = {}
        no_symptoms = {}

        for result in pcr_results:
            subject_identifier = result.subject_visit.subject_identifier
            visit_code = result.subject_visit.visit_code
            visit_code_sequence = result.subject_visit.visit_code_sequence

            missing_visits = missing_infections.get(subject_identifier, [])
            symptom_visits = no_symptoms.get(subject_identifier, [])
            try:
                covid_infections = self.covid19infections_cls.objects.get(
                    subject_visit=result.subject_visit)
            except self.covid19infections_cls.DoesNotExist:
                vaccinated = result.subject_visit.subject_identifier in self.vaccinations
                if vaccinated and not (result.subject_visit.id in enrol_visits):
                    missing_visits.append(f'{visit_code}.{visit_code_sequence}')
                    missing_infections.update({f'{subject_identifier}': missing_visits})
                    # create action item
                    assign = self.site_issue_assign_opts.get(result.site.id)
                    self.create_action_item(
                        site=result.site,
                        subject_identifier=subject_identifier,
                        query_name=query.query_name,
                        assign=assign,
                        status=OPEN,
                        subject=subject,
                        comment=comment % {
                            'issue_description': (
                                'missing covid19symptomatic infections form'),
                            'visits': ', '.join(missing_visits), })
            else:
                if covid_infections.symptomatic_experiences == NO:
                    symptom_visits.append(f'{visit_code}.{visit_code_sequence}')
                    no_symptoms.update({f'{subject_identifier}': symptom_visits})
                    # create action item
                    assign = self.site_issue_assign_opts.get(result.site.id)
                    self.create_action_item(
                        site=result.site,
                        subject_identifier=subject_identifier,
                        query_name=query.query_name,
                        assign=assign,
                        status=OPEN,
                        subject=subject,
                        comment=comment % {
                            'issue_description': (
                                'did not experience COVID symptoms for covid19symptomatic form'),
                            'visits': ', '.join(symptom_visits), })

    def pcr_results_missing(self):
        """
        Participant has symptomatic infections captured, but missing PCR
        requisitions and results at follow ups (excludes symptoms experienced
        7days after vaccination.
        """
        subject = ('Participant has symptomatic infections, but missing PCR '
                   'results and requisition data. '),
        comment = ('Participant has symptomatic infections and no PCR results '
                   'and PCR requisition data at visit(s) %(visits)s. This '
                   'needs to be corrected/recaptured on the system')
        query = self.create_query_name(
            query_name='Missing PCR result data, but has symptomatic infections.')
        infections = self.covid19infections_cls.objects.filter(
            symptomatic_experiences=YES, site_id=self.site_id)
        missing_pcr = {}

        for infection in infections:
            subject_identifier = infection.subject_visit.subject_identifier
            visit_code = infection.subject_visit.visit_code
            visit_code_sequence = infection.subject_visit.visit_code_sequence

            pcr_visits = missing_pcr.get(subject_identifier, [])
            try:
                self.covid19_results_cls.objects.get(
                    subject_visit=infection.subject_visit,)
            except self.covid19_results_cls.DoesNotExist:
                # account for reactogenicity, read pids and visit from file.
                pcr_visits.append(f'{visit_code}.{visit_code_sequence}')
                missing_pcr.update({f'{subject_identifier}': pcr_visits})
                # create action item
                assign = self.site_issue_assign_opts.get(infection.site.id)
                self.create_action_item(
                    site=infection.site,
                    subject_identifier=subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    status=OPEN,
                    subject=subject,
                    comment=comment % {
                        'visits': ', '.join(pcr_visits), })

    def no_infections_symptoms_specified(self):
        """
        Participant has no symptomatic infections, but the symptoms have been
        keyed.
        """
        subject = 'Participant did not experience COVID symptoms, but symptoms keyed.',
        comment = ('Participant did not experience COVID symptoms but their '
                   'symptoms have been captured at visit %(visits)s on the '
                   'covid19symptomatic infections form. This needs to be '
                   'corrected/recaptured on the system')
        query = self.create_query_name(
            query_name='Participant did not experience COVID symptoms, but symptoms keyed.')
        infections = self.covid19infections_cls.objects.filter(
            symptomatic_experiences=NO, symptomatic_infections__isnull=False,
            site_id=self.site_id)
        no_infections = {}

        for infection in infections:
            subject_identifier = infection.subject_visit.subject_identifier
            visit_code = infection.subject_visit.visit_code
            visit_code_sequence = infection.subject_visit.visit_code_sequence

            infection_visits = no_infections.get(subject_identifier, [])

            infection_visits.append(f'{visit_code}.{visit_code_sequence}')
            no_infections.update({f'{subject_identifier}': infection_visits})
            # create action item
            assign = self.site_issue_assign_opts.get(infection.site.id)
            self.create_action_item(
                    site=infection.site,
                    subject_identifier=infection.subject_visit.subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    status=OPEN,
                    subject=subject,
                    comment=comment % {
                        'visits': ', '.join(infection_visits), })

    def enrolment_covidsymptoms_pcr_missing(self):
        """
        Participant has COVID symptoms during screening, but missing PCR
        results before vaccination.
        """
        subject = 'Participant has COVID symptoms at screening, but no PCR results.',
        comment = ('Participant has COVID symptoms during screening, but missing'
                   ' PCR results before getting vaccinated at %(visits)s . '
                   'This needs to be corrected/recaptured on the system')
        query = self.create_query_name(
            query_name='Participant has COVID symptoms at screening, but no PCR results.')
        missing_pcr = {}

        for enrol in self.vaccinations:
            screening = self.screening_eligibility_cls.objects.filter(
                    subject_identifier=enrol,
                    symptomatic_infections_experiences=YES)
            if screening:
                enrol_vacc = self.vaccination_details_cls.objects.filter(
                    subject_visit__subject_identifier=enrol).earliest(
                        'vaccination_date')
                subject_identifier = enrol_vacc.subject_visit.subject_identifier
                visit_code = enrol_vacc.subject_visit.visit_code
                visit_code_sequence = enrol_vacc.subject_visit.visit_code_sequence

                pcr_visits = missing_pcr.get(subject_identifier, [])
                try:
                    self.covid19_results_cls.objects.get(
                        subject_visit=enrol_vacc.subject_visit)
                except self.covid19_results_cls.DoesNotExist:
                    pcr_visits.append(f'{visit_code}.{visit_code_sequence}')
                    missing_pcr.update({f'{subject_identifier}': pcr_visits})
                    # create action item
                    assign = self.site_issue_assign_opts.get(enrol_vacc.site.id)
                    self.create_action_item(
                            site=enrol_vacc.site,
                            subject_identifier=subject_identifier,
                            query_name=query.query_name,
                            assign=assign,
                            status=OPEN,
                            subject=subject,
                            comment=comment % {
                                'visits': ', '.join(pcr_visits), })

    @property
    def vaccinations(self):
        vaccinations = self.vaccination_details_cls.objects.filter(
            received_dose=YES, site=self.site_id).values_list(
                'subject_visit__subject_identifier', flat=True).distinct()
        return [vacc for vacc in vaccinations]
