from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница "О проекте" (about)
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
    # Возвращаем шаблон для конкретного уровня
    return render_template(f'level{level_id}.html')

# Обработка формы входа (УЯЗВИМАЯ ВЕРСИЯ)
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    # Здесь будет уязвимый SQL запрос
    return f"Попытка входа с логином: {username}"

# Админ-панель (если понадобится)
@app.route('/admin')
def admin():
    return "Админ-панель (только для разработчика)"

if __name__ == "__main__":
    app.run(debug=True)
