from django.views.generic import TemplateView


class WebAppIndexView(TemplateView):
    """
    Telegram WebApp (Mini App) asosiy SPA interfeysi sahifasi.
    """
    template_name = 'webapp/index.html'

