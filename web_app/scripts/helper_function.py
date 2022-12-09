import sqlite3
import random
import os
import io
import pandas as pd
import re
import sqlite3
from google.cloud import vision
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import json


def get_db_connection():
    conn = sqlite3.connect(r'final_project.db')
    return conn


def get_food_nutrition_name():
    conn = get_db_connection()
    c = conn.cursor()
    nut_food_ = c.execute("""SELECT food_name FROM nutrition_table""").fetchall()
    nut_food = [nf[0] for nf in nut_food_]
    return nut_food


def get_food_nutrition_kcal():
    conn = get_db_connection()
    c = conn.cursor()
    nut_kcal_ = c.execute("""SELECT energy_kcal FROM nutrition_table """).fetchall()
    nut_kcal = [nc[0] for nc in nut_kcal_]
    return nut_kcal

recipes_main_random =[]
recipes_main_kcal_left=[]
recipes_main_url= []


def recipe_suggestion_main(tot_kcal,gender, specificities):
   if gender == 'female':
      if tot_kcal < 2000.0:
         recom_kcal = 2000.0 - tot_kcal
         conn = get_db_connection()
         c = conn.cursor()
         recipes_list_main = c.execute(""" SELECT label, url, yield, healthLabels, cautions, calories, mealType, dishType FROM recipes WHERE dishType LIKE (?);""",("['main course']",)).fetchall()
         conn.close()
         for meal in recipes_list_main:
            if float(meal[5])/float(meal[2]) < recom_kcal:
               if meal[3].find(specificities) != -1:
                  kcal_left = recom_kcal - (float(meal[5])/float(meal[2]))
                  recipes_main_kcal_left.append(kcal_left)
                  recipes_main_random.append(meal[0])
                  recipes_main_url.append(meal[1])
            else:
               f"Sorry, but for this specificity for the amount of kcal left I couldn't find any recipe suggestions"

         recipe_recommended = random.choice(recipes_main_random)
         index = recipes_main_random.index(recipe_recommended)
         kcal_left = recipes_main_kcal_left[index]
         url = recipes_main_url[index]

         recipe_left_kcal = [recipe_recommended, round(kcal_left, 2), url]
         return recipe_left_kcal

      else:
         kcal_intake = tot_kcal - 2000.0
         return f"You have intake more {round(kcal_intake, 2)} kcals then the daily recommended.\nIf are hungry I would suggest a soup and 2-hours-walk or 1-hour-run."
   else:
      if tot_kcal < 2500.0:
         recom_kcal = 2500.0 - tot_kcal
         conn = get_db_connection()
         c = conn.cursor()
         recipes_list_main = c.execute(""" SELECT label, url, yield, healthLabels, cautions, calories, mealType, dishType FROM recipes WHERE dishType LIKE (?);""",("['main course']",)).fetchall()
         conn.close()
         for meal in recipes_list_main:
            if float(meal[5])/float(meal[2]) < recom_kcal:
               if meal[3].find(specificities) != -1:
                  kcal_left = recom_kcal - (float(meal[5])/float(meal[2]))
                  recipes_main_kcal_left.append(kcal_left)
                  recipes_main_random.append(meal[0])
                  recipes_main_url.append(meal[1])
            else:
               f"Sorry, but for this specificity for the amount of kcal left I couldn't find any recipe suggestions"

         recipe_recommended = random.choice(recipes_main_random)
         index = recipes_main_random.index(recipe_recommended)
         kcal_left = recipes_main_kcal_left[index]
         url = recipes_main_url[index]

         recipe_left_kcal = [recipe_recommended, round(kcal_left, 2), url]
         return recipe_left_kcal

      else:
         kcal_intake = tot_kcal - 2500.0
         return f"You have intake more {round(kcal_intake, 2)} kcals then the daily recommended.\nIf are hungry I would suggest a soup and 2-hours-walk or 1-hour-run."


def read_image(image_name):
    # insert Google API (OCR) credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=r'Google_API\final-project-369611-d232881e4d28.json'    
    # API connection
    client = vision.ImageAnnotatorClient()
    FILE_NAME = image_name
    FOLDER_PATH = r'C:\Users\inesa\OneDrive\IRONHACK\WEEKS\Week_8\Project\Final_Project\Images'
    with io.open(os.path.join(FOLDER_PATH,FILE_NAME), 'rb') as image_file:
        content = image_file.read()
    image = vision_v1.types.Image(content=content)
    response = client.text_detection(image=image)

    texts = response.text_annotations
    result = texts[0].description.replace('\n',' ')
    return result


