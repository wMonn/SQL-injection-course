from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-2024'

# Паттерны для обнаружения SQL-инъекций
SQL_PATTERNS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR '1'='1' --",
    "' OR '1'='1' #",
    "'; DROP TABLE",
    "'; DELETE FROM",
    "UNION SELECT",
    "' UNION SELECT",
    "1' ORDER BY",
    "1' AND '1'='1",
    "' WAITFOR DELAY",
    "' AND SLEEP(",
    "../etc/passwd",
    "xp_cmdshell",
    "'; EXEC",
    "1; SELECT",
    "admin'--",
    "'#"
]

def is_sql_injection(text):
    """Проверяет, содержит ли строка признаки SQL-инъекции"""
    if not text:
        return False
    
    text_upper = text.upper()
    for pattern in SQL_PATTERNS:
        if pattern.upper() in text_upper:
            return True
    return False

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Добавляем тестового пользователя (пароль: admin123)
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                      ('admin', hashed_password))
    
    conn.commit()
    conn.close()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница "О проекте"
@app.route('/about')
def about():
    return '<h1>О проекте SQL Injection Lab</h1><p>Учебный тренажер для изучения SQL-инъекций</p><a href="/">На главную</a>'

# Страница с теорией
@app.route('/theory')
def theory():
    return render_template('theory.html')

# Страница с уровнями
@app.route('/levels')
def levels():
    if 'user_id' not in session:
        flash('Сначала войдите в аккаунт', 'error')
        return redirect(url_for('login_page'))
    return render_template('levels.html', username=session.get('username'))

# Страница логина (GET)
@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('levels'))
    return render_template('login.html')

# Обработка логина (POST) - С ЗАЩИТОЙ ОТ SQL-ИНЪЕКЦИЙ
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    # Проверка на SQL-инъекции
    if is_sql_injection(username) or is_sql_injection(password):
        flash('Обнаружена попытка SQL-инъекции. Доступ запрещен.', 'error')
        print(f"Заблокирована SQL-инъекция: username='{username}', password='{password}'")
        return redirect(url_for('login_page'))
    
    if not username or not password:
        flash('Заполните все поля', 'error')
        return redirect(url_for('login_page'))
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Безопасный параметризованный запрос
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user:
            hashed_input = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == hashed_input:
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash('Вы вошли в аккаунт. Добро пожаловать', 'success')
                return redirect(url_for('levels'))
            else:
                flash('Неверный пароль', 'error')
        else:
            flash('Пользователь не найден', 'error')
            
        conn.close()
        
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
    
    return redirect(url_for('login_page'))

# Выход
@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    print("\nСервер запущен на http://localhost:5000")
    print("Тестовые данные: admin / admin123\n")
    app.run(debug=True)
