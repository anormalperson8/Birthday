import datetime
import json

id = "id"
month = "month"
day = "day"
year = "year"


def turn_to_english(number):
    x = datetime.datetime(1, number, 1).strftime("%B")
    return x


def get_date(user_id):
    f = open("/home/sunny/PythonBday/data/bday.json", 'r')
    data = json.load(f)
    for people in data["people"]:
        if people[id] == user_id:
            return datetime.datetime(people[year], people[month], people[day])
    return None


# debug print
# print(get_date(1117746108161081344).strftime("%Y"))
# print(datetime.datetime.now())


