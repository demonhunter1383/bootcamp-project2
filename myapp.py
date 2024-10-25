from flask import Flask, render_template, redirect, url_for, request, session
from forms import Login, SignUp
from user_management import user_manager, User, Question

app = Flask(__name__)
app.secret_key = '935232e83c80bd5c3d3b7a8b397d85c14af5f6c9369d6d3f9c0ca4263e61332a'


@app.route('/')
@app.route('/home')
def index():
    # داده‌هایی که می‌خواهید به نمودار ارسال کنید
    chart_data = {
        'labels': ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        'sales_data': [450, 200, 100, 220, 500, 100, 400, 230, 500],
        'mobile_apps_data': [50, 40, 300, 220, 500, 250, 400, 230, 500],
        'websites_data': [30, 90, 40, 140, 290, 290, 340, 230, 400]
    }

    if user_manager.current_user is not None and user_manager.current_user.login:
        return render_template('home.html', chart_data=chart_data)
    else:
        return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    my_form = SignUp()

    if my_form.validate_on_submit():
        email = my_form.email.data
        username = my_form.username.data
        password = my_form.password.data
        print(password)

        if password == 'admin':
            user = User(email=email, username=username, password=password, login=False, role='admin', quiz_history=[])
        else:
            user = User(email=email, username=username, password=password, login=False, role='user', quiz_history=[])

        can_save_user = user_manager.add_user(user)
        if can_save_user:
            user_manager.save()
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', form=my_form,
                                   msg='User already exists. Please use a different email or username.')

    return render_template('signup.html', form=my_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    my_form = Login()

    if my_form.validate_on_submit():
        username = my_form.username.data
        password = my_form.password.data

        if user_manager.is_user_exist(username, password):

            user_manager.change_login_state(username, password, True)
            user_manager.set_current_user(username, password)

            return redirect(url_for('index'))

        else:
            return render_template('login.html', form=my_form, msg='The username or password is incorrect')

    return render_template('login.html', form=my_form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if user_manager.current_user is not None:
        username = user_manager.current_user.username
        password = user_manager.current_user.password

        user_manager.change_login_state(username, password, False)
        user_manager.change_current_user_state(False)

    return redirect(url_for('login'))


@app.route('/questions')
def view_questions():
    if user_manager.current_user is not None and user_manager.current_user.login:
        questions_list = user_manager.questions  # Retrieve questions from your list
        if user_manager.current_user.role == 'admin':  # Check if the logged-in user is an admin
            return render_template('admin_questions.html', questions=questions_list)
        else:
            return render_template('user_questions.html', questions=questions_list)
    else:
        return redirect(url_for('login'))


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if user_manager.current_user.role != 'admin':
        return redirect(url_for('view_questions'))

    if request.method == 'POST':
        category = request.form['category']
        soal = request.form['soal']
        gozine1 = request.form['gozine1']
        gozine2 = request.form['gozine2']
        gozine3 = request.form['gozine3']
        gozine4 = request.form['gozine4']
        answer = request.form['answer']

        new_question = Question(category, soal, gozine1, gozine2, gozine3, gozine4, answer)
        user_manager.add_question(new_question)
        user_manager.save_questions()  # Save the updated questions list
        return redirect(url_for('view_questions'))

    return render_template('add_question.html')


@app.route('/delete_question/<soal>', methods=['POST'])
def delete_question(soal):
    if user_manager.current_user.role != 'admin':
        return redirect(url_for('view_questions'))

    for question in user_manager.questions:
        if question.soal == soal:
            user_manager.delete_question(question)
            user_manager.save_questions()  # Save the updated questions list
            break

    return redirect(url_for('view_questions'))


@app.route('/quiz_categories', methods=['GET'])
def quiz_categories():
    # Check if user is logged in
    user = user_manager.get_logged_in_user()
    if not user or not user.login:
        return redirect(url_for('login'))

    # Get the list of categories (from the database or joblib)
    categories = user_manager.get_categories()
    return render_template('quiz_categories.html', categories=categories)


@app.route('/select_question_count/<category>', methods=['GET', 'POST'])
def select_question_count(category):
    user = user_manager.get_logged_in_user()
    if not user or not user.login:
        return redirect(url_for('login'))

    if request.method == 'POST':
        num_questions = int(request.form['num_questions'])
        return redirect(url_for('start_quiz', category=category, num_questions=num_questions))

    return render_template('select_question_count.html', category=category)


@app.route('/start_quiz/<category>/<int:num_questions>', methods=['GET', 'POST'])
def start_quiz(category, num_questions):
    user = user_manager.get_logged_in_user()
    if not user or not user.login:
        return redirect(url_for('login'))

    # Get random questions from the selected category
    questions = user_manager.get_questions_by_category(category, num_questions)

    if request.method == 'POST':
        # Collect user answers and store them in the session
        answers = {f'question_{i + 1}': request.form.get(f'question_{i + 1}') for i in range(len(questions))}

        # Store user answers and questions in the session
        session['user_answers'] = answers
        session['questions'] = questions  # Store questions to validate later

        # Redirect to the results page
        return redirect(url_for('quiz_results'))

    return render_template('quiz.html', questions=questions, category=category)


@app.route('/quiz_results', methods=['GET'])
def quiz_results():
    user = user_manager.get_logged_in_user()
    if not user or not user.login:
        return redirect(url_for('login'))

    user_answers = session.get('user_answers')
    questions = session.get('questions')

    if not user_answers or not questions:
        return redirect(url_for('quiz_categories'))

    correct_count = 0
    feedback = []
    total_questions = len(questions)

    for i, question in enumerate(questions):
        correct_answer = question['answer']
        user_answer = user_answers.get(f'question_{i + 1}')
        if user_answer == correct_answer:
            correct_count += 1
            feedback.append({'question': question['soal'], 'status': 'Correct'})
        else:
            feedback.append({'question': question['soal'], 'status': 'Incorrect', 'correct_answer': correct_answer})

    score = (correct_count / total_questions) * 100

    # Save quiz result to user's profile
    user.add_quiz_result(category=questions[0]['category'], score=score)
    user_manager.save()  # Ensure this saves user data including quiz history

    return render_template('quiz_results.html', score=score, feedback=feedback, total=total_questions)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = user_manager.get_logged_in_user()
    if not user or not user.login:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Update user profile
        user.email = request.form['email']
        user_manager.save()  # Save changes to the database
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


if __name__ == '__main__':
    app.run(port=8080)
