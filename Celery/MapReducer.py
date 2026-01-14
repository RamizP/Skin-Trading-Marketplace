
import time


def params_to_str(function_name, *args, **kwargs):
    args_str = ' '.join(repr(arg) for arg in args)
    kwargs_str = ' '.join(f"{key}={repr(value)}" for key, value in sorted(kwargs.items()))
    return f"{function_name} | args: {args_str} | kwargs: {kwargs_str}"

results = {}
def cache_deco(func):
    def wrapper(*args, **kwargs):
        key = params_to_str(func.__name__, *args, **kwargs)
        if results.get(key):
            return results[key]
        time.sleep(3)
        print("cached")
        res = func(*args, **kwargs)
        results[key] = res
        return res
    return wrapper



limits_dict={}
def limit_deco(limit, duration):
    def wrapper(func):
        def inner(*args, **kwargs):
            if limits_dict.get(func.__name__):
                if limits_dict[func.__name__] >= limit:
                    return print("rate limit")
                limits_dict[func.__name__] += 1
            else:
                limits_dict[func.__name__] = 1
            return func(*args, **kwargs)
        return inner
    return wrapper




# @cache_deco
@limit_deco(3,10)
def my_func(num):
    return print(num)

my_func(1)
my_func(1)
my_func(1)
my_func(1)
my_func(1)
my_func(1)



class MapReducer:
    
    def __init__(self):
        self.result_dict = {}

    def map(self, text):
        text = text.split(" ")
        for word in text:
            self.emit(word)
            
    def emit(self, word):
        if self.result_dict.get(word):
            self.result_dict[word].append(1)
        else:
            self.result_dict[word] = [1]
          
    def reduce(self):
        for key, value in self.result_dict.items():
            self.result_dict[key] = sum(value)
        return self.result_dict
    
    def get_result(self):
        return self.result_dict
    
# mr = MapReducer()
# mr.map("asd asd dsa dsa ss aa dd aaa aa aa aa")
# mr.reduce()
# mr.get_result()