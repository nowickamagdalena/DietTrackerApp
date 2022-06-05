from fatsecret import Fatsecret

#class for searching food using fat secret api
class SearchService:
    DEFAULT_CONSUMER_KEY = 'paste your consumer key here'
    DEFAULT_CONSUMER_SECRET ='paste you secret key here'

    def __init__(self, consumer_key=DEFAULT_CONSUMER_KEY, consumer_secret=DEFAULT_CONSUMER_SECRET, maxResultsNum=50):
        self.api = Fatsecret(consumer_key, consumer_secret) 
        self.maxResultsNum = maxResultsNum
    
    @property
    def maxResultsNum(self):
        return self.__maxResultsNum

    @maxResultsNum.setter
    def maxResultsNum(self, new_num):
        if isinstance(new_num, int):
            if new_num >= 0:
                self.__maxResultsNum = new_num
            else:
                raise ValueError("Maximum results number must not be negative")
        else:
            raise TypeError("Maximum results number must be of type int")
    
    @property
    def api(self):
        return self.__api
    
    @api.setter
    def api(self, new_api):
        if isinstance(new_api, Fatsecret):
            self.__api = new_api
        else:
            raise TypeError("Api must be an instance of the Fatsecret class.")

    #function for searching food by key words
    def searchFood(self, foodName):
        try:
            foods = self.__api.foods_search(foodName, max_results=self.maxResultsNum)
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

