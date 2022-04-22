from django.apps import apps as django_apps
from django.db.models import Q

from edc_appointment.constants import COMPLETE_APPT


class QueryGeneration:

    vaccination_details_model = 'esr21_subject.vaccinationdetails'
    ae_model = 'esr21_subject.adverseeventrecord'
    demographics_data_model = 'esr21_subject.demographicsdata'
    screening_eligibility_model = 'esr21_subject.screeningeligibility'
    eligibility_confirmation_model = 'esr21_subject.eligibilityconfirmation'
    informed_consent_model = 'esr21_subject.informedconsent'
    subject_visit_model = 'esr21_subject.subjectvisit'

    @property
    def consent_model_cls(self):
        return django_apps.get_model(self.informed_consent_model)

    @property
    def screening_eligibility_cls(self):
        return django_apps.get_model(self.screening_eligibility_model)

    @property
    def eligibility_confirmation_cls(self):
        return django_apps.get_model(self.eligibility_confirmation_model)

    @property
    def demographics_data_cls(self):
        return django_apps.get_model(self.demographics_data_model)

    @property
    def ae_model_cls(self):
        return django_apps.get_model(self.ae_model)

    @property
    def vaccination_details_cls(self):
        return django_apps.get_model(self.vaccination_details_model)
    
    @property
    def subject_visit_cls(self):
        return django_apps.get_model(self.subject_visit_model)

    @property
    def query_name(self):
        return django_apps.get_model('edc_data_manager.queryname')

    @property
    def action_item_cls(self):
        return django_apps.get_model('edc_data_manager.dataactionitem')

    def create_query_name(self, query_name=None):
        query = None
        try:
            query = self.query_name.objects.get(query_name=query_name)
        except self.query_name.DoesNotExist:
            query = self.query_name.objects.create(query_name=query_name)
        return query

    @property
    def site_issue_assign_opts(self):
        options = {
            40: 'gabs_clinic',
            41: 'maun_clinic',
            42: 'serowe_clinic',
            43: 'gheto_clinic',
            44: 'sphikwe_clinic',
        }
        return options

    def create_action_item(
            self, site=None, subject_identifier=None, query_name=None,
            assign=None, subject=None, comment=None):
        try:
            self.action_item_cls.objects.get(
                subject_identifier=subject_identifier,
                query_name=query_name
            )
        except self.action_item_cls.DoesNotExist:
            self.action_item_cls.objects.create(
                subject_identifier=subject_identifier,
                query_name=query_name,
                assigned=assign,
                subject=subject,
                comment=comment,
                site=site
            )

    def check_appt_status(self, required_crf=None):
        appointment_model_cls = django_apps.get_model(
            required_crf.schedule.appointment_model)
        try:
            appt = appointment_model_cls.objects.get(
                subject_identifier=required_crf.subject_identifier,
                visit_code=required_crf.visit_code,
                visit_code_sequence=required_crf.visit_code_sequence,
                schedule_name=required_crf.schedule_name)
        except appointment_model_cls.DoesNotExist:
            return False
        else:
            return False if appt.appt_status == COMPLETE_APPT else True
        
    def check_visit_status(self, required_crf=None):        
        try:
            sv = self.subject_visit_cls.objects.get(
            subject_identifier=required_crf.subject_identifier,
            visit_code=required_crf.visit_code)
            
        except self.subject_visit_cls.DoesNotExist: 
            pass
        else:
            return False if sv.reason == 'missed' else True
   

    @property
    def first_dose_second_dose_missing(self):
        """
        First dose missing and second dose not missing
        """
        subject = "Missing first dose data",
        comment = "The data for the fist dose for the participant is missing."\
                  " This needs to be recaptured on the system"
        query = self.create_query_name(
            query_name='Missing First Dose Data')
        first_dose = self.vaccination_details_cls.objects.filter(
            Q(received_dose_before='first_dose')).distinct().values_list(
            'subject_visit__subject_identifier', flat=True)

        second_doses = self.vaccination_details_cls.objects.filter(
            Q(received_dose_before='second_dose') &
            ~Q(subject_visit__subject_identifier__in=first_dose))
        for sec_dose in second_doses:
            assign = self.site_issue_assign_opts.get(sec_dose.site.id)
            self.create_action_item(
                site=sec_dose.site,
                subject_identifier=sec_dose.subject_visit.subject_identifier,
                query_name=query.query_name,
                assign=assign,
                subject=subject,
                comment=comment
            )

    @property
    def ae_data_issues(self):
        """
        AE start date is before first dose
        """
        query = self.create_query_name(
            query_name='AE start date before first dose')
        subject = "The adverse even start date is before the first dose."
        comment = "The participant adverse even start date is before" \
                  " the participant was vaccinated"
        aes = self.ae_model_cls.objects.all().values_list(
            'adverse_event__subject_visit__subject_identifier', 'start_date')
        for ae in aes:
            subject_identifier = ae[0]
            ae_start_date = ae[1]
            try:
                vaccination = self.vaccination_details_cls.objects.get(
                    Q(received_dose_before='first_dose') &
                    Q(subject_visit__subject_identifier=subject_identifier) &
                    Q(vaccination_date__date__gt=ae_start_date))
            except self.vaccination_details_cls.DoesNotExist:
                pass
            else:
                assign = self.site_issue_assign_opts.get(vaccination.site.id)
                self.create_action_item(
                    site=vaccination.site,
                    subject_identifier=vaccination.subject_visit.subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    subject=subject,
                    comment=comment
                )

    @property
    def missing_visit_forms(self):
        """
        Not on demographic data
        need to update to remove participants who missed their visits
        """
        crfmetadata = django_apps.get_model('edc_metadata.crfmetadata')
        query = self.create_query_name(
            query_name='Missing Visit Forms data')
        enrolled_identifiers = self.vaccination_details_cls.objects.all().values_list(
            'subject_visit__subject_identifier', flat=True)
        enrolled_identifiers = list(set(enrolled_identifiers))
        required_crfs = crfmetadata.objects.filter(
            subject_identifier__in=enrolled_identifiers, entry_status='REQUIRED')
        data = [(qs.subject_identifier, qs.schedule_name, qs.visit_code,
                 qs.visit_code_sequence, qs.verbose_name) for qs in required_crfs if self.check_appt_status(qs)]
        for missing_crf in required_crfs:
            assign = self.site_issue_assign_opts.get(missing_crf.site.id)
            model = missing_crf.model
            model = model.split('.')[1]
            subject = f"Participant is missing {model} data for visit {missing_crf.visit_code}."
            comment = subject + " Please complete the missing data for the form"
            self.create_action_item(
                site=missing_crf.site,
                subject_identifier=missing_crf.subject_identifier,
                query_name=query.query_name,
                assign=assign,
                subject=subject,
                comment=comment
            )

        
    @property
    def male_child_bearing_potential(self):
        """
        Male and child bearing potential is Yes
        """
        query = self.create_query_name(
            query_name='Male with child bearing potential')
        subject = 'Male participant with child bearing potential.'
        comment = subject + ' Please correct an update the screening accordingly'
        male_consents = self.consent_model_cls.objects.filter(
            gender='M').values_list('subject_identifier', flat=True)
        screening_eligibility = self.screening_eligibility_cls.objects.filter(
            Q(subject_identifier__in=male_consents) &
            Q(childbearing_potential='Yes'))
        for eligibility in screening_eligibility:
            assign = self.site_issue_assign_opts.get(eligibility.site.id)
            self.create_action_item(
                site=eligibility.site,
                subject_identifier=eligibility.subject_identifier,
                query_name=query.query_name,
                assign=assign,
                subject=subject,
                comment=comment
            )

    @property
    def ineligible_vaccinated_participant(self):
        """
        participant vaccinated but ineligible
        """
        query = self.create_query_name(
            query_name='Ineligible Vaccinated Participants')
        subject = 'Participant who is not eligible but has been vaccinated.'
        comment = subject + ' Please re evaluate the screening criteria'
        not_eligible = []
        screening_identifiers = self.eligibility_confirmation_cls.objects.filter(
            is_eligible=False).values_list('screening_identifier', flat=True)
        consented_ineligible = self.consent_model_cls.objects.filter(
            screening_identifier__in=screening_identifiers).values_list('subject_identifier', flat=True)
        participant_list = self.vaccination_details_cls.objects.filter(
            Q(subject_visit__subject_identifier__in=consented_ineligible))
        for ineligibles in participant_list:
            assign = self.site_issue_assign_opts.get(ineligibles.site.id)
            self.create_action_item(
                site=ineligibles.site,
                subject_identifier=ineligibles.subject_visit.subject_identifier,
                query_name=query.query_name,
                assign=assign,
                subject=subject,
                comment=comment
            )
