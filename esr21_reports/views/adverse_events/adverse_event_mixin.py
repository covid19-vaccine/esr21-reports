from django.apps import apps as django_apps
from django.db.models import Q, Count
from edc_constants.constants import NEG, POS, YES, NO
from ..site_helper_mixin import SiteHelperMixin


class AdverseEventRecordMixin:
    ae_record_model = 'esr21_subject.adverseeventrecord'
    ae_model = 'esr21_subject.adverseevent'
    rapid_hiv_testing_model = 'esr21_subject.rapidhivtesting'
    vaccination_detail_model = 'esr21_subject.vaccinationdetails'
    consent_model = 'esr21_subject.informedconsent'
    demographics_data_model = 'esr21_subject.demographicsdata'

    @property
    def ae_record_cls(self):
        return django_apps.get_model(self.ae_record_model)

    @property
    def ae_cls(self):
        return django_apps.get_model(self.ae_model)

    @property
    def vaccination_detail_cls(self):
        return django_apps.get_model(self.vaccination_detail_model)

    @property
    def rapid_hiv_testing_cls(self):
        return django_apps.get_model(self.rapid_hiv_testing_model)

    @property
    def demographics_data_cls(self):
        return django_apps.get_model(self.demographics_data_model)

    @property
    def consent_cls(self):
        return django_apps.get_model(self.consent_model)

    @property
    def overral_adverse_events(self):
        overral_soc = self.ae_record_cls.objects.values('soc_name').annotate(
            total=Count('soc_name', filter=Q(soc_name__isnull=False)),
            mild=Count('ctcae_grade', filter=Q(ctcae_grade='mild')),
            moderate=Count('ctcae_grade', filter=Q(ctcae_grade='moderate')),
            severe=Count('ctcae_grade', filter=Q(ctcae_grade='severe')),
            life_threatening=Count('ctcae_grade', filter=Q(ctcae_grade='life_threatening')),
            fatal=Count('ctcae_grade', filter=Q(ctcae_grade='fatal')),

        )

        pt_name_list = self.ae_record_cls.objects.values('soc_name', 'pt_name').annotate(
            total=Count('pt_name', filter=Q(soc_name__isnull=False)),
            mild=Count('ctcae_grade', filter=Q(ctcae_grade='mild')),
            moderate=Count('ctcae_grade', filter=Q(ctcae_grade='moderate')),
            severe=Count('ctcae_grade', filter=Q(ctcae_grade='severe')),
            life_threatening=Count('ctcae_grade', filter=Q(ctcae_grade='life_threatening')),
            fatal=Count('ctcae_grade', filter=Q(ctcae_grade='fatal')),
        )

        overall = []
        unique_soc = []
        for pt in pt_name_list:
            soc_name = pt.get('soc_name')
            soc_stats = next((sub for sub in overral_soc if sub['soc_name'] == soc_name), None)
            if soc_stats and soc_stats.get('pt') is not None:
                del pt['soc_name']
                soc_stats['pt'].append(pt)
            elif soc_stats:
                del pt['soc_name']
                soc_stats['pt'] = [pt]

            if soc_name.lower() not in unique_soc:
                overall.append(soc_stats)
                unique_soc.append(soc_name.lower())
        return overall

    @property
    def hiv_uninfected(self):
        return self.adverse_events_by_hiv_status(status=NEG)

    @property
    def hiv_infected(self):
        return self.adverse_events_by_hiv_status(status=POS)

    @property
    def received_first_dose(self):
        return self.adverse_event_by_vaccination(dose='first_dose')

    @property
    def received_second_dose(self):
        return self.adverse_event_by_vaccination(dose='second_dose')

    @property
    def related_ip(self):
        return self.adverse_event_by_attrib(choice=YES)

    @property
    def not_related_ip(self):
        return self.adverse_event_by_attrib(choice=NO)

    @property
    def received_first_dose_plus_28(self):
        pass

    @property
    def all_ae_records(self):
        sae_ids = self.ae_record_cls.objects.all().distinct().values_list(
            'adverse_event__subject_visit__subject_identifier', flat=True)
        all_ae = []
        for subject_identifier in sae_ids:
            sae = self.sae_record(subject_identifier)
            consent = self.consent(subject_identifier)
            hiv_test = self.hiv_test(subject_identifier)
            demographics = self.demographics_record(subject_identifier)

            first_dose_vaccine = self.vaccination_record(
                subject_identifier=subject_identifier, dose='first_dose')

            second_dose_vaccine = self.vaccination_record(
                subject_identifier=subject_identifier, dose='second_dose')

            aes = self.ae_record_cls.objects.filter(
                adverse_event__subject_visit__subject_identifier=subject_identifier)
            for ae in aes:
                all_ae.append((subject_identifier, ae, sae, consent,
                               first_dose_vaccine, second_dose_vaccine,
                               demographics, hiv_test))
        return all_ae

    def adverse_events_by_hiv_status(self, status=None):
        hiv_test = self.rapid_hiv_testing_cls.objects.filter(
            Q(hiv_result=status) | Q(rapid_test_result=status)).values_list(
                'subject_visit__subject_identifier', flat=True).distinct()

        q = Q(adverse_event__subject_visit__subject_identifier__in=hiv_test)

        overall = self.overral_filter_by_query_object(q)
        return overall

    def adverse_event_by_attrib(self, choice):
        q = Q(ae_rel=choice)
        overall = self.overral_filter_by_query_object(q)
        return overall

    def adverse_event_by_vaccination(self, dose):
        received_dose = self.vaccination_detail_cls.objects.filter(
            received_dose_before=dose).values_list(
            'subject_visit__subject_identifier', flat=True).distinct()
        q = Q(adverse_event__subject_visit__subject_identifier__in=received_dose)
        overall = self.overral_filter_by_query_object(q)
        return overall

    def overral_filter_by_query_object(self, query):
        soc_list = self.ae_record_cls.objects.filter(query).values('soc_name').annotate(
            total=Count('soc_name', filter=Q(soc_name__isnull=False)),
            mild=Count('ctcae_grade', filter=Q(ctcae_grade='mild')),
            moderate=Count('ctcae_grade', filter=Q(ctcae_grade='moderate')),
            severe=Count('ctcae_grade', filter=Q(ctcae_grade='severe')),
            life_threatening=Count('ctcae_grade', filter=Q(ctcae_grade='life_threatening')),
            fatal=Count('ctcae_grade', filter=Q(ctcae_grade='fatal')),
        )

        pt_name_list = self.ae_record_cls.objects.filter(query).values(
            'soc_name', 'pt_name').annotate(
            total=Count('pt_name', filter=Q(hlt_name__isnull=False)),
            mild=Count('ctcae_grade', filter=Q(ctcae_grade='mild')),
            moderate=Count('ctcae_grade', filter=Q(ctcae_grade='moderate')),
            severe=Count('ctcae_grade', filter=Q(ctcae_grade='severe')),
            life_threatening=Count('ctcae_grade', filter=Q(ctcae_grade='life_threatening')),
            fatal=Count('ctcae_grade', filter=Q(ctcae_grade='fatal')),
        )

        overall = []
        unique_soc = []

        for pt in pt_name_list:
            soc_name = pt.get('soc_name')
            soc_stats = next((sub for sub in soc_list if sub['soc_name'] == soc_name), None)
            if soc_stats and soc_stats.get('pt') is not None:
                del pt['soc_name']
                soc_stats['pt'].append(pt)
            elif soc_stats:
                del pt['soc_name']
                soc_stats['pt'] = [pt]
            if soc_name not in unique_soc:
                overall.append(soc_stats)
                unique_soc.append(soc_name)

        return overall

    def hiv_test(self, subject_identifier):
        try:
            return self.rapid_hiv_testing_cls.objects.get(
                subject_visit__subject_identifier=subject_identifier,)
        except self.rapid_hiv_testing_cls.DoesNotExist:
            pass
        return None

    def consent(self, subject_identifier):
        try:
            return self.consent_cls.objects.filter(
                subject_identifier=subject_identifier).latest('consent_datetime')
        except self.consent_cls.DoesNotExist:
            pass
        return None

    def sae_record(self, subject_identifier):
        try:
            return self.sae_record_cls.objects.filter(
                serious_adverse_event__subject_visit__subject_identifier=subject_identifier)
        except self.sae_record_cls.DoesNotExist:
            pass
        return None

    def vaccination_record(self, subject_identifier, dose):
        try:
            return self.vaccination_detail_cls.objects.get(
                subject_visit__subject_identifier=subject_identifier,
                received_dose_before=dose)
        except self.vaccination_detail_cls.DoesNotExist:
            pass
        return None

    def demographics_record(self, subject_identifier):
        try:
            return self.demographics_data_cls.objects.get(
                subject_visit__subject_identifier=subject_identifier)
        except self.demographics_data_cls.DoesNotExist:
            pass
        return None

    @property
    def ae_overall(self):
        overall = self.ae_cls.objects.count()
        gaborone = self.get_adverse_event_by_site('Gaborone').count()
        maun = self.get_adverse_event_by_site('Maun').count()
        serowe = self.get_adverse_event_by_site('Serowe').count()
        f_town = self.get_adverse_event_by_site('Francistown').count()
        phikwe = self.get_adverse_event_by_site('Phikwe').count()

        return ['Adverse Events', overall, gaborone, maun, serowe,
                f_town, phikwe, ]

    def get_adverse_event_by_site(self, site=None):
        site_helper = SiteHelperMixin()
        site_id = site_helper.get_site_id(site)
        if site_id:
            return self.ae_cls.objects.filter(site_id=site_id)
