from sqlite3 import Error
from connect import create_connection, database

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)

def select_tasks_by_user(conn, user_id):
    """Отримати всі завдання певного користувача."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    return cur.fetchall()

def select_tasks_by_status(conn, status):
    """Вибрати завдання за певним статусом."""
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tasks
        WHERE status_id = (
            SELECT id FROM status WHERE name = ?
        )
    """, (status,))
    return cur.fetchall()

def update_task_status(conn, task_id, new_status):
    """Оновити статус конкретного завдання."""
    cur = conn.cursor()
    cur.execute("""
        UPDATE tasks SET status_id = (
            SELECT id FROM status WHERE name = ?
        ) WHERE id = ?
    """, (new_status, task_id))
    conn.commit()

def select_users_with_no_tasks(conn):
    """Отримати список користувачів, які не мають жодного завдання."""
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM users
        WHERE id NOT IN (SELECT user_id FROM tasks)
    """)
    return cur.fetchall()

def add_task(conn, title, description, status_id, user_id):
    """Додати нове завдання для конкретного користувача."""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (title, description, status_id, user_id) 
        VALUES (?, ?, ?, ?)
    """, (title, description, status_id, user_id))
    conn.commit()

def select_incomplete_tasks(conn):
    """Отримати всі завдання, які ще не завершено."""
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tasks
        WHERE status_id <> (SELECT id FROM status WHERE name = 'completed')
    """)
    return cur.fetchall()

def delete_task(conn, task_id):
    """Видалити конкретне завдання."""
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

def select_users_by_email(conn, email_pattern):
    """Знайти користувачів з певною електронною поштою."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email LIKE ?", (email_pattern,))
    return cur.fetchall()

def update_user_name(conn, user_id, new_name):
    """Оновити ім'я користувача."""
    cur = conn.cursor()
    cur.execute("UPDATE users SET fullname = ? WHERE id = ?", (new_name, user_id))
    conn.commit()

def count_tasks_by_status(conn):
    """Отримати кількість завдань для кожного статусу."""
    cur = conn.cursor()
    cur.execute("""
        SELECT status.name, COUNT(tasks.id) 
        FROM status 
        LEFT JOIN tasks ON status.id = tasks.status_id 
        GROUP BY status.name
    """)
    return cur.fetchall()

def select_tasks_by_user_email_domain(conn, email_domain):
    """Отримати завдання, які призначені користувачам з певною доменною частиною електронної пошти."""
    cur = conn.cursor()
    cur.execute("""
        SELECT tasks.* 
        FROM tasks 
        JOIN users ON tasks.user_id = users.id 
        WHERE users.email LIKE ?
    """, (f'%{email_domain}%',))
    return cur.fetchall()

def select_tasks_without_description(conn):
    """Отримати список завдань, що не мають опису."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE description IS NULL")
    return cur.fetchall()

def select_users_with_in_progress_tasks(conn):
    """Вибрати користувачів та їхні завдання, які є у статусі 'in progress'."""
    cur = conn.cursor()
    cur.execute("""
        SELECT users.*, tasks.* 
        FROM users 
        INNER JOIN tasks ON users.id = tasks.user_id 
        WHERE tasks.status_id = (SELECT id FROM status WHERE name = 'in progress')
    """)
    return cur.fetchall()

def count_tasks_per_user(conn):
    """Отримати користувачів та кількість їхніх завдань."""
    cur = conn.cursor()
    cur.execute("""
        SELECT users.*, COUNT(tasks.id) 
        FROM users 
        LEFT JOIN tasks ON users.id = tasks.user_id 
        GROUP BY users.id
    """)
    return cur.fetchall()

if __name__ == '__main__':
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
     id integer PRIMARY KEY AUTOINCREMENT,
     fullname varchar(100),
     email varchar(100) UNIQUE
    );
    """

    sql_create_status_table = """
    CREATE TABLE IF NOT EXISTS status (
     id integer PRIMARY KEY AUTOINCREMENT,
     name text varchar(50) UNIQUE
    );
    """

    sql_create_tasks_table = """
    CREATE TABLE IF NOT EXISTS tasks (
     id integer PRIMARY KEY AUTOINCREMENT,
     title varchar(100),
     description text,
     status_id integer,
     user_id integer,
     FOREIGN KEY (status_id) REFERENCES status (id),
     FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """

    with create_connection(database) as conn:
        if conn is not None:
            # Створити таблиці
            create_table(conn, sql_create_users_table)
            create_table(conn, sql_create_status_table)
            create_table(conn, sql_create_tasks_table)

            # Приклади використання функцій
            print("Отримати завдання користувача з ID 1:")
            tasks_user_1 = select_tasks_by_user(conn, 1)
            print(tasks_user_1)

            print("\nВибрати завдання зі статусом 'new':")
            tasks_new = select_tasks_by_status(conn, 'new')
            print(tasks_new)

            print("\nОновити статус завдання з ID 1 на 'in progress':")
            update_task_status(conn, 1, 'in progress')

            print("\nСписок користувачів без завдань:")
            users_no_tasks = select_users_with_no_tasks(conn)
            print(users_no_tasks)

            print("\nДодати нове завдання:")
            add_task(conn, 'Нове завдання', 'Опис нового завдання', 1, 1)

            print("\nЗавдання, що не завершено:")
            incomplete_tasks = select_incomplete_tasks(conn)
            print(incomplete_tasks)

            print("\nВидалити завдання з ID 1:")
            delete_task(conn, 1)

            print("\nКористувачі з електронною поштою, що містить '@example.com':")
            users_by_email = select_users_by_email(conn, '%@example.com')
            print(users_by_email)

            print("\nОновити ім'я користувача з ID 1:")
            update_user_name(conn, 1, 'Новий Ім\'я')

            print("\nКількість завдань для кожного статусу:")
            tasks_count_by_status = count_tasks_by_status(conn)
            print(tasks_count_by_status)

            print("\nЗавдання, призначені користувачам з доменною частиною електронної пошти '@example.com':")
            tasks_by_email_domain = select_tasks_by_user_email_domain(conn, 'example.com')
            print(tasks_by_email_domain)

            print("\nЗавдання без опису:")
            tasks_without_description = select_tasks_without_description(conn)
            print(tasks_without_description)

            print("\nКористувачі з завданнями у статусі 'in progress':")
            users_in_progress_tasks = select_users_with_in_progress_tasks(conn)
            print(users_in_progress_tasks)

            print("\nКористувачі та кількість їхніх завдань:")
            users_and_task_count = count_tasks_per_user(conn)
            print(users_and_task_count)
        else:
            print("Error! Cannot create the database connection.")
