from django.urls import path
from apps.webapp.views import WebAppIndexView

app_name = 'webapp'

urlpatterns = [
    path('', WebAppIndexView.as_view(), name='index'),
]

