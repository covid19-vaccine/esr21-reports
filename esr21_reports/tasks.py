from celery import shared_task
from celery.signals import worker_process_init
from celery.utils.log import get_task_logger
from django.core.management import call_command

logger = get_task_logger(__name__)


@worker_process_init.connect
def configure_workers(sender=None, conf=None, **kwargs):
    from Crypto import Random
    Random.atfork()


@shared_task
def pull_reports_data():
    call_command('populate_graphs')


@shared_task
def generate_queries():
    print("generating new queries")
    call_command("generate_data_queries", verbosity=0)
    return "success"
