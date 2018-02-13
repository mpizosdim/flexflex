import re
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
import pickle
from db import db
#import sklearn.metrics.pairwise.cosine_similarity as cos_sim


class recipie(db.Model):
    __tablename__ = 'recipies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    type = db.Column(db.String(80))
    protein = db.Column(db.Float(precision=2))
    fat = db.Column(db.Float(precision=2))
    carbs = db.Column(db.Float(precision=2))
    link = db.Column(db.String(200))

    def __init__(self, _id, title, type, protein, fat, carbs, link):
        self.id = _id
        self.title = title
        self.type = type
        self.protein = protein
        self.fat = fat
        self.carbs = carbs
        self.link = link

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(80))

    def __init__(self, username, password, height, weight, age, sex):
        self.username = username
        self.password = password
        self.height = height
        self.weight = weight
        self.age = age
        self.sex = sex

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

macro_meals = pickle.load(open('data/recipe_np.pkl', "rb"))


class Recommendation(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('activity', type=str, required=True, help='activity: no blank')
    parser.add_argument('goal', type=str, required=True, help='goal: no blank')

    @jwt_required()
    def post(self, username):
        data = Recommendation.parser.parse_args()
        user = User.find_by_username(username)
        protein, fat, carbs = get_macros(user.weight, user.height, user.age, user.sex, data['activity'], data['goal'])
        # TODO: find the way to optimize the meals. Not implimented yet.
        # =========================
        breakfast_id = 14
        launch_id = 30
        dinner_id = 50
        # =========================
        breakfast = recipie.find_by_id(breakfast_id)
        launch = recipie.find_by_id(launch_id)
        dinner = recipie.find_by_id(dinner_id)

        return {'breakfast': breakfast.title, "launch": launch.title, "dinner": dinner.title}


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='username: no blank')
    parser.add_argument('password', type=str, required=True, help='password: no blank')
    parser.add_argument('height', type=int, required=True, help='height: no blank')
    parser.add_argument('weight', type=int, required=True, help='weight: no blank')
    parser.add_argument('age', type=int, required=True, help='age: no blank')
    parser.add_argument('sex', type=str, required=True, help='sex: no blank')

    def post(self):
        data = UserRegister.parser.parse_args()

        if User.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400

        user = User(**data)
        user.save_to_db()
        return {'message': 'User created succesfully'}, 201


info_dict = {
    "male": 5,
    "female": -161,
    "no_activity": 1.2,
    "light_activity": 1.375,
    "moderate_activity": 1.55,
    "very_active": 1.725,
    "loose_weight": 0.8,
    "gain_weight": 1.2,
    "maintain_weight": 1,

    "loose_weight_protein": 2.5,
    "gain_weight_protein": 2,
    "maintain_weight_protein": 2.2,
    "loose_weight_fat": 0.2,
    "gain_weight_fat": 0.25,
    "maintain_weight_fat": 0.22,

    "protein": 4.0,
    "fat": 9.0,
    "carbs": 4.0
}

quantity_dic = {
    "cup": 225,
    "cups": 225,
    "tablespoon": 15,
    "tablespoons": 15,
    "ounce": 30,
    "ounces": 30,
    "teaspoon": 5,
    "teaspoons": 5,
    "pound": 450,
    "pounds": 450,
    "tsp": 5,
    "oz": 30,
    "tbs": 15,
    "lb": 450
}

food_stopwords = ['and', 'or', 'chopped', 'fresh', 'of', ',', 'into', 'cut', 'for', 'sliced',
                  'to', 'whole', 'the', '\xbd', 'red', 'finely', 'large', 'small', 'peeled', 'a',
                  'as', 'in', 'leaves', 'with', '-', 'about', 'crushed', 'peeled', '.', 'if',
                  'from', 'at', 'needed', 'on', "stick", "cold"]


REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
GOOD_SYMBOLS_RE = re.compile('[^a-z #+_]')


def clean_ingredient(ingredient):
    text = ingredient.lower()
    text = re.sub(REPLACE_BY_SPACE_RE, " ", text)
    text = re.sub(GOOD_SYMBOLS_RE, "", text)
    text = " ".join([word for word in text.split(" ") if word not in food_stopwords+list(quantity_dic.keys())])
    return re.sub(' +', ' ', text).strip()


def get_calories(weight, height, age, sex, activity, goal):
    basic_ree = (((10 * weight) + (6.25 * height) - (5 * age) \
                + info_dict[sex]) \
                * info_dict[activity]) \
                * info_dict[goal]
    return basic_ree


def get_macros(weight, height, age, sex, activity, goal):
    calories = get_calories(weight, height, age, sex, activity, goal)

    protein_grams = (weight * info_dict[goal + "_protein"])
    protein_cal = protein_grams * info_dict["protein"]

    fat_cal = (calories * info_dict[goal + "_fat"])
    fat_grams = fat_cal / info_dict['fat']

    carbs_grams = (calories - protein_cal - fat_cal) / info_dict['carbs']

    return protein_grams, fat_grams, carbs_grams
