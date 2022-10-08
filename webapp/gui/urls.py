from django.urls import path
from . import views

urlpatterns = [
    path('', views.gui_home, name='gui_home'),
]