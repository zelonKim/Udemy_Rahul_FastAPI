from typing import Any, Callable


text: str = "value"
pert: int = 90
temp: float = 37.5
number: int | float = 12

digits: list[int] = [1, 2, 3, 4, 5]
table_5: tuple[int, ...] = (5, 10, 15, 20, 25)
shipment: dict[str, Any] = {
    "id": 12701,
    "weight": 1.2,
    "content": "wooden table",
    "status": "in transit",
}




def root(num: int | float, exp: float = 0.5) -> float:
    return pow(num, exp)

root_25 = root(25)




class City:
    def __init__(self, name, country):
        self.name = name
        self.country = country

city1 = City("New York", "USA")
city2 = City("Paris", "France")

city1_temp: tuple[City, float] = (city1, 22.5)
city2_temp: tuple[City, float] = (city2, 16.0)




def decorator(func: Callable[[Any], None]):
    pass