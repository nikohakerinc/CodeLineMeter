import os
import shutil
import gitlab
import logging
import datetime
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
import sqlite3
import asyncio

load_dotenv()

GIT_URL = os.getenv('GIT_URL')
GIT_TOKEN = os.getenv('GIT_TOKEN')
GIT_USERNAME = os.getenv('GIT_USERNAME')
GIT_PASSWORD = os.getenv('GIT_PASSWORD')

class CodeStats:
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

    # Считывание списка проектов из файла 'project.txt'
    def read_projects(self):
        with open('project.txt', 'r') as f:
            self.projects = [project.strip() for project in f.readlines() if project.strip()]

    # Клонирование репозиториев
    def clone_repository(self, project, i, line_count):
        repo_url = project.strip().replace("https://", "")
        repo_dir = os.path.join(self.repo_folder, repo_url[repo_url.rfind("/") + 1:].replace(".git", ""))
        project_dir = "/".join(repo_url.split("/")[-2:])[:-4]

        start_time = datetime.datetime.now()
        logging.info(f"Start cloning a repository ({i}/{line_count}): {project_dir}")
        os.system(f"git clone https://{GIT_USERNAME}:{GIT_PASSWORD}@{repo_url} {repo_dir}")
        end_time = datetime.datetime.now()
        logging.info(f"Finish cloning a repository: {project_dir}")
        timer = end_time - start_time
        timer_seconds = timer.total_seconds()
        timer_rounded = round(timer_seconds, 2)
        logging.info(f"Cloning took time: {timer_rounded} seconds")
        return repo_url, repo_dir, project_dir

    # Подсчёт строк
    def count_lines_of_code(self, repo_dir):
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
        return language_lines, total_lines
    

    # Создание отчётов
    def generate_report(self, project, repo_url, project_dir, language_lines, total_lines):
        report_dir = os.path.join(self.reports_dir, project_dir)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        # Save the language lines data as a CSV file
        data = {'Language': list(language_lines.keys()), 'Lines of Code': list(language_lines.values())}
        df = pd.DataFrame(data)
        csv_file = os.path.join(report_dir, 'language_lines.csv')
        df.to_csv(csv_file, index=False)

        # Generate a bar chart of the language lines data
        fig = px.bar(df, x='Language', y='Lines of Code', title=f'Language Lines of Code - {project}')
        chart_file = os.path.join(report_dir, 'language_lines_chart.html')
        fig.write_html(chart_file)

        # Save the total lines data in a text file
        text_file = os.path.join(report_dir, 'total_lines.txt')
        with open(text_file, 'w') as f:
            f.write(str(total_lines))

        # Create a summary dictionary for the project
        summary = {
            'Project': project,
            'Repository URL': repo_url,
            'Total Lines of Code': total_lines,
            'Language Lines': language_lines
        }

        return summary

    def write_summary_to_database(self, summary):
        if not self.conn:
            self.conn = sqlite3.connect('code_stats.db')
            self.c = self.conn.cursor()

        project = summary['Project']
        repo_url = summary['Repository URL']
        total_lines = summary['Total Lines of Code']
        language_lines = json.dumps(summary['Language Lines'])

        self.c.execute("INSERT INTO code_stats (project, repo_url, total_lines, language_lines) VALUES (?, ?, ?, ?)",
                       (project, repo_url, total_lines, language_lines))
        self.conn.commit()

    def generate_global_report(self):
        if not self.conn:
            self.conn = sqlite3.connect('code_stats.db')
            self.c = self.conn.cursor()

        self.c.execute("SELECT * FROM code_stats")
        rows = self.c.fetchall()

        projects = []
        total_lines = []
        for row in rows:
            project = row[1]
            total = row[3]
            projects.append(project)
            total_lines.append(total)

        df = pd.DataFrame({'Project': projects, 'Total Lines of Code': total_lines})

        fig = px.bar(df, x='Project', y='Total Lines of Code', title='Total Lines of Code - All Projects')
        chart_file = os.path.join(self.reports_dir, 'global_chart.html')
        fig.write_html(chart_file)

    async def analyze_projects(self):
        line_count = len(self.projects)
        logging.info(f"Analyzing {line_count} projects...")
        self.start_time = datetime.datetime.now()

        for i, project in enumerate(self.projects, start=1):
            try:
                repo_url, repo_dir, project_dir = self.clone_repository(project, i, line_count)
                language_lines, total_lines = self.count_lines_of_code(repo_dir)
                summary = self.generate_report(project, repo_url, project_dir, language_lines, total_lines)
                self.write_summary_to_database(summary)
                self.total += total_lines

                # Удаление содержимого папки repo_dir, оставляя папку 'repo'
                shutil.rmtree(repo_dir, ignore_errors=True)
                os.system(f"rm -rf {repo_dir} 2> /dev/null")    # Для Linux/Mac
                os.system(f"rd /s /q {repo_dir} 2> nul")        # Для Windows
                
            except Exception as e:
                logging.error(f"Error analyzing project: {project}. Error message: {str(e)}")

        self.end_time = datetime.datetime.now()
        elapsed_time = self.end_time - self.start_time
        logging.info(f"Analysis completed in {elapsed_time.total_seconds()} seconds.")
        self.generate_global_report()

def main():
    code_stats = CodeStats()
    asyncio.run(code_stats.analyze_projects())

if __name__ == '__main__':
    main()
