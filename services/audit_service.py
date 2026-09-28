from database.connection import get_connection


def write_audit(id_user, action, object_type=None, object_id=None, details=None, old_value=None, new_value=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''INSERT INTO audit_log(id_user,action,object_type,object_id,details,old_value,new_value)
                              VALUES(%s,%s,%s,%s,%s,%s,%s)''',(id_user,action,object_type,object_id,details,old_value,new_value))
        connection.commit()


def get_audit(limit=200):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT a.created_at,COALESCE(u.full_name,'Система'),u.role,a.action,a.object_type,a.object_id,
                                     a.details,a.old_value,a.new_value
                              FROM audit_log a LEFT JOIN users u ON u.id_user=a.id_user
                              ORDER BY a.created_at DESC,a.id_audit DESC LIMIT %s''',(limit,))
            return cursor.fetchall()
