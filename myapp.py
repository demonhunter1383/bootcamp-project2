from flask import Flask, render_template, redirect, url_for, request
from flask_login import login_required
# from Questions import question_manager, Question
from forms import Login, SignUp
from user_management import user_manager, User, Question

app = Flask(__name__)
app.secret_key = '935232e83c80bd5c3d3b7a8b397d85c14af5f6c9369d6d3f9c0ca4263e61332a'


@app.route('/home/profile')
def profile():
    if user_manager.current_user is not None and user_manager.current_user.login:
        return render_template('profile.html', current_user=user_manager.current_user)
    else:
        return redirect(url_for('login'))


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
            user = User(email=email, username=username, password=password, login=False, role='admin')
        else:
            user = User(email=email, username=username, password=password, login=False, role='user')

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


if __name__ == '__main__':
    app.run(port=8080)
