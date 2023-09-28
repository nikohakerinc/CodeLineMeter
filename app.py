from flask import Flask, render_template, request
import os

app = Flask(__name__, static_folder='static')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получение данных из формы
        git_username = request.form['git_username']
        git_token = request.form['git_token']
        projects = request.form['projects']
        # project_lines = projects.split('\n')
        # first_project_line = project_lines[0]
        # index_of_slash = first_project_line.find('/')
        # git_url = first_project_line[:index_of_slash+4]
        e_mail = request.form['e_mail']
        

        # Запись данных в файл .env
        with open('.env', 'w') as env_file:
            env_file.write(f"GIT_USERNAME = '{git_username}'\n")
            env_file.write(f"GIT_TOKEN = '{git_token}'\n")
            env_file.write(f"TO_EMAIL = '{e_mail}'\n")

        # Запись списка проектов в файл project.txt
        with open('project.txt', 'w') as project_file:
            project_file.write(projects)

        # Выполнение команды Python
        os.system('python main_code.py')

        return 'Данные отправлены и команда выполнена успешно.'

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
