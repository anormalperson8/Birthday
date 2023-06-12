import datetime
import json
import os
from dotenv import load_dotenv
load_dotenv("/home/sunny/PythonBday/data/data.env")
dir = os.getenv("OLD_BDAY_PATH")

def turn_to_english(number):
    x = datetime.datetime(1, number, 1).strftime("%B")
    return x


def get_date(user_id):
    f = open(dir + "bday.json", 'r')
    data = json.load(f)
    for people in data["people"]:
        if people["id"] == user_id:
            return datetime.datetime(people["year"], people["month"], people["day"])
    return None


def set_date(user_id, year, month, day):
    fr = open(dir + "bday.json", 'r')
    data = json.load(fr)
    data_obj = []
    stat = False
    for people in data["people"]:
        if people["id"] == user_id:
            people["year"] = year
            people["month"] = month
            people["day"] = day
            stat = True
        data_obj.append(people)
    fr.close()
    obj = {"people": data_obj}
    if not stat:
        obj["people"].append({"id": user_id, "year": year, "month": month, "day": day})
    fw = open(dir + "/dummy.json", 'w')
    fw.write(json.dumps(obj, indent=4))
    fw.close()
    os.remove(dir + "bday.json")
    os.rename(dir + "dummy.json", dir + "bday.json")


def remove_date(user_id):
    fr = open(dir + "bday.json", 'r')
    data = json.load(fr)
    data_obj = []
    stat = False
    for people in data["people"]:
        if people["id"] == user_id:
            stat = True
            continue
        data_obj.append(people)
    fr.close()
    obj = {"people": data_obj}
    fw = open(dir + "/dummy.json", 'w')
    fw.write(json.dumps(obj, indent=4))
    fw.close()
    os.remove(dir + "bday.json")
    os.rename(dir + "dummy.json", dir + "bday.json")
    return stat


# debug print
# print(get_date(1117746108161081344).strftime("%Y"))
# print(datetime.datetime.now())


