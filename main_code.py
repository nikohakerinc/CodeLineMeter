# Импорт зависимостей
import os
import gitlab
import logging
from lang import dict as languages
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv


# Загрузка переменных среды
load_dotenv()
GIT_URL = os.getenv('GIT_URL')
GIT_TOKEN = os.getenv('GIT_TOKEN')
GIT_USERNAME = os.getenv('GIT_USERNAME')
GIT_PASSWORD = os.getenv('GIT_PASSWORD')

# Метод подключения к GIT
gl = gitlab.Gitlab(GIT_URL, private_token=GIT_TOKEN)

# Создаем директорию для логов, если она не существует
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Задаем уровень логов
logging.basicConfig(filename=os.path.join(log_dir, 'info.log'), level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Функция записи результатов в файл count.csv
def write_results_to_file(result, languages, total):
    # Создаём файл 'count.csv' и записываем в него названия колонок
    with open('count.csv', 'a') as f:
        keys = ";".join(languages.keys())
        f.write(f"Project URL;Project Name;{keys};Total lines of code\n")

    # Запись результатов в файл 'count.csv'
    with open('count.csv', 'a') as f:
        for repo_url, values in result.items():
            line = f"{repo_url};{';'.join(map(str, values))}\n"
            f.write(line)

    # Добавляем отступы и записываем общее количество строк кода в конец файла 'count.csv'
    with open('count.csv', 'a') as f:
        f.write('\n\n')
        f.write(f"Total lines of code:; {total}\n")

# Инициализация счётчика строк кода и результирующего словаря
total = 0
result = {}

# Конструкция обработки исключений в случае их возникновения при подсчёте строк кода
try:
    # Клонирование репозитория и процесс подсчёта строк кода
    with open('project.txt', 'r') as f:
        projects = [project.strip() for project in f.readlines() if project.strip()]

    for project in projects:
        # Получаем репозиторий
        repo_url = project.strip().replace("https://", "")
        repo_dir = repo_url[repo_url.rfind("/") + 1:].replace(".git", "")
        project_dir = "/".join(repo_url.split("/")[-2:])[:-4]       # Сохраняет проект + папка вышестоящей подгруппы
        # Клонирование репозитория
        os.system(f"git clone https://{GIT_USERNAME}:{GIT_PASSWORD}@{repo_url} {repo_dir}")

        # Инициализация подсчёта строк кода по языкам
        language_lines = {lang: 0 for lang in languages}

        # Подсчёт строк кода в репозитории
        total_lines = 0
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                file_path = os.path.join(root, file)
                _, extension = os.path.splitext(file)

                # Подсчет строк на основе расширения файла
                for lang in languages:
                 if extension.lower() in languages[lang]:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            non_empty_lines = [line for line in lines if line.strip()]
                            language_lines[lang] += len(non_empty_lines)
                            total_lines += len(non_empty_lines)
                    except UnicodeDecodeError:
                        pass
        
        # Запись результатов подсчёта в словарь 'result' с сортировкой по языкам программирования            
        result[repo_url] = (project_dir,) + tuple(language_lines.values()) + (total_lines,)

        # Добавляем количество строк кода проекта к общему счетчику
        total += total_lines
        
        # Удаление скаченного репозитория
        # os.system(f"rm -rf {repo_dir}")         # Если код запускается Linux
        # os.system(f"rm -rf {repo_dir}")         # Чтоб наверняка удалил папку
        os.system(f"rd /s /q {repo_dir}")       # Если код запускается в Windows
        os.system(f"rd /s /q {repo_dir}")       # Чтоб наверняка удалил папку

        pass
# В случае разрыва интернет соединения, ожидать переподключения
except Exception as e:
    raise e
# В случае отмены выполнения кода с клавиатуры, продолжать выполнение кода с уже полученными результатами
except: 
    pass

# Конструкция обработки исключений для блока построения диаграмм
try:
    # Инициализация словаря 'temp' на основе словаря 'languages'
    temp = {key: 0 for key in languages}

    # Чтение словаря 'result' и суммирование значений по колонкам (языкам) и дальнейшего построения диаграмм
    for values in result.values():
        language_lines = values[1:-1]
        for language, lines in zip(temp.keys(), language_lines):
            temp[language] += lines
            
    # Фильтрация колонок содержащих только ненулевых значений
    temp_filtered = {k: v for k, v in temp.items() if v != 0}

    # Создание DataFrame и сортировка от большего суммарного значения к меньшему
    df = pd.DataFrame({'Language': list(temp_filtered.keys()), 'Count': list(temp_filtered.values())})
    df = df.sort_values('Count', ascending=False)

    # Построение гистограммы
    fig = px.bar(df, x='Language', y='Count', text='Count', color='Language',
                 color_discrete_sequence=px.colors.qualitative.Vivid)
    fig.update_traces(texttemplate='%{text:.4s}', textposition='outside')
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        width=1600, height=900, margin=dict(t=15, l=15, r=15, b=15),
        xaxis_title='Языки программирования', yaxis_title='Количество строк кода',
        xaxis=dict(
            tickfont=dict(size=16)
        ),
        yaxis=dict(
            tickfont=dict(size=16)
        ),
        legend=dict(
            font=dict(size=18)
        )
    )

    # Запись гистограммы в файл 'gistogram.pdf' в горизонтальной ориентации
    fig.write_image("gistogram.pdf", engine="kaleido", format="pdf", width=1920, height=1080, scale=1.25)

    # Построение кольцевой диаграммы
    fig = go.Figure()
    pull = [0] * len(df['Count'])
    fig.add_trace(go.Pie(values=df['Count'], labels=df['Language'], pull=pull, hole=0.7))
    fig.update_traces(textfont=dict(size=15))
    fig.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    legend_orientation="v",
    annotations=[dict(text='Соотношение<br>количества строк<br>программного кода<br>в Git<br>репозитории(ях)',
    x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    # Запись кольцевой диаграммы в файл 'ring_diagram.pdf' в горизонтальной ориентации
    fig.write_image("ring_diagram.pdf", engine="kaleido", format="pdf", width=1920, height=1080, scale=1.25)

# В случае исключения, запуск функции записи результатов в файл 'count.csv'
except:
    write_results_to_file(result, languages, total)

# Если результат выполнения всего кода успешный, запуск функции записи результатов в файл 'count.csv'
else:
    write_results_to_file(result, languages, total)

# Печать сообщения с общим количеством строк по репозиторию(ям)
print(f"Total lines of code: {total}")
