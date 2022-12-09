from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta, datetime
from scripts.helper_function import *


app = Flask(__name__)
app.secret_key = "hello"


# store the permanent session data for 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)

# dropdown list
gender = ''
specificities = ''
food_list= []
kcal_list= []
qtt_list = []

# recipe suggestion recipe
recipes_main_random =[]
recipes_main_kcal_left=[]
recipes_main_url= []
Recipe = ''
Left_kcal = ''
Url = ''
            
@app.route('/', methods=["POST", "GET"])
def first_page():
    global kcal_list
    global food_list
    global qtt_list
    global Recipe
    global Left_kcal
    global Url
    spec_labels = specificities_lables()

    if "user" in session:
        user = session['user']


        if  request.method == "POST":
            gender = request.form["gender"]
            specificities = request.form["specificities"]

            food = str(request.form['food_selec'])
            food_list.append(food)
            nut_kcal = get_food_nutrition_kcal()
            nut_food = get_food_nutrition_name()


            index = nut_food.index(food)
            qtt = request.form['qtt']
            qtt_list.append(qtt)

            food_kcal = nut_kcal[index] * float(qtt) / 100
            kcal_list.append(food_kcal)
            tot_kcal = round(sum(kcal_list), 2)

            result = recipe_suggestion_main(tot_kcal, gender, specificities)
            if type(result) is list:
                Recipe = result[0]
                Left_kcal = round(result[1],2)
                Url = result[2]
                return render_template('index.html', user=user, food_list=food_list, tot_kcal=tot_kcal, nut_food=nut_food, Recipe=Recipe, Left_kcal=Left_kcal, Url=Url, spec_labels=spec_labels)
            else:
                msg = result
                return render_template('index.html', user=user, food_list=food_list, tot_kcal=tot_kcal, nut_food=nut_food, msg=msg, spec_labels=spec_labels)    

        else:
            nut_food = get_food_nutrition_name()
            return render_template('index.html', user=user, nut_food=nut_food, spec_labels=spec_labels)
        
    else:
        return render_template('index.html', spec_labels=spec_labels)



@app.route('/profile', methods=["POST", "GET"])
def profile_page():
    if "user" in session:
        user = session['user']
        
        try:
            graphJSON = dash(user)
            df_1 = get_table_profile_nut(user)
            df_2 = get_table_profile_recipes(user)
            return render_template('profile.html', user=user,  df_1=[df_1.to_html(classes='data', index=False)], df_2=[df_2.to_html(classes='data', index=False)], titles=[df_1.columns.values, df_2.columns.values], graphJSON=graphJSON)
        except:
            return render_template('profile.html', user=user)
    
    else:
        flash("You have to login first to access your profile!")
        return render_template('index.html')



@app.route('/ocr', methods=["POST", "GET"])
def ocr():
    if "user" in session:
        user = session['user']

        if  request.method == "POST":
            img = request.form['image_name']
            image_text = read_image(img)
            recipe_response, url_response = recipe_match(image_text)
            return render_template('ocr.html', user=user, img=img, image_text=image_text, recipe_response=recipe_response,url_response=url_response)
        else:
            return render_template('ocr.html', user=user)
    else:
        return render_template('ocr.html')
        

@app.route('/remove_list')
def remove_food_list():
    global food_list
    global kcal_list
    global qtt_list
    food_list = []
    kcal_list = []
    qtt_list = []
    return redirect(url_for('first_page'))


@app.route('/save_info')
def save_info():
    global kcal_list
    global food_list
    global qtt_list
    global Recipe
    global Url

    if "user" in session:
        user = session['user']
        conn = get_db_connection()
        c = conn.cursor()

        user_id = c.execute("""SELECT user_id FROM user WHERE name = (?)""", (user,)).fetchone()[0]
        receipe_id = c.execute("""SELECT recipe_id FROM recipes WHERE label = (?)""", (Recipe,)).fetchone()[0]
        
        c.execute("""INSERT INTO recipes_hist (user_id, receipe_id) 
                         VALUES (?,?)""",
                         (user_id, receipe_id))
        conn.commit()

        for food, qtt, kcal in zip(food_list, qtt_list, kcal_list):
            food_id = c.execute("""SELECT food_id FROM nutrition_table WHERE food_name = (?)""", (food,)).fetchone()[0]
            quantity = qtt
            portion_kcal = kcal         
            c.execute("""INSERT INTO nutrition_hist (user_id, food_id, quantity, portion_kcal) 
                         VALUES (?,?,?,?)""",
                         (user_id, food_id, quantity, portion_kcal))
            conn.commit()

        conn.close()
        return redirect(url_for('first_page'))



@app.route('/login', methods=["POST", "GET"])    
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        email = request.form["email"]
        password = request.form['pass']
        session["user"] = user    #create a session
        
        conn = get_db_connection()
        c = conn.cursor()
        email_exist = c.execute("""SELECT e_mail FROM user WHERE e_mail = (?)""", (email,)).fetchone()
        
        if email_exist == None:
            c.execute("""INSERT INTO user (password, e_mail, name) 
                         VALUES (?,?,?)""",
                         (password, email, user))
            conn.commit()
            conn.close()
            return redirect(url_for("first_page"))

        elif email_exist[0] == email:
            return redirect(url_for("first_page"))
    else:
        if "user" in session:
            flash("Already Logged in!")
            return redirect(url_for("first_page"))

        return render_template("login.html")



# to logout the session
@app.route("/logout")
def logout():
    global food_list
    global kcal_list
    global qtt_list
    food_list = []
    kcal_list = []
    qtt_list = []
    
    flash("You have been logged out!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))



if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True, port=3435)