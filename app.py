from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Признаки SQL-инъекции
SQL_PATTERNS = [
    "'", '"', "--", ";", 
    " OR ", " AND ", " UNION ",
    "SELECT", "DROP", "INSERT", "UPDATE", "DELETE",
    "1=1", "'1'='1", '"1"="1"'
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

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница "О проекте"
@app.route('/about')
def about():
    return "<h1>О проекте SQL Injection Lab</h1><p>Учебный тренажер для изучения SQL-инъекций</p><a href='/'>На главную</a>"

# Страница с теорией
@app.route('/theory')
def theory():
    return render_template('theory.html')

# Страница с уровнями
@app.route('/levels')
def levels():
    return render_template('levels.html')

# Страница конкретного уровня
@app.route('/level/<int:level_id>')
def level(level_id):
    return render_template(f'level{level_id}.html')

# Обработка формы входа с проверкой на SQL-инъекцию
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    
    if is_sql_injection(username):
        return f"""
        <h2> ОБНАРУЖЕНА SQL-ИНЪЕКЦИЯ!</h2>
        <p>Вы ввели: <strong>{username}</strong></p>
        <p>Этот ввод содержит признаки SQL-инъекции.</p>
        <p><a href='/'>Вернуться на главную</a></p>
        """
    else:
        return f"""
        <h2> Вход выполнен</h2>
        <p>Добро пожаловать, {username}!</p>
        <p><a href='/'>На главную</a></p>
        """

# Админ-панель
@app.route('/admin')
def admin():
    return "Админ-панель (только для разработчика)"

if __name__ == '__main__':
    app.run(debug=True)
