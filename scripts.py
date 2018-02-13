import requests
from bs4 import BeautifulSoup
import sqlite3
import numpy as np
import re
import pickle

def create_meals_database():

    def _find_macro(text, dict_data):
        if "Total Fat" in text:
            dict_data['fat'] = int(re.search("(\d+)g", text).group(1))
        elif "Total Carbohydrates" in text:
            dict_data['carb'] = int(re.search("(\d+)g", text).group(1))
        elif "Protein" in text:
            dict_data['protein'] = int(re.search("(\d+)g", text).group(1))
        return dict_data

    def _get_category(categ_list):
        if "Breakfast & Brunch" in categ_list:
            return "breakfast"
        elif "Salads" in categ_list:
            return "dinner"
        elif "Desserts" in categ_list:
            return "other"
        elif "Beverages" in categ_list:
            return "other"
        else:
            return "launch"

    main_page = "https://www.justataste.com/recipes/page/"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'}
    connection = sqlite3.connect('data/database.db')
    cursor = connection.cursor()
    count = 0
    numpy_memory_values = []

    for i in range(1, 81):
        page = main_page + str(i)
        print(page)
        page_url = requests.get(page, headers=headers)
        soup = BeautifulSoup(page_url.text, 'html.parser')
        links = [x.find("a", href=True)['href'] for x in soup.find_all('div', {"class":"post"})]
        for link in links:
            reciepe_url = requests.get(link, headers=headers)
            soup2 = BeautifulSoup(reciepe_url.text, 'html.parser')

            title_temp = soup2.find("h3", {"class": "recipe-title"})
            if not title_temp:
                continue
            title = title_temp.text
            print(title)
            # TODO: UNFINISHED STUFF: preparation time etc.
            #info = soup2.find("div", {"class": "wprm-recipe-details-container wprm-recipe-times-container"}).text
            #ingridients = [x.text for x in soup2.find("ul", {"class": "wprm-recipe-ingredients"}).find_all("li")]
            categories_temp = soup2.find_all("div", {"class": "recipe-categories-single"})[0].text
            _, _, cat = categories_temp.partition("Categories:")
            categories = [x.strip() for x in cat.split(",")]
            category_final = _get_category(categories)
            macros = {}
            for item in soup2.find_all("div", {"class": "nutrition-item"}):
                macros = _find_macro(item.text, macros)
            if not macros:
                continue
            if 'protein' not in macros:
                macros['protein'] = 0
            if 'fat' not in macros:
                macros['fat'] = 0
            if 'carb' not in macros:
                macros['carb'] = 0

            numpy_memory_values.append([macros['protein'], macros['fat'], macros['carb']])

            query = "INSERT INTO recipies VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (count, title, category_final, macros['protein'], macros['fat'], macros['carb'], link))
            count += 1

    connection.commit()
    connection.close()
    numpy_array = np.array(numpy_memory_values)
    with open("data/recipe_np.pkl", "wb") as fp:
        pickle.dump(numpy_array, fp)


def create_recipes_table():
    connection = sqlite3.connect('data/database.db')
    cursor = connection.cursor()

    create_table_recipies = "CREATE TABLE IF NOT EXISTS recipies (id int, " \
                             "title text," \
                             "type text," \
                             "protein int," \
                             "fat int," \
                             "carbs int," \
                             "link text)"

    create_table_users = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, " \
                   "username text, " \
                   "password text, " \
                   "height int, " \
                   "weight int," \
                   "age int," \
                   "sex text)"

    cursor.execute(create_table_recipies)
    cursor.execute(create_table_users)
    connection.commit()
    connection.close()


if __name__ == '__main__':
    create_meals_database()
