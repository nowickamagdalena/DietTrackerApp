from app.models import Ingredient
from .searchService import SearchService

#class for counting calories and other nutrients of different food got from fat secret api
class CalorieCounter:

    def __init__(self, api) :
        self.api = api
    
    @property
    def api(self):
        return self.__api
        
    @api.setter
    def api(self, new_api):
        if isinstance(new_api, SearchService):
            self.__api = new_api
        else:
            raise TypeError("Api must be an instance of the SearchService class.")


    #function calculating calories, fat, protein and carbohydrates for given food id, serving id and quantity
    def calcNutrientsForServing(self, foodid, servingid, quantity):
        result = self.api.getFoodById(foodid)
        myServing = None
        servings = result['servings']['serving']
        if type(servings) != list:
            servings = [servings]
        for serv in servings:
            if serv['serving_id'] == servingid:
                myServing = serv
                return {'calories': round(float(myServing['calories']) * float(quantity), 2), "protein":round(float(myServing['protein']) * float(quantity), 2),
                    "fat": round(float(myServing['fat']) * float(quantity), 2), "carbohydrate": round(float(myServing['carbohydrate']) * float(quantity), 2)}

    #function calculating calories, fat, protein and carbohydrates for given food item from database
    def calcNutrientsForFood(self, food):
        result = self.api.getFoodById(food.food_id)
        myServing = None
        servings = result['servings']['serving']
        if type(servings) != list:
            servings = [servings]
        for serv in servings:
            if serv['serving_id'] == food.serving_id:
                myServing = serv
                return {'calories' :round(float(myServing['calories']) * food.quantity, 2), "protein":round(float(myServing['protein']) * food.quantity, 2),
                    "fat": round(float(myServing['fat']) * food.quantity, 2), "carbohydrate": round(float(myServing['carbohydrate']) * food.quantity, 2)}

    #function calculating sum of calories, fat, protein and carbohydrates for given list of food items from database
    def calcNutrientsForMeal(self, foodList):
        meal_nutrients={"calories": 0, "protein": 0, "fat": 0, "carbohydrate": 0}
        foods_nutr ={}
        for food in foodList:
            nutrients = self.calcNutrientsForFood(food)
            foods_nutr[food.food_id] = nutrients
            meal_nutrients['calories'] += nutrients['calories']
            meal_nutrients['protein'] += nutrients['protein']
            meal_nutrients['fat'] += nutrients['fat']
            meal_nutrients['carbohydrate'] += nutrients['carbohydrate']
        return {'meal_sum': meal_nutrients, 'foods_sum': foods_nutr}

   #function calculating sum of calories, fat, protein and carbohydrates for given list of meal items from database
    def calcNutrientsForDay(self, mealList):
        day_nutrients={"calories": 0, "protein": 0, "fat": 0, "carbohydrate": 0}
        meals_nutrients={}
        for meal in mealList:
            ingredients = Ingredient.query.filter_by(meal=meal.id).all()
            meal_nutr = self.calcNutrientsForMeal(ingredients)
            meals_nutrients[meal.type] = meal_nutr['meal_sum']

            day_nutrients['calories'] += meal_nutr['meal_sum']['calories']
            day_nutrients['protein'] += meal_nutr['meal_sum']['protein']
            day_nutrients['fat'] += meal_nutr['meal_sum']['fat']
            day_nutrients['carbohydrate'] += meal_nutr['meal_sum']['carbohydrate']
        return {"day_sum": day_nutrients, "meals_sum": meals_nutrients}
        

