from fatsecret import Fatsecret

class SearchService:
    DEFAULT_CONSUMER_KEY = '3ff7ca99e0fe438b9fae36e5b099666b'
    DEFAULT_CONSUMER_SECRET ='d3c02e434d5e4755a2df887363b76017'

    def __init__(self, consumer_key=DEFAULT_CONSUMER_KEY, consumer_secret=DEFAULT_CONSUMER_SECRET, maxResultsNum=50,):
        self.__api = Fatsecret(consumer_key, consumer_secret) 
        self.__maxResultsNum = maxResultsNum
    
    def searchFood(self, foodName):
        try:
            foods = self.__api.foods_search(foodName, max_results=self.__maxResultsNum)
            return foods
        except KeyError:
            print("No results matching: ", foodName)
            return []
    
    def getFoodById(self, foodId):
        food = self.__api.food_get(foodId)        
        return food
    def getFoodServings(self, foodId):
        servings = self.__api.food_get(foodId)['servings']['serving']
        return servings

api = SearchService()
# print(api.searchFood("bread roll"))
# print(api.getFoodById(52548))
# print("\n")
# for serv in api.getFoodServings(52548):
#     print(serv['serving_description'])
