from django.contrib.sites.models import Site


class SiteHelperMixin:

    @property
    def sites_names(self):
        site_names = Site.objects.order_by('id').values_list('name', flat=True)
        site_names = list(map(lambda name: name.split('-')[1], site_names))
        return site_names

    @property
    def sites_ids(self):
        return Site.objects.order_by('id').values_list('id', flat=True)

    def get_site_id(self, site_name_postfix):
        try:
            return Site.objects.get(name__endswith=site_name_postfix).id
        except Site.DoesNotExist:
            pass

    @property
    def site_ids(self):
        return Site.objects.order_by('id').values_list('id', flat=True)