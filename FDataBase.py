import time
import math
import sqlite3


class FDataBase:
    def __init__(self, db):  # Ссылка на связь с базой данных
        self.__db = db  # Созраняем в экземпляре класса
        # Создаем класс курсора. С помощью экземаляра класса курсова и работаем с БД
        self.__cur = db.cursor()

    # Метод выборки всех записей из таблицы статусов документа
    def getMenu(self):
        try:
            self.__cur.execute(
                f"SELECT * FROM statuses"
            )
            res = self.__cur.fetchall()  # Считываем все записи
            if res:
                return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addTask(self, subject, description, user_id):
        # Пытаемся добавить данные в БД
        try:
            tm = math.floor(time.time())  # Текущее время добавления статьи
            status_id_temp = 1  # По умолчанию статус "Новая" задача
            self.__cur.execute("INSERT INTO tasks VALUES(NULL, ?, ?, ?, ?)",
                               (subject, description, tm, status_id_temp))
            last_row_id = self.__cur.lastrowid
            user_status_change_temp = user_id
            # Добавление данных в log_task_statuses после присвоеяния новой задаче id
            self.__cur.execute("INSERT INTO log_task_statuses VALUES(NULL, ?, ?, ?, ?)",
                               (user_status_change_temp, last_row_id, status_id_temp, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False

        return True

    def getPost(self, postId):
        try:
            self.__cur.execute(
                f"SELECT subject, description, status_id, id FROM tasks WHERE id = {postId} LIMIT 1")
            res = self.__cur.fetchone()  # Получить одну запись
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def loginUser(self, email, psw):
        try:
            res = self.__cur.execute(
                f"SELECT id, name, surname FROM users WHERE email = '{email}' AND password = {psw}")
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(
                f"SELECT id, subject, description, creation_date FROM tasks ORDER BY creation_date DESC")
            res = self.__cur.fetchall()  # Получить все записи
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def getAllTasks(self, namestatmytasks):
        try:
            namestatmytasks='/'+namestatmytasks
            print('namestatmytasks = ', namestatmytasks)
            self.__cur.execute(
                f"SELECT id, subject, description, creation_date FROM tasks WHERE status_id=(SELECT id FROM statuses WHERE url='{namestatmytasks}') ORDER BY creation_date DESC")
            res = self.__cur.fetchall()  # Получить все записи
            print('res = ', res)
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def getMyTasks(self, namestatmytasks, user_id):
        try:
            namestatmytasks='/'+namestatmytasks
            print('namestatmytasks = ', namestatmytasks)
            self.__cur.execute(
                f"SELECT tasks.id, tasks.subject, tasks.description, tasks.creation_date, tasks.status_id FROM tasks JOIN log_task_statuses ON tasks.id=log_task_statuses.task_id and log_task_statuses.user_status_change_id={user_id} and tasks.status_id=(SELECT id FROM statuses WHERE url='{namestatmytasks}') GROUP by task_id ORDER BY log_task_statuses.date_status DESC")
                # f"SELECT id, subject, description, creation_date FROM tasks WHERE status_id=(SELECT id FROM statuses WHERE url='{namestatmytasks}') AND  ORDER BY creation_date DESC")
            res = self.__cur.fetchall()  # Получить все записи
            print('res = ', res)
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def addTakeDocWorkTake(self, task_id, status_id, user_id):
        try:
            tm = math.floor(time.time())
            self.__cur.execute(
                f"UPDATE tasks SET status_id = 2 WHERE id = {task_id}")
            # Добавление данных в log_task_statuses после присвоеяния новой задаче id
            # status_id = 2  # Переводим задачу в статус "В работе"

            self.__cur.execute("INSERT INTO log_task_statuses VALUES(NULL, ?, ?, ?, ?)",
                               (user_id, task_id, status_id, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка перевода задачи в статус \"В работе\" " + str(e))
            return False

        return True
