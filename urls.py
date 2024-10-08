from django.urls import path, include

from . import views

urlpatterns = [
    path('transits',views.transits, name='transits'),
]