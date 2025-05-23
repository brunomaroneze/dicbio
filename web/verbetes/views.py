from django.shortcuts import render

def home(request):
    return render(request, 'verbetes/home.html')
