from database.connection import get_connection


def get_access_log(id_parent=None, limit=200, search='', date_from='', date_to=''):
    sql='''SELECT l.id_record,l.event_time,l.event_type,s.last_name,s.first_name,s.middle_name,s.class_name,t.uid
           FROM access_log l JOIN tags t ON t.id_tag=l.id_tag JOIN students s ON s.id_student=t.id_student'''
    where=[]; params=[]
    if id_parent is not None:
        sql += ' JOIN student_parents sp ON sp.id_student=s.id_student'; where.append('sp.id_parent=%s'); params.append(id_parent)
    if search:
        where.append("LOWER(s.last_name || ' ' || s.first_name || ' ' || s.class_name || ' ' || t.uid) LIKE LOWER(%s)"); params.append(f'%{search}%')
    if date_from: where.append('l.event_time::date >= %s'); params.append(date_from)
    if date_to: where.append('l.event_time::date <= %s'); params.append(date_to)
    if where: sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY l.event_time DESC,l.id_record DESC LIMIT %s'; params.append(limit)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql,params); return cursor.fetchall()


def get_notifications(id_parent=None,limit=200):
    sql='''SELECT n.id_notification,n.text,n.sent_at,n.status,p.last_name,p.first_name,p.middle_name,l.event_time
           FROM notifications n JOIN parents p ON p.id_parent=n.id_parent JOIN access_log l ON l.id_record=n.id_record'''
    params=[]
    if id_parent is not None: sql+=' WHERE n.id_parent=%s'; params.append(id_parent)
    sql+=' ORDER BY n.id_notification DESC LIMIT %s'; params.append(limit)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql,params); return cursor.fetchall()
