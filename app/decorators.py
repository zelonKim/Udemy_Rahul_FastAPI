# def fence(func):
#     def wrapper(text:str):
#         print("-" * len(text))
#         func(text)
#         print("-" * len(text))
        
#     return wrapper



# @fence
# def log(text:str):
#     print(text)
    
    
# log("hello there")
# -----------
# hello there
# -----------




###################################




def custom_fence(pattern: str = "-"):
    def add_fence(func):
        def wrapper(text:str):
            print(pattern * len(text))
            func(text)
            print(pattern * len(text))
        return wrapper
    return add_fence



@custom_fence("+")
def log(text:str):
    print(text)
    
    
log("hello there")
# +++++++++++
# hello there
# +++++++++++