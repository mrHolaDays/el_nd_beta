import os
from datetime import date, timedelta, datetime
import sqlite3

def update_home_work_table(dp_path):
    way = f"students_dbs/{dp_path}/home_works.db"
    conn = sqlite3.connect(way)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM home_work LIMIT 0")
    column_names = [description[0] for description in cur.description]
    with open(f"students_dbs/{dp_path}/lesson_list.txt", "r" , encoding="utf-8") as f:
        lesson_list = f.readlines()
        f.close
    column_names.sort()
    lesson_list.sort()
    if column_names == lesson_list:
        print("НЕ ТРЕБУЕСТСЯ ОБНОВЛЕНИЕ!")
    else:
        print(lesson_list)
        for item in lesson_list:
            if item[:-1] in column_names:
                print(f"{item[:-1]} есть")
            else:
                print(item)
                E = item[:-1]
                cur.execute(f"ALTER TABLE home_work ADD COLUMN {E} TEXT")
                conn.commit()

    conn.close

def update_db_version(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='version';")
        if cur.fetchone() is None:
            cur.execute("CREATE TABLE version (Date TEXT, Version INTEGER);")
            cur.execute("INSERT INTO version (Date, Version) VALUES (?, ?);", (datetime.now(), 1))
            conn.commit()
            conn.close()
            return 
        query = "SELECT Date, Version FROM version;"
        cur.execute(query)
        rows = cur.fetchone()
        if rows:
            date_val, version_val = rows
            if version_val is None:
                ver = 1
            else:
                ver = int(version_val) + 1
        else:
            cur.execute("INSERT INTO version (Date, Version) VALUES (?, ?);", (datetime.now(), ver))
        query = "UPDATE version SET Date = ?, Version = ?;" 
        cur.execute(query, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ver))
        conn.commit()
        conn.close()


