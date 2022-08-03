from django.apps import apps as django_apps
from django.db.models import Q

from edc_appointment.constants import NEW_APPT
from edc_constants.constants import OPEN, YES


class QueryGeneration:

    vaccination_details_model = 'esr21_subject.vaccinationdetails'
    vaccination_history_model = 'esr21_subject.vaccinationhistory'
    ae_model = 'esr21_subject.adverseeventrecord'
    demographics_data_model = 'esr21_subject.demographicsdata'
    screening_eligibility_model = 'esr21_subject.screeningeligibility'
    eligibility_confirmation_model = 'esr21_subject.eligibilityconfirmation'
    informed_consent_model = 'esr21_subject.informedconsent'
    medical_history_model = 'esr21_subject.medicalhistory'
    pregnancy_model = 'esr21_subject.pregnancystatus'

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
    def vaccination_history_cls(self):
        return django_apps.get_model(self.vaccination_history_model)

    @property
    def medical_history_cls(self):
        return django_apps.get_model(self.medical_history_model)

    @property
    def pregnancy_status_cls(self):
        return django_apps.get_model(self.pregnancy_model)

    @property
    def query_name_cls(self):
        return django_apps.get_model('edc_data_manager.queryname')

    @property
    def action_item_cls(self):
        return django_apps.get_model('edc_data_manager.dataactionitem')

    @property
    def overall_enrols(self):
        return self.homologous_enrols + self.heterologous_first_enrols + self.heterologous_second_enrols

    @property
    def homologous_enrols(self):
        enrols = self.vaccination_details_cls.objects.filter(
            received_dose_before='first_dose')
        return [enrol for enrol in enrols]

    @property
    def heterologous_first_enrols(self):
        hist = self.vaccination_history_cls.objects.filter(
            dose_quantity='1').exclude(dose1_product_name='azd_1222').values_list(
                'subject_identifier', flat=True)

        enrols = self.vaccination_details_cls.objects.filter(
            received_dose_before='second_dose', subject_visit__subject_identifier__in=hist)
        return [enrol for enrol in enrols]

    @property
    def heterologous_second_enrols(self):
        hist = self.vaccination_history_cls.objects.filter(
            dose_quantity='2').exclude(Q(dose1_product_name='azd_1222') |
                                       Q(dose2_product_name='azd_1222')).values_list(
                                           'subject_identifier', flat=True)

        enrols = self.vaccination_details_cls.objects.filter(
            received_dose_before='booster_dose', subject_visit__subject_identifier__in=hist)
        return [enrol for enrol in enrols]

    def create_query_name(self, query_name=None):
        obj, created = self.query_name_cls.objects.get_or_create(query_name=query_name)
        return obj

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
            assign=None, status=OPEN, subject=None, comment=None):
        obj, created = self.action_item_cls.objects.update_or_create(
            subject_identifier=subject_identifier,
            query_name=query_name,
            defaults={'assigned': assign,
                      'status': status,
                      'subject': subject,
                      'comment': comment,
                      'site': site})
        return obj

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
            return False if appt.appt_status == NEW_APPT else True

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
        hist = self.vaccination_history_cls.objects.filter(
            dose_quantity='1').exclude(dose1_product_name='azd_1222').values_list(
                'subject_identifier', flat=True)

        hetero_enrols = self.vaccination_details_cls.objects.filter(
            received_dose_before='second_dose',
            subject_visit__subject_identifier__in=hist).values_list(
                'subject_visit__subject_identifier', flat=True)

        second_doses = self.vaccination_details_cls.objects.filter(
            received_dose_before='second_dose').exclude(
                subject_visit__subject_identifier__in=hetero_enrols)

        for dose in second_doses:
            first_dose = self.vaccination_details_cls.objects.filter(
                subject_visit__subject_identifier=dose.subject_visit.subject_identifier,
                received_dose_before='first_dose')
            if not first_dose:
                assign = self.site_issue_assign_opts.get(dose.site.id)
                self.create_action_item(
                    site=dose.site,
                    subject_identifier=dose.subject_visit.subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    subject=subject,
                    comment=comment)

    @property
    def ae_data_issues(self):
        """
        AE start date is before first dose
        """
        query = self.create_query_name(
            query_name='AE start date before first dose')
        subject = "The adverse even start date is before the first dose."
        comment = "The participant adverse even start date is before" \
                  " the participant was vaccinated at visit(s) %(visits)s"
        aes = self.ae_model_cls.objects.all()
        erroneous_aes = {}

        for aer in aes:
            ae = aer.adverse_event
            subject_identifier = ae.subject_visit.subject_identifier
            visit_code = ae.subject_visit.visit_code
            visit_code_sequence = ae.subject_visit.visit_code_sequence
            ae_start_date = aer.start_date

            ae_visits = erroneous_aes.get(subject_identifier, [])
            try:
                vaccination = self.vaccination_details_cls.objects.get(
                    received_dose_before='first_dose',
                    subject_visit__subject_identifier=subject_identifier,
                    vaccination_date__date__gt=ae_start_date)
            except self.vaccination_details_cls.DoesNotExist:
                pass
            else:
                ae_visits.append(f'{visit_code}.{visit_code_sequence}')
                erroneous_aes.update({f'{subject_identifier}': ae_visits})
                assign = self.site_issue_assign_opts.get(vaccination.site.id)
                self.create_action_item(
                    site=vaccination.site,
                    subject_identifier=vaccination.subject_visit.subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    status=OPEN,
                    subject=subject,
                    comment=comment % {'visits': ', '.join(ae_visits)}
                )

    @property
    def missing_enrol_forms(self):
        """
        Missing required forms, e.g. demographic data form
        """
        crfmetadata = django_apps.get_model('edc_metadata.crfmetadata')
        query = self.create_query_name(
            query_name='Missing Visit Forms data')
        enrolments = self.overall_enrols
        for enrolment in enrolments:
            required_crfs = crfmetadata.objects.filter(
                subject_identifier=enrolment.subject_visit.subject_identifier,
                visit_code=enrolment.subject_visit.visit_code,
                entry_status='REQUIRED')

            for missing_crf in required_crfs:
                assign = self.site_issue_assign_opts.get(missing_crf.site.id)
                model = missing_crf.model
                model = model.split('.')[1]
                visit_code = missing_crf.visit_code
                subject = f'Participant is missing {model} data for visit {visit_code}.'
                comment = f'{subject}. Please complete the missing data for the form'
                self.create_action_item(
                    site=missing_crf.site,
                    subject_identifier=missing_crf.subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    subject=subject,
                    comment=comment, )

    @property
    def male_child_bearing_potential(self):
        """
        Male and child bearing potential is Yes
        """
        query = self.create_query_name(
            query_name='Male with child bearing potential')
        subject = 'Male participant with child bearing potential.'
        comment = f'{subject}. Please correct an update the screening accordingly'
        male_consents = self.consent_model_cls.objects.filter(
            gender='M').values_list('subject_identifier', flat=True)
        screening_eligibility = self.screening_eligibility_cls.objects.filter(
            subject_identifier__in=male_consents,
            childbearing_potential='Yes')
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
        comment = f'{subject}. Please re-evaluate the screening criteria'

        subject_identifiers = self.screening_eligibility_cls.objects.filter(
            is_eligible=False).values_list('subject_identifier', flat=True)
        participant_list = self.vaccination_details_cls.objects.filter(
            subject_visit__subject_identifier__in=subject_identifiers,
            received_dose=YES)

        for ineligibles in participant_list:
            assign = self.site_issue_assign_opts.get(ineligibles.site.id)
            self.create_action_item(
                site=ineligibles.site,
                subject_identifier=ineligibles.subject_visit.subject_identifier,
                query_name=query.query_name,
                assign=assign,
                subject=subject,
                comment=comment)

    @property
    def duplicate_subject_doses(self):
        enrolled_identifiers = self.vaccination_details_cls.objects.all().values_list(
            'subject_visit__subject_identifier', flat=True)
        enrolled_identifiers = list(set(enrolled_identifiers))
        doses = ['first_dose', 'second_dose', 'booster_dose']
        query = self.create_query_name(
            query_name='Subject has duplicate doses')
        comment = f'%(subject)s. Please re-evaluate the screening criteria'

        for enrol in enrolled_identifiers:
            for dose in doses:
                duplicated = ' '.join(dose.split('_'))
                subject = f'Subject has duplicate {duplicated}'
                vaccinations = self.vaccination_details_cls.objects.filter(
                    subject_visit__subject_identifier=enrol,
                    received_dose_before=dose)
                if vaccinations.count() > 1:
                    assign = self.site_issue_assign_opts.get(vaccinations[0].site.id)
                    self.create_action_item(
                        site=vaccinations[0].site,
                        subject_identifier=vaccinations[0].subject_visit.subject_identifier,
                        query_name=query.query_name,
                        assign=assign,
                        subject=subject,
                        comment=comment % {'subject': subject})

    @property
    def female_missing_preg(self):
        female_consents = self.consent_model_cls.objects.filter(
            gender='F').values_list('subject_identifier', flat=True)
        enrolled = self.vaccination_details_cls.objects.filter(
            subject_visit__subject_identifier__in=female_consents,
            received_dose=YES)
        query = self.create_query_name(
            query_name='Gender is F and pregnancy status form is missing')
        subject = 'Gender is F and pregnancy status form is missing'
        comment = 'Gender is F and pregnancy status form is missing'

        for enrol in enrolled:
            pregnancies = self.pregnancy_status_cls.objects.filter(
                subject_visit__subject_identifier=enrol.subject_visit.subject_identifier)
            if not pregnancies:
                assign = self.site_issue_assign_opts.get(enrol.site.id)
                self.create_action_item(
                    site=enrol.site,
                    subject_identifier=enrol.subject_visit.subject_identifier,
                    query_name=query.query_name,
                    assign=assign,
                    subject=subject,
                    comment=comment % {'subject': subject})
