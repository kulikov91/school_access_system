import os
from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session, url_for
from services.access_service import register_access
from services.audit_service import get_audit, write_audit
from services.catalog_service import (delete_parent, delete_student, get_parent, get_parents, get_student,
                                      get_students, get_tag, get_tags, save_parent, save_student, save_tag,
                                      get_parent_students, save_parent_student, delete_parent_student)
from services.user_service import authenticate, ensure_demo_users
from services.view_service import get_access_log, get_notifications

app=Flask(__name__); app.secret_key=os.getenv('SECRET_KEY','development-secret-change-later')
ROLE_NAMES={'sysadmin':'Системный администратор','director':'Директор','deputy':'Завуч','security':'Охранник','parent':'Родитель'}

def login_required(view):
    @wraps(view)
    def wrapped(*args,**kwargs):
        if 'user' not in session: return redirect(url_for('login'))
        return view(*args,**kwargs)
    return wrapped

def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args,**kwargs):
            if 'user' not in session: return redirect(url_for('login'))
            if session['user']['role'] not in roles: return render_template('forbidden.html'),403
            return view(*args,**kwargs)
        return wrapped
    return decorator

@app.context_processor
def inject_globals(): return {'role_names':ROLE_NAMES}

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=authenticate(request.form.get('username',''),request.form.get('password',''))
        if user:
            session['user']=user; write_audit(user['id_user'],'LOGIN','user',str(user['id_user']),'Успешный вход в систему'); return redirect(url_for('dashboard'))
        flash('Неверный логин или пароль.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    user=session['user']; write_audit(user['id_user'],'LOGOUT','user',str(user['id_user']),'Выход из системы'); session.clear(); return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard(): return render_template('dashboard.html')

@app.route('/access',methods=['GET','POST'])
@roles_required('sysadmin','director','deputy','security')
def access_control():
    result=None
    if request.method=='POST':
        uid=request.form.get('uid','')
        try:
            result=register_access(uid)
            if result['ok']: write_audit(session['user']['id_user'],'RFID_SCAN','tag',uid.strip(),f"{result['student']}; событие {result['event_type']}")
            else: write_audit(session['user']['id_user'],'RFID_SCAN_REJECTED','tag',uid.strip(),result['message'])
        except Exception as exc: result={'ok':False,'message':f'Ошибка работы с базой данных: {exc}'}
    return render_template('access.html',result=result)

@app.route('/journal')
@login_required
def journal():
    user=session['user']; parent_id=user['id_parent'] if user['role']=='parent' else None
    return render_template('journal.html',rows=get_access_log(parent_id,search=request.args.get('q',''),date_from=request.args.get('date_from',''),date_to=request.args.get('date_to','')))

@app.route('/notifications')
@login_required
def notifications():
    user=session['user']; parent_id=user['id_parent'] if user['role']=='parent' else None
    return render_template('notifications.html',rows=get_notifications(parent_id))

@app.route('/audit')
@roles_required('sysadmin','director')
def audit(): return render_template('audit.html',rows=get_audit())

@app.route('/students')
@roles_required('sysadmin','director','deputy')
def students(): return render_template('students.html',rows=get_students(request.args.get('q','')))

@app.route('/students/new',methods=['GET','POST'])
@app.route('/students/<int:item_id>/edit',methods=['GET','POST'])
@roles_required('sysadmin','director','deputy')
def student_form(item_id=None):
    row=get_student(item_id) if item_id else None
    if request.method=='POST':
        if not request.form.get('last_name') or not request.form.get('first_name') or not request.form.get('class_name'):
            flash('Заполните фамилию, имя и класс.'); return render_template('student_form.html',row=row)
        old=str(row) if row else None
        new_id=save_student(item_id,request.form['last_name'],request.form['first_name'],request.form.get('middle_name',''),request.form['class_name'])
        write_audit(session['user']['id_user'],'UPDATE' if item_id else 'CREATE','student',str(new_id),'Карточка учащегося',old,str(get_student(new_id)))
        return redirect(url_for('students'))
    return render_template('student_form.html',row=row)

@app.post('/students/<int:item_id>/delete')
@roles_required('sysadmin','director')
def student_delete(item_id):
    old=get_student(item_id)
    try: delete_student(item_id); write_audit(session['user']['id_user'],'DELETE','student',str(item_id),'Удаление учащегося',str(old),None)
    except Exception as exc: flash(f'Удаление невозможно: {exc}')
    return redirect(url_for('students'))

@app.route('/parents')
@roles_required('sysadmin','director','deputy')
def parents(): return render_template('parents.html',rows=get_parents(request.args.get('q','')))

@app.route('/parents/new',methods=['GET','POST'])
@app.route('/parents/<int:item_id>/edit',methods=['GET','POST'])
@roles_required('sysadmin','director','deputy')
def parent_form(item_id=None):
    row=get_parent(item_id) if item_id else None
    if request.method=='POST':
        required=[request.form.get('last_name'),request.form.get('first_name'),request.form.get('phone'),request.form.get('email')]
        if not all(required):
            flash('Заполните обязательные поля.')
            return render_template('parent_form.html',row=row,students=get_students(),linked_students=get_parent_students(item_id) if item_id else [])
        old=str(row) if row else None
        new_id=save_parent(item_id,request.form['last_name'],request.form['first_name'],request.form.get('middle_name',''),request.form['phone'],request.form['email'])
        student_id=request.form.get('id_student')
        if student_id:
            save_parent_student(new_id,student_id,request.form.get('relationship','родитель'))
        write_audit(session['user']['id_user'],'UPDATE' if item_id else 'CREATE','parent',str(new_id),'Карточка родителя',old,str(get_parent(new_id)))
        return redirect(url_for('parent_form',item_id=new_id))
    return render_template('parent_form.html',row=row,students=get_students(),linked_students=get_parent_students(item_id) if item_id else [])

@app.post('/parents/<int:parent_id>/students/<int:student_id>/delete')
@roles_required('sysadmin','director','deputy')
def parent_student_delete(parent_id,student_id):
    delete_parent_student(parent_id,student_id)
    write_audit(session['user']['id_user'],'DELETE','student_parent',f'{student_id}:{parent_id}','Удалена связь учащегося с родителем')
    return redirect(url_for('parent_form',item_id=parent_id))

@app.post('/parents/<int:item_id>/delete')
@roles_required('sysadmin','director')
def parent_delete(item_id):
    old=get_parent(item_id)
    try: delete_parent(item_id); write_audit(session['user']['id_user'],'DELETE','parent',str(item_id),'Удаление родителя',str(old),None)
    except Exception as exc: flash(f'Удаление невозможно: {exc}')
    return redirect(url_for('parents'))

@app.route('/tags')
@roles_required('sysadmin','director','deputy')
def tags(): return render_template('tags.html',rows=get_tags(request.args.get('q','')))

@app.route('/tags/new',methods=['GET','POST'])
@app.route('/tags/<int:item_id>/edit',methods=['GET','POST'])
@roles_required('sysadmin','director','deputy')
def tag_form(item_id=None):
    row=get_tag(item_id) if item_id else None
    if request.method=='POST':
        if not request.form.get('uid') or not request.form.get('id_student'): flash('Укажите UID и учащегося.'); return render_template('tag_form.html',row=row,students=get_students())
        old=str(row) if row else None
        try:
            new_id=save_tag(item_id,request.form['uid'],request.form.get('status','active'),request.form['id_student'])
            write_audit(session['user']['id_user'],'UPDATE' if item_id else 'CREATE','tag',str(new_id),'RFID/NFC-метка',old,str(get_tag(new_id)))
            return redirect(url_for('tags'))
        except Exception as exc: flash(f'Не удалось сохранить метку: {exc}')
    return render_template('tag_form.html',row=row,students=get_students())

if __name__ == '__main__':
    try:
        ensure_demo_users()
    except Exception as exc:
        print('Не удалось подготовить пользователей. Выполните миграции БД.')
        print(exc)
        raise
    app.run(host='127.0.0.1', port=5000, debug=False)
