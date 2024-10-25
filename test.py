import joblib
from pprint import pprint

path = r"C:\Users\Kara\PycharmProjects\bootcamp_project2\db\users.joblib"

users = joblib.load(path)

pprint(users)