def recipe_match(image_text):
    conn = get_db_connection()
    c = conn.cursor()
    recipe_list_name = [row[0].lower() for row in c.execute('SELECT label, url, calories, yield FROM recipes')]
    recipe_list_url = [row[1].lower() for row in c.execute('SELECT label, url, calories, yield FROM recipes')]
    conn.close()
    recipe_response = [food for food in recipe_list_name if set(image_text.lower().split()).issubset(food.split())]
    url_response = [url for food, url in zip(recipe_list_name,recipe_list_url) if set(image_text.lower().split()).issubset(food.split())]
    return recipe_response, url_response


def get_table_profile_nut(user):
    conn = get_db_connection()
    c = conn.cursor()
    data = c.execute("""SELECT time_stamp, food_name, quantity, portion_kcal  
                    FROM nutrition_table 
                    INNER JOIN nutrition_hist
                    ON nutrition_table.food_id = nutrition_hist.food_id
                    INNER JOIN user
                    ON nutrition_hist.user_id = user.user_id
                    WHERE name = (?);
                    """, (user,)).fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['Day and Hour', 'Food Selected', 'Food Quantity', 'Kcal per Portion'])
    return df


def get_table_profile_recipes(user):
    conn = get_db_connection()
    c = conn.cursor()
    data = c.execute("""SELECT time_stamp, label, url  
                    FROM recipes 
                    INNER JOIN recipes_hist
                    ON recipes.recipe_id = recipes_hist.receipe_id
                    INNER JOIN user
                    ON recipes_hist.user_id = user.user_id
                    WHERE name = (?);
                    """, (user,)).fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['Day and Hour', 'Recipe', 'Link to Recipe'])
    return df


def specificities_lables():
    conn = get_db_connection()
    c = conn.cursor()
    lables = c.execute("""SELECT healthLabels FROM recipes""").fetchall()
    healthLabels_labels = [label.strip("'[]").split("', '") for tuple_ in lables for label in tuple_]
    spec_labels = list(set([lab for specs in healthLabels_labels for lab in specs]))
    return spec_labels


def dash(user):
    conn = get_db_connection()
    c = conn.cursor()
    data = c.execute("""SELECT time_stamp, quantity, portion_kcal, lipids_g, carbohydrates_g, sugars_g, fiber_g , proteins_g, sal___g
                    FROM nutrition_table 
                    INNER JOIN nutrition_hist
                    ON nutrition_table.food_id = nutrition_hist.food_id
                    INNER JOIN user
                    ON nutrition_hist.user_id = user.user_id
                    WHERE name = (?);
                    """, (user,)).fetchall()
    conn.close()
    
    df = pd.DataFrame(data, columns=['Day and Hour', 'Quantity', 'Kcal per Portion', 'Lipids_g', 'Carbohydrates_g', 'Sugar_g', 'Fiber_g' , 'Proteins_g', 'Salt_g'])
    df['Other_Carbohydrates'] = df['Carbohydrates_g'] - df['Sugar_g']
    df['Date'] = pd.to_datetime(df['Day and Hour']).dt.date
    
    df.drop(columns=['Day and Hour', 'Carbohydrates_g'], inplace=True)
    
    df['Lipids_g'] = df['Lipids_g'] * df['Quantity'] /100
    df['Sugar_g'] = df['Sugar_g'] * df['Quantity'] /100
    df['Fiber_g'] = df['Fiber_g'] * df['Quantity'] /100
    df['Proteins_g'] = df['Proteins_g'] * df['Quantity'] /100
    df['Salt_g'] = df['Salt_g'] * df['Quantity'] /100
    df['Other_Carbohydrates'] = df['Other_Carbohydrates'] * df['Quantity'] /100
    
    df_gb = df.groupby(["Date"]).apply(sum).reset_index()
    df_verticalized = pd.melt(df_gb, id_vars= ["Date","Quantity","Kcal per Portion"])
    df_verticalized.rename(columns={"variable":"Componentes","value":"Quantity_g"}, inplace=True)
    
    fig = px.bar(df_verticalized, x="Quantity_g", y=str("Date"), color="Componentes", hover_name="Componentes",
                color_discrete_sequence=["rgb(0, 158, 108)", "rgb(2, 181, 124)", "rgb(252, 211, 187)", "rgb(247, 177, 136)", "rgb(252, 141, 76)", "rgb(255, 94, 0)"], title="Nutricional Information per day")
    fig.update_yaxes(type='category')
    fig.update_layout(paper_bgcolor="rgb(255, 255, 255, 0.5)", plot_bgcolor="rgb(255, 255, 255, 0.5)", legend=dict(bgcolor="rgb(242, 242, 242)"))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

