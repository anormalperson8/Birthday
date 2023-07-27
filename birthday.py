import datetime
import json
import os
from dotenv import load_dotenv

path = os.path.dirname(os.path.abspath(__file__))
data_path = f"{path}/data/"
load_dotenv(f"{data_path}data.env")
os.getenv(f"{data_path}data.env")


def turn_to_english(number):
    x = datetime.datetime(1, number, 1).strftime("%B")
    return x


def get_date(user_id):
    f = open(data_path + "/bday.json", 'r')
    data = json.load(f)
    for people in data["people"]:
        if people["id"] == user_id:
            return datetime.datetime(people["year"], people["month"], people["day"])
    return None


def get_user():
    now = datetime.datetime.now()
    f = open(data_path + "bday.json", 'r')
    data = json.load(f)
    people_list = []
    stat = False
    for people in data["people"]:
        if int(people["day"]) == now.day and int(people["month"]) == now.month:
            people_list.append(int(people["id"]))
            stat = True
    if stat:
        return people_list
    return None


def set_date(user_id, year, month, day):
    fr = open(data_path + "bday.json", 'r')
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
    fw = open(data_path + "/dummy.json", 'w')
    fw.write(json.dumps(obj, indent=2))
    fw.close()
    os.remove(data_path + "bday.json")
    os.rename(data_path + "dummy.json", data_path + "bday.json")


def remove_date(user_id):
    fr = open(data_path + "bday.json", 'r')
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
    fw = open(data_path + "dummy.json", 'w')
    fw.write(json.dumps(obj, indent=2))
    fw.close()
    os.remove(data_path + "bday.json")
    os.rename(data_path + "dummy.json", data_path + "bday.json")
    return stat


def get_month(date):
    return date["month"]


def get_day(date):
    return date["day"]


def coming_birthdays():
    f = open(data_path + "bday.json", 'r')
    data = json.load(f)
    people_list = []
    for person in data["people"]:
        people_list.append(person)
    people_list.sort(key=get_day)
    people_list.sort(key=get_month)
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    count = 10
    if len(people_list) < 10:
        count = len(people_list)
    ret = []
    # Add all birthdays on/after this day
    for i in people_list:
        print(f"Object {i}")
        if count > 0:
            if i["month"] > month:
                print(f"Appended {i}")
                ret.append(i)
                count -= 1
            elif i["month"] == month and i["day"] >= day:
                print(f"Appended {i}")
                ret.append(i)
                count -= 1
        else:
            break
    if count > 0:
        for j in people_list:
            if count > 0:
                ret.append(j)
                count -= 1
            else:
                break
    return ret


def get_perm():
    a = [int(os.getenv('TEST_CHANNEL')), int(os.getenv('MODERATOR_ONLY')), int(os.getenv('BOT_STUFF'))]
    return a

