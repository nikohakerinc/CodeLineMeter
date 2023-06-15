import os
import datetime
import shutil
import logging
import json
import asyncio
import sqlite3
import gitlab
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

GIT_URL = os.getenv('GIT_URL')
GIT_TOKEN = os.getenv('GIT_TOKEN')
GIT_USERNAME = os.getenv('GIT_USERNAME')
GIT_PASSWORD = os.getenv('GIT_PASSWORD')

class CodeLineMeter:
    def __init__(self):
        self.gl = gitlab.Gitlab(GIT_URL, private_token=GIT_TOKEN)
        self.languages = self.load_languages()
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        self.reports_dir = 'reports'
        self.repo_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo")
        self.projects = [] # Список проектов
        self.total = 0 # Общий счётчик строк
        self.result = {} # Словарь с результатами
        self.start_time = None
        self.global_start_time = datetime.datetime.now()
        self.conn = None
        self.c = None
        self.create_directories()
        self.setup_logging()
        self.create_table()
        self.read_projects()

    # Импорт JSON файла с языками программирования с соответствующими форматами файлов
    def load_languages(self):
        with open('lang_dict.json', 'r') as json_file:
            json_data = json_file.read()
        return json.loads(json_data)

    # Создание рабочих папок
    def create_directories(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        if not os.path.exists(self.repo_folder):
            os.makedirs(self.repo_folder)

    # Настройка логирования
    def setup_logging(self):
        logging.basicConfig(filename=os.path.join(self.log_dir, 'info.log'), level=logging.DEBUG,
                            format='%(levelname)s: %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    # Создаём базу для альтернативного отчёта
    def create_table(self):
        if not self.conn:
            self.conn = sqlite3.connect(os.path.join(self.reports_dir, 'code_stats.db'))
            self.c = self.conn.cursor()
            # Создание таблицы проектов если она отсутствует
            self.c.execute('''CREATE TABLE IF NOT EXISTS projects
             (project_url TEXT, project_name TEXT, python INTEGER, java INTEGER, c INTEGER, cplusplus INTEGER,
              objc INTEGER, csharp INTEGER, javascript INTEGER, php INTEGER, ruby INTEGER, swift INTEGER, go INTEGER,
              rust INTEGER, kotlin INTEGER, lua INTEGER, scala INTEGER, typescript INTEGER, sql INTEGER, shell INTEGER,
              powershell INTEGER, batch INTEGER, perl INTEGER, html INTEGER, css INTEGER, basic INTEGER, pascal INTEGER,
              fortran INTEGER, kobol INTEGER, groovy INTEGER, json INTEGER, yaml INTEGER, xml INTEGER, markdown INTEGER,
              text INTEGER, logfiles INTEGER, configfiles INTEGER, otherlang INTEGER, total_lines INTEGER)''')

    # Считывание списка проектов из файла 'project.txt'
    def read_projects(self):
        with open('project.txt', 'r') as f:
            self.projects = [project.strip() for project in f.readlines() if project.strip()]

    # Клонирование репозиториев
    def clone_repository(self, project, i, line_count):
        result = {}
        repo_url = project.strip().replace("https://", "")
        repo_dir = os.path.join(self.repo_folder, repo_url[repo_url.rfind("/") + 1:].replace(".git", ""))
        project_dir = "/".join(repo_url.split("/")[-2:])[:-4]

        start_time = datetime.datetime.now()
        logging.info(f"Start cloning a repository ({i}/{line_count}): {project_dir}")
        os.system(f"git clone https://{GIT_USERNAME}:{GIT_PASSWORD}@{repo_url} {repo_dir}")
        logging.info(f"Finish cloning a repository: {project_dir}")
        timer_rounded = round(((datetime.datetime.now() - start_time).total_seconds()), 2)
        logging.info(f"Completed in: {timer_rounded} seconds")

        language_lines = {lang: 0 for lang in self.languages}
        total_lines = 0
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                file_path = os.path.join(root, file)
                _, extension = os.path.splitext(file)
                for lang in self.languages:
                    if extension.lower() in self.languages[lang]:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                non_empty_lines = [line for line in lines if line.strip()]
                                language_lines[lang] += len(non_empty_lines)
                                total_lines += len(non_empty_lines)
                        except UnicodeDecodeError:
                            logging.warning(f"Failed to read file: {file_path}")
        
        result[repo_url] = (project_dir,) + tuple(language_lines.values()) + (total_lines,)                  
        self.write_to_database(repo_url, project_dir, language_lines, total_lines)

        # Удаление содержимого папки repo_dir, оставляя папку 'repo'
        shutil.rmtree(repo_dir, ignore_errors=True)
        os.system(f"rm -rf {repo_dir} 2> /dev/null")    # Для Linux/Mac
        os.system(f"rd /s /q {repo_dir} 2> nul")        # Для Windows
                
        return result, total_lines

    # Запись подсчётов по каждому проекту в таблицу 'projects' в БД 'code_state.db'
    def write_to_database(self, repo_url, project_dir, language_lines, total_lines):
        if not self.conn:
            self.conn = sqlite3.connect(os.path.join(self.reports_dir, 'code_stats.db'))
            self.c = self.conn.cursor()

        self.c.execute('''INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                       ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (repo_url, project_dir) + tuple(language_lines.values()) + (total_lines,))
        self.conn.commit()

    # Управление последовательностью выполнения
    async def analyze_projects(self):
        line_count = len(self.projects)
        logging.info(f"Analyzing {line_count} projects...")
        self.start_time = datetime.datetime.now()

        for i, project in enumerate(self.projects, start=1):
            try:
                result, total_lines = self.clone_repository(project, i, line_count)
                self.result.update(result)
                self.total += total_lines
                logging.info(f"Total lines of code: {self.total}")

            except Exception as e:
                logging.error(f"Error analyzing project: {project_dir}.git\nError message: {str(e)}")

        logging.info(f"Analysis completed in {(str((datetime.datetime.now() - self.start_time)).split('.')[0])}")
        shutil.rmtree(self.repo_folder)
        
        return self.result, self.total

    def generate_visualizations(self, result, languages, reports_dir):
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
            xaxis=dict(tickfont=dict(size=16)),
            yaxis=dict(tickfont=dict(size=16)),
            legend=dict(font=dict(size=18))
        )

        histogram_pdf_path = os.path.join(reports_dir, 'histogram.pdf')
        fig.write_image(histogram_pdf_path, engine="kaleido", format="pdf", width=1920, height=1080, scale=1.25)

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

        donut_diagram_pdf_path = os.path.join(reports_dir, 'donut_diagram.pdf')
        fig.write_image(donut_diagram_pdf_path, engine="kaleido", format="pdf", width=1920, height=1080, scale=1.25) 

    # Запись данных в файл
    def write_results_to_file(self, result, languages, total, reports_dir):
        count_csv_path = os.path.join(reports_dir, 'count.csv')
        with open(count_csv_path, 'a') as f:
            keys = ";".join(languages.keys())
            f.write(f"Project URL;Project Name;{keys};Total lines of code\n")
            for repo_url, values in result.items():
                line = f"{repo_url};{';'.join(map(str, values))}\n"
                f.write(line)
            f.write('\n\n')
            f.write(f"Total lines of code:; {total}")
         
    # Экспорт данных из БД в countdb.csv
    def write_dbdata_to_file(self, languages, total, reports_dir):
        if not self.conn:
            self.conn = sqlite3.connect(os.path.join(self.reports_dir, 'code_stats.db'))
            self.c = self.conn.cursor()

        with open(os.path.join(reports_dir, 'countdb.csv'), 'w') as f:
            keys = ";".join(languages.keys())
            f.write(f"Project URL;Project Name;{keys};Total lines of code\n")
            for row in self.c.execute("SELECT * FROM projects"):
                project_data = [str(item) for item in row[:-1]]  # Конвертация int to string
                project_lines = str(row[-1])
                f.write(f"{';'.join(project_data)};{project_lines}\n")
            f.write('\n\n')
            f.write(f"Total lines of code:; {total}")
        self.conn.close()


def main():
    code_stats = CodeLineMeter()
    result, total_lines = asyncio.run(code_stats.analyze_projects())
    code_stats.generate_visualizations(result, code_stats.languages, code_stats.reports_dir)
    code_stats.write_results_to_file(result, code_stats.languages, total_lines, code_stats.reports_dir)
    code_stats.write_dbdata_to_file(code_stats.languages, total_lines, code_stats.reports_dir)
    print(f"Total lines of code: {total_lines}")


if __name__ == '__main__':
    main()
