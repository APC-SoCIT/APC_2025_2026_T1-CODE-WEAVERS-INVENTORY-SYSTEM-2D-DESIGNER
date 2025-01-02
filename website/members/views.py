from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

def resume(request):
    return render(request, 'resume.html')

def projects(request):
    return render(request, 'projects.html')

def about(request):
    return render(request, 'about.html')

def signin(request):
    return render(request, 'signin.html')
 
def store(request):
    return render(request, 'store.html')

def profile(request):
    return render(request, 'profile.html')

def myfirst(request):
    return render(request, 'myfirst.html')