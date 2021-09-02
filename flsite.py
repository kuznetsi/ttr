import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
# Подключение внешнего файла для управления базой данных
from FDataBase import FDataBase


# Конфигурация
DATABASE = 'ttr.db'
DEBUG = True  # Режим отладки
SECRET_KEY = 'xhaksjdhakjsbasjqwe,jhv'

app = Flask(__name__)

# Загружаем файл настройки подключения к БД из текущего файла
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'ttr.db')))
app.config['SECRET_KEY'] = 'secret_key_for_sessions'


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row  # Записи из БД буду представлены в виде словаря
    return conn


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):  # Проверяем наличие свойства link_db у g
        # Если свойства нет, то устанавливаем соединение
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.route("/index")
@app.route("/")
def index():
    if 'userLogged' not in session:
        return redirect(url_for('login'))
    return render_template('index.html',
                           menu=dbase.getMenu(),
                           posts=dbase.getPostsAnonce(),
                           user_id=session['userLogged'],
                           nameuser=session['userName'],
                           namesurname=session['userSurname']
                           )


# Обработчик формы, где будет отображаться форма для добавления задачи
@app.route("/add_task", methods=["POST", "GET"])
def addTask():
    if 'userLogged' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        # name - заголовок статьи
        # post - содержимое статьи
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            # Передаем в метод addTask заголовок и текст статьи
            res = dbase.addTask(request.form['name'], request.form['post'], session['userLogged'])
            # Проверка передачи данных о статье в addTask
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добаления статьи', category='error')
    return render_template('add_task.html', menu=dbase.getMenu(), title="Добавление статьи")


# Обработчик отображения информации о задаче
@app.route("/post/<int:id_post>")
def showPost(id_post):
    title, post, status_post_id, task_id = dbase.getPost(id_post)
    if not title:
        abort(404)

    return render_template('post.html',
                           menu=dbase.getMenu(),
                           title=title,
                           post=post,
                           task_id=task_id,
                           status_post_id=status_post_id,
                           user_id=session['userLogged'],
                           nameuser=session['userName'],
                           namesurname=session['userSurname']
                           )


# Обработчик отображения информации о всех задачах
@app.route("/<namestatmytasks>")
def showAllTasks(namestatmytasks):
    return render_template('mytasks.html',
                           menu=dbase.getMenu(),
                           tasks=dbase.getAllTasks(namestatmytasks),
                           user_id=session['userLogged'],
                           nameuser=session['userName'],
                           namesurname=session['userSurname']
                           )

# Обработчик отображения информации о моих задачах


@app.route("/mytasks/<namestatmytasks>")
def showMyTasks(namestatmytasks):
    return render_template('mytasks.html',
                           menu=dbase.getMenu(),
                           tasks=dbase.getMyTasks(
                               namestatmytasks, session['userLogged']),
                           user_id=session['userLogged'],
                           nameuser=session['userName'],
                           namesurname=session['userSurname']
                           )


@app.route("/login", methods=["POST", "GET"])
def login():
    # Если пользователь авторизовался и есть свойство в сессии userLogged
    if 'userLogged' in session:
        # Переадресуем в соответствующий профайл сессии
        return redirect(url_for('profile', user_id=session['userLogged']))
    elif request.method == 'POST' and request.form['email'] != "" and request.form['psw'] != "":
        res = dbase.loginUser(request.form['email'], request.form['psw'])
        for user in res:
            user_id = user['id']
            nameuser = user['name']
            namesurname = user['surname']
        session['userLogged'] = user_id
        session['userName'] = nameuser
        session['userSurname'] = namesurname
        return redirect(url_for('profile',
                                user_id=session['userLogged'],
                                nameuser=session['userName'],
                                namesurname=session['userSurname']))
    msgs = "Авторизация"
    return render_template('login.html',
                           title="Авторизация",
                           # menu=dbase.getMenu(),
                           msgs=msgs)


# Завершение подключения к БД
@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/about")
def about():
    print(url_for('about'))
    return render_template('about.html', title="О сайте", menu=dbase.getMenu())


@app.route("/profile/<int:user_id>")
def profile(user_id):
    # Проверка пользователя на доступ именно к своему профилю
    if 'userLogged' not in session or session['userLogged'] != user_id:
        # Перекидываем на страницу ошибки доступа
        print("Перекидываем на страницу ошибки доступа")
        abort(401)

    # return f"Пользователь пользователя: {username}"
    return render_template('index.html', menu=dbase.getMenu(),
                           posts=dbase.getPostsAnonce(),
                           user_id=session['userLogged'],
                           nameuser=session['userName'],
                           namesurname=session['userSurname'])


@app.route("/post/<int:id_post>/takeDocWorkTake", methods=["POST", "GET"])
def takeDocWorkTake(id_post):
    title, post, status_post_id, task_id = dbase.getPost(id_post)
    print("Нажата кнопка смены статуса")
    print("title=", title)
    print("post=", post)
    print("task_id=", task_id)

    print("status_id=", request.form['select_status'])
    # print("user_id=", user_id)

    task_id = id_post
    status_id = status_post_id
    user_id = session['userLogged']

    print("Нажата кнопка смены статуса")
    print("task_id=",task_id)
    print("status_id=",status_id)
    print("status_id=", request.form['select_status'])
    print("user_id=", user_id)

    # request.form['email']

    # res = dbase.addTakeDocWorkTake(task_id, status_id, user_id)

    res = dbase.addTakeDocWorkTake(task_id, request.form['select_status'], user_id)

    if res:
        flash("Вы взяли в работу задачу", "success")
        return redirect(url_for('index'))
    else:
        flash("Ошибка ошибка смены статуса задачи", "error")
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


# Если указать "/profile/<path:username" - то это говорит о том, что все что идет после
# profile, необходимо посместить в username (для более глубокого URL)


@app.route("/logout")
def logout():
    if 'userLogged' in session:
        session.pop('userLogged', None)  # удаление данных о посещениях
        msgs = "Вы больше не авторизованы!"
    else:
        msgs = "Вам необходимо авторизоваться!"

    return render_template('login.html', title="Авторизация", menu=dbase.getMenu(), msgs=msgs)

# Пользовательский фильтр для перевода даты
# Использование {{p.creation_date | ctime }}


@app.template_filter('ctime')
def timectime(s):
    return datetime.utcfromtimestamp(s).strftime('%d.%m.%Y %H:%M:%S')


# Обработчик ошибок
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title="Страница не найдена", menu=dbase.getMenu())


# Запуск локального web-сервера + ошибки
if __name__ == "__main__":
    app.run(debug=True)

# SELECT log_task_statuses.user_status_change_id, tasks.subject, users.name, statuses.name
# FROM tasks
# JOIN log_task_statuses JOIN users JOIN statuses
# ON tasks.id = log_task_statuses.task_id AND users.id = log_task_statuses.user_status_change_id AND statuses.id = log_task_statuses.status_id