def add_data_bases(classes_list):
    try:
        os.mkdir("students_dbs")
        print("Создана главная папка")
    except FileExistsError:
        print("Главная папка уже существует") 
    
    for item in classes_list:
        class_dir = f"students_dbs/{item}"
        try:
            os.mkdir(class_dir)
            print(f"Создана папка для {item}")
        except FileExistsError:
            print(f"Папка для {item} уже существует")

        timetable_db = f"{class_dir}/time_table.db"
        if not os.path.exists(timetable_db):
            conn = sqlite3.connect(timetable_db)
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS time_table(
                id INTEGER PRIMARY KEY,
                Monday TEXT,
                Tuesday TEXT,
                Wednesday TEXT,
                Thursday TEXT,
                Friday TEXT,
                Saturday TEXT,
                Sunday TEXT);
                """)

            for i in range(15):
                cur.execute("INSERT INTO time_table (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (None, None, None, None, None, None, None))
            conn.commit()
            conn.close()
            update_db_version(timetable_db)
            print(f"Создано расписание для {item}")
        else:
            print(f"Расписание для {item} уже существует")


        class_list_db = f"{class_dir}/class_list.db"
        if not os.path.exists(class_list_db):  
            conn = sqlite3.connect(class_list_db)
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS class_list(
                Name TEXT,
                Surname TEXT,
                Patronymic TEXT,
                Login TEXT);                 
                """)
            conn.commit()
            conn.close()
            update_db_version(class_list_db)
            print(f"Создан список класса {item}")
        else:
           print(f"Список класса для {item} уже существует")
        home_work_db = f"{class_dir}/home_works.db"
        conn = sqlite3.connect(home_work_db)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS home_work(Date TEXT);""")
        start_date = date(date.today().year, 1, 1) 
        end_date = date(date.today().year, 12, 31)
        val2 = ""
        current_date = start_date
        while current_date <= end_date:
            val2 = current_date.strftime("%Y-%m-%d")
            current_date += timedelta(days=1)
            cur.execute("""INSERT INTO home_work (Date) VALUES (?)""", (val2,))
        conn.commit()
        conn.close()
        update_db_version(home_work_db)



def time_table_add(info):
    try:
        conn = sqlite3.connect(f"students_dbs/{info[0]}/time_table.db")
        cur = conn.cursor()
       
        day = info[1]
        lesson_number = info[2] 
        lesson_name = info[3]

        update_query = f"UPDATE time_table SET {day} = ? WHERE id = {lesson_number};" 
       
        cur.execute(update_query, (lesson_name,)) 

        conn.commit()

        try:
            with open(f"students_dbs/{info[0]}/lesson_list.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lesson_name + "\n" in lines:
                    print(f"{lesson_name} уже есть")
                    f.close()
                else:         
                    with open(f"students_dbs/{info[0]}/lesson_list.txt", "a", encoding="utf-8") as f: 
                        f.write(lesson_name + "\n")
                        print(f"{lesson_name} добавлена")
                        f.close()
        except:
            with open(f"students_dbs/{info[0]}/lesson_list.txt", "a", encoding="utf-8") as f: 
                        f.write(lesson_name + "\n")
                        print(f"{lesson_name} добавлена")
                        f.close()
        if cur.rowcount > 0:
            print(f"Успешно обновлено {cur.rowcount} строк(а)")
            return True
        else:
            print("Не удалось обновить ни одной строки.")
            return False
    
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        return False
    finally:
        if conn:
            conn.close()
            update_home_work_table(info[0])

def add_user(info):
    conn = None
    try:
        conn = sqlite3.connect("logins.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            login TEXT UNIQUE,
            password TEXT,
            role TEXT,
            info TEXT);
            """)
        conn.commit()
        try:
            cursor.execute("INSERT INTO users (login, password, role, info) VALUES (?, ?, ?, ?)", (info[0], info[1], info[2], info[3]))
            conn.commit()
            
            print("Пользователь успешно добавлен.")

            conn.close()
            
            if info[2] == "student":
                with open(f"students_dbs/{info[3]}/lesson_list.txt", "r", encoding="utf-8") as f:
                    lessons_list = f.readlines()
                    f.close()
                    val = "?, "
                    strs = "Дата TEXT, \n"
                    strs2 = "Дата, "
                    val2 = ["01.01"]
                for item in lessons_list:
                    item = item.strip()
                    strs += f"{item} TEXT,\n"
                    strs2 += f"{item}, "
                    val += "?, "
                    val2.append(None) 

                strs = strs[:-2]
                strs2 = strs2[:-2]
                val = val[:-2]
                print(val2)
                print(val)
                print(strs2)
                print(strs)
                ins = f"""INSERT INTO marks ({strs2}) VALUES ({val})"""
                e = f"""CREATE TABLE IF NOT EXISTS marks({strs});"""
                conn = sqlite3.connect(f"students_dbs/{info[3]}/{info[0]}.db")
                cur = conn.cursor()
                cur.execute(e)
                conn.commit()
                start_date = date(date.today().year, 1, 1)  
                end_date = date(date.today().year, 12, 31) 

                current_date = start_date
                while current_date <= end_date:
                    val2[0] = current_date.strftime("%Y-%m-%d")
                    current_date += timedelta(days=1)
                    cur.execute(ins, (val2))
                cur.execute(ins, (val2))
                conn.commit()
                conn.close()
                conn = sqlite3.connect(f"students_dbs/{info[3]}/class_list.db")
                cur = conn.cursor()
                cur.execute(F"""INSERT INTO class_list(Name, Surname, Patronymic, Login) VALUES (?, ?, ?, ?)""", (info[4], info[5], info[6], info[0]))
                conn.commit()
                conn.close()       

        except sqlite3.IntegrityError:
            print(f"Ошибка: Пользователь с логином {info[0]} уже существует.")
            conn.rollback()         
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении пользователя: {e}")


def add_mark(info):
    way = f"students_dbs/{info[0]}/{info[1]}.db"
    conn = sqlite3.connect(way)
    cur = conn.cursor()
    cur.execute(f"UPDATE marks SET {info[2]} = ? WHERE Дата = ?;", (info[4], info[3]))
    conn.commit()
    conn.close()

# e = ["A1", "A2","b1"]
# add_data_bases(e)
f = ['A2', 'Wednesday', 2, 'Математика']
# time_table_add(f)
# i = ['stud1', 'pas1234', 'student', '1А', "Семён", "Глухов", "Андреевич"]
# add_user(i)
n = ['1А', 'stud1', 'Математика', '2025-01-07', "5"]
# update_home_work_table(f[0])
add_mark(n)