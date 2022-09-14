from django.core.management.base import BaseCommand

from ...classes import QueryGeneration, COVIDRelatedQueries, HIVStatusQueries


class Command(BaseCommand):

    help = 'Generate queries'

    def handle(self, *args, **kwargs):
        general_queries = QueryGeneration()
        hiv_queries = HIVStatusQueries()
        covid_queries = COVIDRelatedQueries()
        print("Generating queries for missing first dose")
        general_queries.first_dose_second_dose_missing
        print("Generating queries for vaccinated but not eligible participants")
        general_queries.ineligible_vaccinated_participant
        print("Generating queries for male with child bearing potential")
        general_queries.male_child_bearing_potential
        print("Generating queries with ae date before vaccination")
        general_queries.ae_data_issues
        print("Generating queries for missing enrolment forms")
        general_queries.missing_enrol_forms
        print("Generating queries for duplicate subject doses")
        general_queries.duplicate_subject_doses
        print("Generating queries for female missing pregnancy status")
        general_queries.female_missing_preg
        print("Generating ae stop date not resolved")
        general_queries.ae_not_resolved
        print("Generating booster dose with missing second dose")
        general_queries.booster_dose_missing_second_dose
        print("Generating booster dose with missing vaccination history")
        general_queries.booster_dose_missing_vaccination_history
        print('Generating COVID related queries')
        covid_queries.symptomaticinfections_missing()
        covid_queries.pcr_results_missing()
        covid_queries.no_infections_symptoms_specified()
        covid_queries.enrolment_covidsymptoms_pcr_missing()
        print('Generating HIV related queries')
        hiv_queries.missing_hiv_test_results()
#         hiv_queries.neg_hiv_status_on_art()
        print('Done')
