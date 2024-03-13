from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        # Liste des noms de vue que vous souhaitez inclure dans le sitemap
        return ['home', 'task_lists', 'create_task_list', 'register', 'login', 'logout', 'create_category',
                'category_list']

    def location(self, item):
        return reverse(item)
