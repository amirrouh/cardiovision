from http.client import HTTPResponse
from urllib import request
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

def gui_home(request):
    return render(request, 'gui/index.html')