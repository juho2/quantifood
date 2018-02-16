from django.shortcuts import render, redirect
from django.http import HttpResponse#, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
#from django.template import RequestContext
#from django.contrib.auth.models import User
#from django.template import loader
from django.core.cache import cache

from .models import Food#, Profile
from .helpers import *

@login_required
def index(request):
#    food_list = Food.objects.order_by('name')[:10]
#    food_list = Food.objects.all()[0:20]

#     if cache.get('recipe_ids'):
#         recipe_ids = cache.get('recipe_ids')
#         recipe_matrix = cache.get('recipe_matrix')
# #        print(sys.stderr, 'from cache')
#     else:
#         recipe_ids, recipe_matrix = make_recipe_matrix_from_postgres()
#         cache.set('recipe_ids', recipe_ids, None)
#         cache.set('recipe_matrix', recipe_matrix, None)
# #        print(sys.stderr, 'calculated')
#     target = initial_target
#     u = request.user
#     target = update_target(target, recipe_ids, recipe_matrix, u)
#     ratings = rate_recipes(recipe_matrix, target)
#     best_IDs, best_ratings = recommend_foods(ratings)
#     best_names, best_urls = [], []
#     for ID in best_IDs:
#         best_names.append(Food.objects.get(id_string=ID).name)
#         best_urls.append(Food.objects.get(id_string=ID).url)
#     best = zip(best_IDs, best_ratings, best_names, best_urls)
#     context = {'best': best, 'target': target}

   #  return (render(request, 'recommender/index.html', context))
    return (render(request, 'recommender/index.html'))


@login_required
def profile(request): #, user_id):
    prefs = {}
    preferences = {'Disabilities':'Lvl5 vegan - can not eat anything that casts a shadow', 
                 'Banned foods': 'Bacon, Cheese',
                 'Allergies': 'Fish, Milk'
                 }
    prefs['Placeholder preferences'] = preferences
    context = {'prefs': prefs}
    return(render(request, 'recommender/profile.html', context))

@login_required
def history(request):#, page_number): #, user_id):
#    food_history = Food.objects.all()
    u = request.user
    history = u.profile.food_history
    foodnames = []
    if len(history) > 0:
        for ID in history:
            foodnames.append(Food.objects.get(id_string=ID).name)
        if cache.get('recipe_ids'):
            recipe_ids = cache.get('recipe_ids')
            recipe_matrix = cache.get('recipe_matrix')
#            print(sys.stderr, 'from cache')
        else:
            recipe_ids, recipe_matrix = make_recipe_matrix_from_postgres()
            cache.set('recipe_ids', recipe_ids, None)    
            cache.set('recipe_matrix', recipe_matrix, None)
#            print(sys.stderr, 'calculated')
    context = {'foodnames': foodnames, 'history': history}#, 'nutrient_history': nutrient_history}
    return(render(request, 'recommender/history.html', context))
    
@login_required
def plot_history(request):
    u = request.user
    if cache.get('recipe_ids'):
        recipe_ids = cache.get('recipe_ids')
        recipe_matrix = cache.get('recipe_matrix')
#        response = plot_history(initial_target, recipe_ids, \
#        recipe_matrix, u, nutrient_list, nutrient_units)
        index, meal_no = 0, []
        history = u.profile.food_history
        nutrient_history = np.zeros((len(history), recipe_matrix.shape[1]))
        for recipe_id in history:
            #index = nutrient_history.index(meal)
            meal_no.append(index + 1)
            ind = recipe_ids.index(recipe_id)
    #        print(sys.stderr, ind)
            nutrients = np.asarray(recipe_matrix[ind,:])
            if index == 0:
                nutrient_history[index,:] = nutrients
            else:
                nutrient_history[index,:] = np.sum(np.vstack((nutrient_history[index-1:index,:],nutrients)), axis=0)
            
            index += 1
        daily_target = initial_target
    #    weekly_target = [value * 7 for value in initial_target]
        plt.ioff()
        fig=plt.figure(figsize=(16,9))
        plotindex = 0
        for value in daily_target:
            plt.subplot(3,3,plotindex+1)
            plt.plot(meal_no, nutrient_history[:,plotindex], 'bo', meal_no, \
            np.ones(len(meal_no)) * daily_target[plotindex], 'r--')
            plt.xlabel('Meal number')
            plt.ylabel('Nutrients consumed')
            nut = nutrient_list[plotindex]
            leg = [nut + ' (' + nutrient_units[nut] + ')']
            leg.append('Daily recommendation')# + ' (' + nutrient_units[nut] + ')')
            plt.legend(leg, loc=2, prop={'size':10})
            plotindex += 1
    #    plt.savefig(os.path.join(settings.BASE_DIR, 'recommender/static/recommender/images/history.png'), dpi=300)
    #    plt.close('all')
    #    return(nutrient_history)
        canvas=FigureCanvas(fig)
        response=HttpResponse(content_type='image/png')
        canvas.print_png(response)
        return(response)
#        return(response)
    else:
        return(redirect('recommender:history'))

@login_required    
def eat_ID(request, food_ID):
    u = request.user
    u.profile.food_history.append(food_ID)
    u.save()
#    return(HttpResponse('you ate food number %s' % food_ID))
    return(redirect('recommender:history'))

def reset(request):
    u = request.user
    u.profile.food_history = []
    u.save()
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
#    return(render_to_response('registration/register.html', {'form': form}))

def registration_complete(request):
    return(render(request, 'registration/registration_complete.html'))
    
#Your view can read records from a database, or not. It can use a template 
#system such as Django’s – or a third-party Python template system – or not. 
#It can generate a PDF file, output XML, create a ZIP file on the fly, anything 
#you want, using whatever Python libraries you want.
#All Django wants is that HttpResponse. Or an exception.