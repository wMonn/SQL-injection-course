from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-2024'

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
    
    # Таблица для Level 1 (разные типы данных)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            release_date TEXT NOT NULL
        )
    ''')
    
    # Таблица для Level 2 и Level 3 (секретные данные)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_secret (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            credit_card TEXT NOT NULL,
            secret_info TEXT NOT NULL
        )
    ''')
    
    # Таблица для Level 3 (дополнительная)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL
        )
    ''')
    
    # Добавляем тестового пользователя
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                      ('admin', hashed_password))
    
    # Добавляем тестовые данные для Level 1
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        products = [
            ('Laptop', 1000, '2024-01-15'),
            ('Mouse', 25, '2024-02-20'),
            ('Keyboard', 75, '2024-03-10'),
            ('Monitor', 300, '2024-01-05'),
            ('USB Cable', 10, '2024-04-01'),
            ('Headphones', 50, '2024-02-15'),
            ('Webcam', 80, '2024-03-20')
        ]
        cursor.executemany('INSERT INTO products (name, price, release_date) VALUES (?, ?, ?)', products)
    
    # Добавляем секретные данные для Level 2 и 3
    cursor.execute('SELECT COUNT(*) FROM users_secret')
    if cursor.fetchone()[0] == 0:
        secrets = [
            ('john_doe', 'john123', 'john@email.com', '4111-1111-1111-1111', 'Likes pizza'),
            ('jane_smith', 'jane456', 'jane@email.com', '4222-2222-2222-2222', 'Works at Google'),
            ('admin_secret', 'superpass', 'admin@system.com', '4333-3333-3333-3333', 'Master key: 42'),
            ('bob_wilson', 'bob789', 'bob@email.com', '4444-4444-4444-4444', 'Favorite color: blue'),
            ('alice_brown', 'alice000', 'alice@email.com', '4555-5555-5555-5555', 'Has a cat named Whiskers')
        ]
        cursor.executemany('INSERT INTO users_secret (username, password, email, credit_card, secret_info) VALUES (?, ?, ?, ?, ?)', secrets)
    
    # Добавляем посты для Level 3
    cursor.execute('SELECT COUNT(*) FROM posts')
    if cursor.fetchone()[0] == 0:
        posts = [
            ('First Post', 'This is my first post!', 1),
            ('Hello World', 'Welcome to the blog', 1),
            ('SQL Injection', 'Learning about security', 2),
            ('Database Tips', 'Always sanitize input', 3)
        ]
        cursor.executemany('INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)', posts)
    
    conn.commit()
    conn.close()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return '<h1>О проекте SQL Injection Lab</h1><p>Учебный тренажер для изучения SQL-инъекций</p><a href="/">На главную</a>'

@app.route('/theory')
def theory():
    return render_template('theory.html')

@app.route('/levels')
def levels():
    if 'user_id' not in session:
        flash('Сначала войдите в аккаунт', 'error')
        return redirect(url_for('login_page'))
    return render_template('levels.html', username=session.get('username'))

# ==================== УРОВЕНЬ 1 ====================
@app.route('/level/1')
def level1():
    if 'user_id' not in session:
        flash('Сначала войдите в аккаунт', 'error')
        return redirect(url_for('login_page'))
    return render_template('level1.html', username=session.get('username'))

@app.route('/level/1/string', methods=['POST'])
def level1_string():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    search = request.form.get('search', '')
    query_type = 'string'
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return render_template('level1_result.html', 
                               results=results, search=search, query=query,
                               query_type=query_type, username=session.get('username'))
    except Exception as e:
        return render_template('level1_result.html', 
                               error=str(e), search=search,
                               query_type=query_type, username=session.get('username'))

@app.route('/level/1/number', methods=['POST'])
def level1_number():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    price = request.form.get('price', '')
    query_type = 'number'
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM products WHERE price > {price}"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return render_template('level1_result.html', 
                               results=results, search=price, query=query,
                               query_type=query_type, username=session.get('username'))
    except Exception as e:
        return render_template('level1_result.html', 
                               error=str(e), search=price,
                               query_type=query_type, username=session.get('username'))

@app.route('/level/1/date', methods=['POST'])
def level1_date():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    date = request.form.get('date', '')
    query_type = 'date'
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM products WHERE release_date = '{date}'"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return render_template('level1_result.html', 
                               results=results, search=date, query=query,
                               query_type=query_type, username=session.get('username'))
    except Exception as e:
        return render_template('level1_result.html', 
                               error=str(e), search=date,
                               query_type=query_type, username=session.get('username'))

# ==================== УРОВЕНЬ 2 (ERROR-BASED) ====================
@app.route('/level/2')
def level2():
    if 'user_id' not in session:
        flash('Сначала войдите в аккаунт', 'error')
        return redirect(url_for('login_page'))
    return render_template('level2.html', username=session.get('username'))

@app.route('/level/2/search', methods=['POST'])
def level2_search():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = request.form.get('user_id', '')
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # УЯЗВИМЫЙ КОД - прямая подстановка
        query = f"SELECT id, username, email FROM users_secret WHERE id = {user_id}"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return render_template('level2_result.html', 
                               results=results, search=user_id, query=query,
                               username=session.get('username'))
    except Exception as e:
        # Показываем ошибку - ЭТО И ЕСТЬ ERROR-BASED INJECTION
        error_message = str(e)
        return render_template('level2_result.html', 
                               error=error_message, search=user_id, 
                               query=f"SELECT * FROM users_secret WHERE id = {user_id}",
                               username=session.get('username'))

# ==================== УРОВЕНЬ 3 (UNION-BASED) ====================
@app.route('/level/3')
def level3():
    if 'user_id' not in session:
        flash('Сначала войдите в аккаунт', 'error')
        return redirect(url_for('login_page'))
    return render_template('level3.html', username=session.get('username'))

@app.route('/level/3/search', methods=['POST'])
def level3_search():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    category = request.form.get('category', '')
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # УЯЗВИМЫЙ КОД - прямая подстановка для UNION инъекций
        query = f"SELECT id, title, content FROM posts WHERE id = {category}"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return render_template('level3_result.html', 
                               results=results, search=category, query=query,
                               username=session.get('username'))
    except Exception as e:
        return render_template('level3_result.html', 
                               error=str(e), search=category,
                               query=f"SELECT id, title, content FROM posts WHERE id = {category}",
                               username=session.get('username'))

@app.route('/level/3/union', methods=['POST'])
def level3_union():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    payload = request.form.get('payload', '')
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Специально уязвимый endpoint для UNION инъекций
        query = f"SELECT id, title, content FROM posts WHERE id = {payload}"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return render_template('level3_result.html', 
                               results=results, search=payload, query=query,
                               username=session.get('username'))
    except Exception as e:
        return render_template('level3_result.html', 
                               error=str(e), search=payload,
                               query=f"SELECT id, title, content FROM posts WHERE id = {payload}",
                               username=session.get('username'))

# ==================== АВТОРИЗАЦИЯ ====================
@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('levels'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not username or not password:
        flash('Заполните все поля', 'error')
        return redirect(url_for('login_page'))
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
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
