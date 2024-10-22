import os
import joblib
from dataclasses import dataclass


@dataclass
class User:
    username: str
    email: str
    password: str
    login: bool
    role: bool  # False admin True user


@dataclass
class Question:
    category: str
    soal: str
    gozine1: str
    gozine2: str
    gozine3: str
    gozine4: str
    answer: str


class UserManagement(object):
    def __init__(self) -> None:

        self._db_filename = os.path.join(os.path.dirname(__file__), 'db', 'users.joblib')
        self.current_user = None
        if os.path.exists(self._db_filename):
            self.users = joblib.load(self._db_filename)
        else:
            self.users = [
                User("shahikian", "shahikian@gmail.com", "12345", False, True)
            ]
        self._db_filename1 = os.path.join(os.path.dirname(__file__), 'db', 'questions.joblib')

        if os.path.exists(self._db_filename1):
            self.questions = joblib.load(self._db_filename1)
        else:
            self.questions = [
                Question("riazi", "2+2=?", "1-50", "2-40", "3-4", "4-40", "3")
            ]

    def add_user(self, user: User):
        self.users.append(user)

    def save(self):
        joblib.dump(self.users, self._db_filename)

    def save_questions(self):
        joblib.dump(self.questions, self._db_filename1)

    def change_login_state(self, username, password, state=True):
        for user in self.users:
            if user.username == username and user.password == password:
                user.login = state
                break

    def set_current_user(self, username, password):
        self.current_user = self.get_user(username, password)

    def is_user_exist(self, username, password) -> bool:
        for user in self.users:
            if user.username == username and user.password == password:
                return True

        return False

    def get_user(self, username, password):

        for user in self.users:
            if user.username == username and user.password == password:
                return user

        return

    def change_current_user_state(self, state=False):
        self.current_user.login = state

    def add_question(self, question: Question):
        self.questions.append(question)

    def delete_question(self, question: Question):
        for q in self.questions:
            if q.soal == question.soal:
                self.questions.remove(question)


user_manager = UserManagement()
