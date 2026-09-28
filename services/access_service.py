from database.connection import get_connection
from services.access_logic import determine_event_type, build_notification_text


def find_student_by_uid(uid: str):
    sql='''SELECT t.id_tag,s.id_student,s.last_name,s.first_name,s.middle_name,s.class_name
           FROM tags t JOIN students s ON s.id_student=t.id_student
           WHERE t.uid=%s AND t.status='active' '''
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql,(uid.strip(),)); row=cursor.fetchone()
    if row is None: return None
    return {'id_tag':row[0],'id_student':row[1],'last_name':row[2],'first_name':row[3],'middle_name':row[4],'class_name':row[5]}


def register_access(uid: str):
    uid=uid.strip()
    if not uid:
        return {'ok':False,'message':'UID не введен.'}
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT t.id_tag,s.id_student,s.last_name,s.first_name,s.middle_name,s.class_name
                              FROM tags t JOIN students s ON s.id_student=t.id_student
                              WHERE t.uid=%s AND t.status='active' ''',(uid,))
            student=cursor.fetchone()
            if student is None:
                return {'ok':False,'message':'Метка не найдена или заблокирована.'}
            id_tag,id_student,last_name,first_name,middle_name,class_name=student
            cursor.execute('''SELECT event_type FROM access_log WHERE id_tag=%s
                              ORDER BY event_time DESC,id_record DESC LIMIT 1''',(id_tag,))
            row=cursor.fetchone(); event_type=determine_event_type(row[0] if row else None)
            cursor.execute('''INSERT INTO access_log(id_tag,event_type) VALUES(%s,%s)
                              RETURNING id_record,event_time''',(id_tag,event_type))
            id_record,event_time=cursor.fetchone()
            full_name=' '.join(x for x in [last_name,first_name,middle_name] if x)
            text=build_notification_text(full_name,class_name,event_type,event_time)
            cursor.execute('''SELECT p.id_parent FROM parents p JOIN student_parents sp ON sp.id_parent=p.id_parent
                              WHERE sp.id_student=%s''',(id_student,))
            for (id_parent,) in cursor.fetchall():
                cursor.execute("INSERT INTO notifications(id_parent,id_record,text,status) VALUES(%s,%s,%s,'created')",(id_parent,id_record,text))
        connection.commit()
    return {'ok':True,'id_record':id_record,'student':full_name,'class_name':class_name,'event_type':event_type,'event_time':event_time,'message':text}
