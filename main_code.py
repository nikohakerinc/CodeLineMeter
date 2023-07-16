import os
import datetime
import shutil
import logging
import json
import sqlite3
import mplcyberpunk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

GIT_URL = os.getenv('GIT_URL')
GIT_USERNAME = os.getenv('GIT_USERNAME')
GIT_TOKEN = os.getenv('GIT_TOKEN')

class CodeLineMeter:
    def __init__(self):
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
        logging.basicConfig(filename=os.path.join(self.log_dir, 'info.log'), level=logging.INFO,
                            format='%(levelname)s: %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    # Создаём базу для альтернативного отчёта
    def create_table(self):
        if not self.conn:
            self.conn = sqlite3.connect(os.path.join(self.reports_dir, 'code_stats.db'))
            self.c = self.conn.cursor()

            # Базовый SQL запрос
            create_table_sql = '''
                CREATE TABLE IF NOT EXISTS projects (
                    project_url TEXT,
                    project_name TEXT,
            '''
            # Добавление колонок для языков динамически из значений JSON
            for lang, extensions in self.languages.items():
                lang_col_name = lang.lower().replace(' ', '')
                create_table_sql += f'"{lang_col_name}" INTEGER, '
            # Завершение SQL-запроса, добавление в таблицу колонки total lines
            create_table_sql += 'total_lines INTEGER)'
            self.c.execute(create_table_sql)

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
        os.system(f"git clone https://{GIT_USERNAME}:{GIT_TOKEN}@{repo_url} {repo_dir}")
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

        placeholders = ', '.join(['?' for _ in range(len(self.languages.keys()) + 3)])
        insert_values = '''INSERT INTO projects VALUES ('''
        insert_values += placeholders
        insert_values += ')'
        values = (repo_url, project_dir) + tuple(language_lines.values()) + (total_lines,)
        self.c.execute(insert_values, values)
        self.conn.commit()

    # Управление последовательностью выполнения
    def analyze_projects(self):
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
                logging.error(f"Error analyzing project: {self.repo_folder}.git\nError message: {str(e)}")

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
        with plt.style.context('cyberpunk'):
            ax = df.plot(x='Language', kind='bar', stacked=False, alpha=0.8, figsize=(16,9), legend=False)
            ax.set_ylim(top=ax.get_ylim()[1] * 1.1)
            # Вывод значений над каждым столбцом Language
            for p in ax.patches:
                ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2, p.get_height()),
                            ha='center', va='bottom', rotation = 30)
            plt.xticks(range(len(df)), df['Language'], fontsize=10, ha='center')
            plt.gcf().autofmt_xdate()
            plt.tight_layout()
        histogram_chart_pdf_path = os.path.join(reports_dir, 'histogram_chart.pdf')
        plt.savefig(histogram_chart_pdf_path, format="pdf", dpi=300, orientation='portrait', bbox_inches='tight')


        # Построение кольцевой диаграммы
        with plt.style.context('cyberpunk'):
            labels = [f"{lang} ({count})" for lang, count in zip(df['Language'], df['Count'])]
            sizes = df['Count']
            explode = (0.1,) * len(df)
            colors = plt.cm.plasma(np.linspace(0.2, 1, len(df['Language'])))
            # Создание круговой диаграммы
            fig, ax = plt.subplots(figsize=(16, 9))
            wedges, labels, text_handles = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct=lambda pct: f"{pct:.1f}%" if pct > 2.0 else None, shadow=True,
                    startangle=45, wedgeprops=dict(width=0.5), rotatelabels=True, pctdistance=0.75)
            for label, text_handle in zip(labels, text_handles):
                if label.get_text() == '':
                    text_handle.set_alpha(0)
            ax.axis('equal')
        donat_chart_pdf_path = os.path.join(reports_dir, 'donat_chart.pdf')
        plt.savefig(donat_chart_pdf_path, format="pdf", dpi=300, orientation='portrait', bbox_inches='tight')


    # Запись данных из словаря result в файл count.csv
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
    result, total_lines = code_stats.analyze_projects()
    code_stats.generate_visualizations(result, code_stats.languages, code_stats.reports_dir)
    code_stats.write_results_to_file(result, code_stats.languages, total_lines, code_stats.reports_dir)
    # code_stats.write_dbdata_to_file(code_stats.languages, total_lines, code_stats.reports_dir)
    print(f"Total lines of code: {total_lines}")


if __name__ == '__main__':
    main()
