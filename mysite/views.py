from django.shortcuts import render, redirect, render_to_response
# from django.http import HttpResponse

def index(request):
    # return HttpResponse("Welcome to Quantifood.")
    return(redirect('recommender:index'))

#def login(request):
#    return HttpResponse("Login form")
#
#def register(request):
#    return HttpResponse("Register form")
#    