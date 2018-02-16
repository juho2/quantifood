from django.http import HttpResponse
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os

from .models import Food
from qf_site.settings import STATIC_ROOT

# constants
foodcom_target = {'208':2000.,
                  '205':300.,
                  '601':300.,
                  '204':65.,
                  '291':25.,
                  '203':50.,
                  '606':20.,
                  '307':2400.,                  
                  '269':25.,
                  }
nutrient_conv_foodcom = {'calories':'208',
                         'carbohydrate':'205',
                         'cholesterol':'601',
                         'fat':'204',
                         'fiber':'291',
                         'protein':'203',
                         'saturatedfat':'606',
                         'sodium':'307',
                         'sugar':'269'
                         }
nutrient_units = {"fat": "g",
                  "fiber": "g",
                  "sugar": "g",
                  "sodium": "mg",
                  "protein": "g",
                  "calories": "kcal",
                  "cholesterol": "mg",
                  "carbohydrate": "g",
                  "saturatedfat": "g"
                  }
initial_target = [foodcom_target[key]
                  for key in [nutrient_conv_foodcom[key2]
                              for key2 in sorted(nutrient_conv_foodcom)]]
nutrient_list = [key for key in sorted(nutrient_conv_foodcom)]


def get_recipe_matrix(loc='static'):
    """ Get a (foods, nutrients)-matrix from db or file. """
    if loc == 'db':
        recipe_ids, nut_dicts = [], []
        for food in Food.objects.all():
            recipe_ids.append(food.id_string)
            nut_dicts.append(food.nutrients)
        recipe_matrix = np.zeros([len(recipe_ids), len(nut_dicts[0])])
        for rownum, nut_dict in enumerate(nut_dicts):
            nut_values = [nut_dict[key][0] for key in sorted(nut_dict)]
            row = np.asarray(nut_values).astype(np.float)
            recipe_matrix[rownum, :] = row
    elif loc == 'static':
        path = os.path.join(STATIC_ROOT, 'recipe_data.npz')
        recipe_data = np.load(path)
        recipe_ids = recipe_data['ids']
        recipe_matrix = recipe_data['mat']
    else:
        raise(Exception('Invalid nutrient data source: ' + str(loc)))
    return(list(recipe_ids), recipe_matrix)

   
def filter_recipes(recipe_matrix, banned_keywords, banned_recipes):
    """ Filter by user preferences """
    #return(filtered_recipe_matrix)
    pass


def rate_recipes(recipe_matrix, target, rating_constant=50):
    """ Ratings wrt. other recipes in DB (1 serving). """
    # target is recommended daily intake
    target_vector = np.asarray(target)
    nutrient_weights = np.ones(len(target_vector))  # TBD reasonable weights
    target_vector *= nutrient_weights
    # relative errors
    errors = np.sum(np.power((recipe_matrix-target_vector)/target_vector, 2), axis=1)
    errors /= np.max(errors)
    # foods rated relative to rating_constant (%) best foods in db
    rating_constant = len(errors) * (100 - rating_constant) // 100
    min_errors = sorted(list(errors))[:rating_constant]
    ratings = 100 * (1 - errors/np.max(min_errors))  # worst foods will be negative
    return(ratings)


def recommend_foods(ratings, pos = (0,29)):
    best_IDs, best_ratings = [], []
    best_indices = ratings.argsort()[-len(ratings):][::-1]
    for index in best_indices[pos[0]:pos[1]]:
        index_DB = Food.objects.all()[0].pk + index
        recipe_id = Food.objects.get(pk=index_DB).id_string
        best_IDs.append(recipe_id)
#        recommended[recipe_id] = ratings[index]
        best_ratings.append(str(round(ratings[index],1)))
    return(best_IDs, best_ratings)


def update_target(target, recipe_ids, recipe_matrix, u):
    history = u.profile.food_history
    for recipe_id in history:
        ind = recipe_ids.index(recipe_id)
        nutrients = recipe_matrix[ind,:]        
        target -= nutrients
    return(target)


def plot_nutrient_history(u, recipe_ids, recipe_matrix, initial_target=initial_target,
                          nutrient_list=nutrient_list, nutrient_units=nutrient_units):
    index, meal_no = 0, []
    history = u.profile.food_history
    nutrient_history = np.zeros((len(history), recipe_matrix.shape[1]))
    for recipe_id in history:
        meal_no.append(index + 1)
        ind = recipe_ids.index(recipe_id)
        nutrients = np.asarray(recipe_matrix[ind, :])
        if index == 0:
            nutrient_history[index, :] = nutrients
        else:
            nutrient_history[index, :] = \
                np.sum(np.vstack((nutrient_history[index - 1:index, :],
                                  nutrients)), axis=0)
        index += 1
    daily_target = initial_target
    #    weekly_target = [value * 7 for value in initial_target]
    plt.ioff()
    fig = plt.figure(figsize=(16, 9))
    for k in range(len(daily_target)):
        plt.subplot(3, 3, k + 1)
        plt.plot(meal_no, nutrient_history[:, k], 'bo', meal_no,
                 np.ones(len(meal_no)) * daily_target[k], 'r--')
        plt.xlabel('Meal number')
        plt.ylabel('Nutrients consumed')
        nut = nutrient_list[k]
        leg = ['{} ({})'.format(nut, nutrient_units[nut]), 'Daily recommendation']
        plt.legend(leg, loc=2, prop={'size': 10})
    return(fig)
