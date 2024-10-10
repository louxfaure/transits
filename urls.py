from django.urls import path, include

from . import views

urlpatterns = [
    path('',views.transits, name='transits'),
    path('data', views.transits_data, name='transits_data'),  # Vue qui renvoie les données JSON
]