from searchService import SearchService

api = SearchService()
def calcNutrientsForEntry(foodId, servingId, quantity):
    food = api.getFoodById(foodId)
    myServing = None
    for serv in food['servings']['serving']:
        if serv['serving_id'] == servingId:
            myServing = serv
            return (float(myServing['calories']) * quantity, float(myServing['protein']) * quantity, float(myServing['fat']) * quantity, float(myServing['carbohydrate']) * quantity)

def addIngredientToMeal(mealId, foodId, servingId, quantity):
    pass


print("\nkcal, protein, fat, carbs")
print(calcNutrientsForEntry(794, '733', 1))
