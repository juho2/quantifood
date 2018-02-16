from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from .helpers import *


@login_required
def index(request):
    if cache.get('recipe_ids') is not None:
        recipe_ids = cache.get('recipe_ids')
        recipe_matrix = cache.get('recipe_matrix')
    else:
        recipe_ids, recipe_matrix = get_recipe_matrix(loc='static')
        cache.set_many({'recipe_ids': recipe_ids, 'recipe_matrix': recipe_matrix}, None)
    u = request.user
    if cache.get('target') is not None:
        cached = cache.get_many(['target', 'best_IDs', 'best_ratings'])
        target, best_IDs, best_ratings = cached['target'], cached['best_IDs'], cached['best_ratings']
    else:
        target = update_target(initial_target, recipe_ids, recipe_matrix, u)
        ratings = rate_recipes(recipe_matrix, target)
        best_IDs, best_ratings = recommend_foods(ratings)
        cache.set_many({'target': target, 'best_IDs': best_IDs,
                        'best_ratings': best_ratings}, None)
    best_names, best_urls = [], []
    for ID in best_IDs:
        best_names.append(Food.objects.get(id_string=ID).name)
        best_urls.append(Food.objects.get(id_string=ID).url)
    best = zip(best_IDs, best_ratings, best_names, best_urls)
    context = {'best': best, 'target': target}
    return (render(request, 'recommender/index.html', context))


@login_required
def profile(request):
    prefs = {}
    preferences = {'Disabilities':'Lvl5 vegan - can not eat anything that casts a shadow', 
                 'Banned foods': 'Bacon, Cheese',
                 'Allergies': 'Fish, Milk'
                 }
    prefs['Placeholder preferences'] = preferences
    context = {'prefs': prefs}
    return(render(request, 'recommender/profile.html', context))


@login_required
def history(request):
    u = request.user
    history = u.profile.food_history
    foodnames = []
    if len(history) > 0:
        for ID in history:
            foodnames.append(Food.objects.get(id_string=ID).name)
    context = {'foodnames': foodnames, 'history': history}
    return(render(request, 'recommender/history.html', context))


@login_required
def plot_history(request):
    u = request.user
    if cache.get('recipe_ids') is not None:
        recipe_ids = cache.get('recipe_ids')
        recipe_matrix = cache.get('recipe_matrix')
    else:
        recipe_ids, recipe_matrix = get_recipe_matrix(loc='static')
        cache.set_many({'recipe_ids': recipe_ids, 'recipe_matrix': recipe_matrix}, None)
    fig = plot_nutrient_history(u, recipe_ids, recipe_matrix)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return(response)


@login_required    
def eat_ID(request, food_ID):
    u = request.user
    u.profile.food_history.append(food_ID)
    u.save()
    cache.delete_many(['target', 'best_IDs', 'best_ratings'])
    return(redirect('recommender:history'))


@login_required
def reset(request):
    u = request.user
    u.profile.food_history = []
    u.save()
    cache.delete_many(['target', 'best_IDs', 'best_ratings'])
    return(redirect('recommender:index'))    


def register(request):
#    c = RequestContext(request, {})
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            u = form.save()
            return(redirect('recommender:registration_complete'))
    else:
        form = UserCreationForm()
    return(render(request, 'registration/register.html', {'form':form}))


def registration_complete(request):
    return(render(request, 'registration/registration_complete.html'))
