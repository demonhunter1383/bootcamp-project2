import os
import random

import joblib
from dataclasses import dataclass


@dataclass
class User:
    username: str
    email: str
    password: str
    login: bool
    role: str


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
                User("admin-defult", "admin-defult@gmail.com", "admin", False, 'admin')
            ]

        self._db_filename1 = os.path.join(os.path.dirname(__file__), 'db', 'questions.joblib')
        if os.path.exists(self._db_filename1):
            self.questions = joblib.load(self._db_filename1)
        else:
            self.questions = [
                Question("riazi", "2+2=?", "1-50", "2-40", "3-4", "4-40", "3")
            ]

    def add_user(self, new_user: User):
        user_exist = False
        email_exist = False
        for user in self.users:
            if new_user.username == user.username:
                user_exist = True
            if new_user.email == user.email:
                email_exist = True

        if user_exist or email_exist:
            return False
        else:
            self.users.append(new_user)
            return True

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

    def get_user_by_username(self, username):
        for user in self.users:
            if user.username == username:
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

    def get_logged_in_user(self):
        # Logic to check session or user list for the logged-in user
        for user in self.users:
            if user.login:  # Assuming login_state tracks if a user is logged in
                return user
        return None

    def get_categories(self):
        categories = []
        for question in self.questions:
            categories.append(question.category)
        categories = set(categories)
        categories = list(categories)
        return categories

    def get_questions_by_category(self, category, num_questions):
        # Filter questions by category
        category_questions = [q for q in self.questions if q.category == category]
        # Randomly select 'num_questions' questions from the category
        return random.sample(category_questions, min(num_questions, len(category_questions)))


user_manager = UserManagement()
