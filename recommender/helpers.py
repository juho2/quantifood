from django.http import HttpResponse
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from .models import Food

# recipe_matrix nutrient cols are in alphabetical order
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
                         
initial_target = [foodcom_target[key] for key in [nutrient_conv_foodcom[key2]
                                                  for key2 in sorted(nutrient_conv_foodcom)]]
nutrient_list = [key for key in sorted(nutrient_conv_foodcom)]

def make_recipe_matrix_from_postgres():
#    t = time.time()
#    cur.execute("SELECT id_string,nutrients FROM recommender_food")    
#    tuplelist = cur.fetchall()
    recipe_ids, nut_dicts, servings = [], [], []
    for food in Food.objects.all():
        recipe_ids.append(food.id_string)
        nut_dicts.append(food.nutrients)
#        servings.append(food.servings)
#    tuplelist = Food.objects.all()
#    recipe_ids = [item[0] for item in tuplelist] # will be in ascending order
#    nut_dicts = [item[1] for item in tuplelist]
    recipe_matrix = np.zeros([len(recipe_ids), len(nut_dicts[0])])
    for rownum, nut_dict in zip(range(len(nut_dicts)), nut_dicts):
        nutlist = [nut_dict[key][0] for key in sorted(nut_dict)]
        row = np.asarray(nutlist).astype(np.float)
        recipe_matrix[rownum,:] = row #/ float(servings[rownum])
#    print(sys.stderr, recipe_matrix.shape)
#    print(str(recipe_matrix.shape[0]) + ' rows, ' + str(recipe_matrix.shape[1]) + \
#    ' columns constructed in ' + str(time.time()-t) + ' s')
    return(recipe_ids, recipe_matrix)
 
def insert_recipe_matrix_to_postgres(recipe_matrix, cur):
#    print(str(recipe_matrix.shape[0]) + ' rows, ' + str(recipe_matrix.shape[1]) + \
#    ' columns inserted in ' + str(time.time()-t) + ' s')    
    pass

def get_recipe_matrix_from_postgres(cur):
    pass
   
def filter_recipes(recipe_matrix, banned_keywords, banned_recipes):
    #return(filtered_recipe_matrix)
    pass

def rate_recipes(recipe_matrix, target, rating_constant=50):
    """ Ratings wrt. other recipes in DB (1 serving). """
    # target is recommended daily intake
    target_vector = np.asarray(target)
    nutrient_weights = np.ones(len(target_vector)) # TBD reasonable weights
    target_vector *= nutrient_weights
    # relative errors
    errors = np.sum(np.power((recipe_matrix-target_vector)/target_vector, 2), axis=1)
    errors /= np.max(errors)
    # foods rated relative to rating_constant (%) best foods
    rating_constant = len(errors) * (100 - rating_constant) // 100
    min_errors = sorted(list(errors))[:rating_constant]
    ratings = 100 * (1 - errors/np.max(min_errors)) # worst 100-rating_constant % of foods will be negative
#    ratings = 100*(1-errors)
#    print(sorted(ratings)[-10:])
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
    
def plot_history(initial_target, recipe_ids, recipe_matrix, u, nutrient_list, nutrient_units):
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
    fig = plt.figure(figsize=(16,9))
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
    