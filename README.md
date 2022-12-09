
# Project: I'm Hungry! (Web app)

Ironhack's Data Analytics Bootcamp Final Project


## Overview
For my final Ironhack project I chose to build a Web App that suggests recipes just because at the end of a very busy day the last thing we want is to decide what to cook! Right?

In this app we can input what we’ve already eaten and have a tasty easy-to-do balanced recipe idea. It’s also possible to take a picture of your favourite dish from a restaurant menu and have the recipe for that.

**Features:**
- Recipe suggestion;
- Direct link to recipes;
- Profile page with nutritional value, food intake and recipes saved;
- Menu picture upload for recipe.

**Data Collection:**
- Ricardo Jorge nutritional table (translated from Portuguese);
- Edamam API for recipes.

**Methodologies:**
- Data pipeline;
- SQLite (python connection);
- Flask, Html, Css, JavaScript;
- Unsupervised learning (variety of suggested recipes);
- Optical Character Recognition (OCR) - Google Vision API (text recognition from menu pictures);
- Google translate.


## Web App Exemple

### First Page
![home_page](https://github.com/IAndradeDA/I-m_Hungry_web_app/blob/main/Gifs/Intro11.gif)


### Profile
![profile_page](https://github.com/IAndradeDA/I-m_Hungry_web_app/blob/main/Gifs/OCR.gif)


### OCR
![ocr_page](https://github.com/IAndradeDA/I-m_Hungry_web_app/blob/main/Gifs/Profile.gif)


## Getting started

#### Web_app
Run web_app > web_app.py

#### Credentials

1. You will need to have **Google Vision API** credentials and insert your json file path into the `read_image()` function in web_app > scripts > helper_function.py if you want OCR to work. 

2. You will need credentials for **Edamam API** only if you want to add more recipes to the database.


