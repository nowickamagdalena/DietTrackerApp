from fatsecret import Fatsecret

#class for searching food using fat secret api
class SearchService:
    #keys below have been generated for project owner email and shouldn't be used by other developers
    DEFAULT_CONSUMER_KEY = '3ff7ca99e0fe438b9fae36e5b099666b'
    DEFAULT_CONSUMER_SECRET ='d3c02e434d5e4755a2df887363b76017'

    def __init__(self, consumer_key=DEFAULT_CONSUMER_KEY, consumer_secret=DEFAULT_CONSUMER_SECRET, maxResultsNum=50):
        self.__api = Fatsecret(consumer_key, consumer_secret) 
        self.__maxResultsNum = maxResultsNum
    
    #function for searching food by key words
    def searchFood(self, foodName):
        try:
            foods = self.__api.foods_search(foodName, max_results=self.__maxResultsNum)
            return foods
        except KeyError:
            print("No results matching: ", foodName)
            return []
    
    #function for searching food by id from fat secret database
    def getFoodById(self, foodId):
        food = self.__api.food_get(foodId)        
        return food
    
    #function for searching food servings by id from fat secret database
    def getFoodServings(self, foodId):
        servings = self.__api.food_get(foodId)['servings']['serving']
        return servings

api = SearchService()
