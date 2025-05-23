from django.shortcuts import render

def home(request):
    return render(request, 'corpus_digital/home.html')
