from database.connection import get_connection


def get_students(search=''):
    sql = '''SELECT id_student, last_name, first_name, middle_name, class_name
             FROM students'''
    params = []
    if search:
        sql += ''' WHERE LOWER(last_name || ' ' || first_name || ' ' || COALESCE(middle_name,'') || ' ' || class_name)
                   LIKE LOWER(%s)'''
        params.append(f'%{search}%')
    sql += ' ORDER BY class_name, last_name, first_name'
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def get_student(student_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id_student,last_name,first_name,middle_name,class_name FROM students WHERE id_student=%s', (student_id,))
            return cursor.fetchone()


def save_student(student_id, last_name, first_name, middle_name, class_name):
    values = (last_name.strip(), first_name.strip(), middle_name.strip() or None, class_name.strip())
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if student_id:
                cursor.execute('''UPDATE students SET last_name=%s, first_name=%s, middle_name=%s, class_name=%s
                                  WHERE id_student=%s''', (*values, student_id))
            else:
                cursor.execute('''INSERT INTO students(last_name,first_name,middle_name,class_name)
                                  VALUES(%s,%s,%s,%s) RETURNING id_student''', values)
                student_id = cursor.fetchone()[0]
        connection.commit()
    return int(student_id)


def delete_student(student_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM students WHERE id_student=%s', (student_id,))
        connection.commit()


def get_parents(search=''):
    sql = '''SELECT id_parent,last_name,first_name,middle_name,phone,email FROM parents'''
    params=[]
    if search:
        sql += ''' WHERE LOWER(last_name || ' ' || first_name || ' ' || COALESCE(middle_name,'') || ' ' || phone || ' ' || email)
                   LIKE LOWER(%s)'''
        params.append(f'%{search}%')
    sql += ' ORDER BY last_name, first_name'
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def get_parent(parent_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id_parent,last_name,first_name,middle_name,phone,email FROM parents WHERE id_parent=%s',(parent_id,))
            return cursor.fetchone()


def save_parent(parent_id,last_name,first_name,middle_name,phone,email):
    values=(last_name.strip(),first_name.strip(),middle_name.strip() or None,phone.strip(),email.strip())
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if parent_id:
                cursor.execute('''UPDATE parents SET last_name=%s,first_name=%s,middle_name=%s,phone=%s,email=%s
                                  WHERE id_parent=%s''',(*values,parent_id))
            else:
                cursor.execute('''INSERT INTO parents(last_name,first_name,middle_name,phone,email)
                                  VALUES(%s,%s,%s,%s,%s) RETURNING id_parent''',values)
                parent_id=cursor.fetchone()[0]
        connection.commit()
    return int(parent_id)


def delete_parent(parent_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM parents WHERE id_parent=%s',(parent_id,))
        connection.commit()


def get_parent_students(parent_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT sp.id_student, s.last_name, s.first_name, s.middle_name, s.class_name, sp.relationship
                              FROM student_parents sp
                              JOIN students s ON s.id_student=sp.id_student
                              WHERE sp.id_parent=%s
                              ORDER BY s.class_name, s.last_name, s.first_name""", (parent_id,))
            return cursor.fetchall()


def save_parent_student(parent_id, student_id, relationship):
    relationship=(relationship or 'родитель').strip()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO student_parents(id_student,id_parent,relationship)
                              VALUES(%s,%s,%s)
                              ON CONFLICT (id_student,id_parent)
                              DO UPDATE SET relationship=EXCLUDED.relationship""",
                           (int(student_id), int(parent_id), relationship))
        connection.commit()


def delete_parent_student(parent_id, student_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM student_parents WHERE id_parent=%s AND id_student=%s',
                           (int(parent_id), int(student_id)))
        connection.commit()


def get_tags(search=''):
    sql='''SELECT t.id_tag,t.uid,t.status,t.id_student,s.last_name,s.first_name,s.class_name
           FROM tags t JOIN students s ON s.id_student=t.id_student'''
    params=[]
    if search:
        sql += ''' WHERE LOWER(t.uid || ' ' || s.last_name || ' ' || s.first_name || ' ' || s.class_name) LIKE LOWER(%s)'''
        params.append(f'%{search}%')
    sql += ' ORDER BY t.id_tag DESC'
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql,params)
            return cursor.fetchall()


def get_tag(tag_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id_tag,uid,status,id_student FROM tags WHERE id_tag=%s',(tag_id,))
            return cursor.fetchone()


def save_tag(tag_id,uid,status,student_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if tag_id:
                cursor.execute('UPDATE tags SET uid=%s,status=%s,id_student=%s WHERE id_tag=%s',(uid.strip(),status,int(student_id),tag_id))
            else:
                cursor.execute('INSERT INTO tags(uid,status,id_student) VALUES(%s,%s,%s) RETURNING id_tag',(uid.strip(),status,int(student_id)))
                tag_id=cursor.fetchone()[0]
        connection.commit()
    return int(tag_id)
