import os
import datetime
import shutil
import logging
import json
import mplcyberpunk
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from dotenv import load_dotenv


load_dotenv()


class CodeLineMeter:
    def __init__(self):
        self.languages = self.load_languages()
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        self.reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
        self.repo_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo")
        self.projects = []  # Список проектов
        self.total = 0  # Общий счётчик строк
        self.result = {}  # Словарь с результатами
        self.start_time = None
        self.global_start_time = datetime.datetime.now()
        self.create_directories()
        self.setup_logging()
        self.read_projects()

    # Загрузка списка ЯП с расширениями их файлов из JSON
    def load_languages(self):
        with open('lang_dict.json', 'r') as json_file:
            return json.load(json_file)

    # Создание рабочих директорий
    def create_directories(self):
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.repo_folder, exist_ok=True)

    # Настройка уровня логирования
    def setup_logging(self):
        logging.basicConfig(filename=os.path.join(self.log_dir, 'info.log'), level=logging.INFO,
                            format='%(levelname)s: %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    # Чтение списка проектов из файла project.txt
    def read_projects(self):
        with open('project.txt', 'r') as f:
            self.projects = [project.strip() for project in f if project.strip()]

    # Клонирование репозитория GIT на локальную машину и подсчёт строк кода
    def clone_repository(self, project, i, line_count):
        result = {}
        repo_url = project.strip().replace("https://", "")
        repo_dir = os.path.join(self.repo_folder, repo_url[repo_url.rfind("/") + 1:].replace(".git", ""))
        project_dir = "/".join(repo_url.split("/")[-2:])[:-4]

        start_time = datetime.datetime.now()
        logging.info(f"Start cloning a repository ({i}/{line_count}): {project_dir}")
        os.system(f"GIT_SSL_NO_VERIFY=true git clone https://{os.getenv('GIT_USERNAME')}:{os.getenv('GIT_TOKEN')}@{repo_url} {repo_dir}")
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

        shutil.rmtree(repo_dir, ignore_errors=True)
        if os.name == 'nt':
            os.system(f"rd /s /q {repo_dir}")
        else:
            os.system(f"rm -rf {repo_dir}")

        return result, total_lines

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
        shutil.rmtree(self.repo_folder, ignore_errors=True)

        return self.result, self.total

    # Построение отчётности
    def generate_visualizations(self, result, total_lines, languages, reports_dir):
        # Создание словаря temp на основе languages
        temp = {key: 0 for key in languages}
        for values in result.values():
            language_lines = values[1:-1]
            for language, lines in zip(temp.keys(), language_lines):
                temp[language] += lines

        # Удаляем лишние данные из диаграмм
        if "Markdown" in temp:
            md_value = temp["Markdown"]
            del temp["Markdown"]
        if "Any Text" in temp:
            text_value = temp["Any Text"]
            del temp["Any Text"]
        if "Other Lang" in temp:
            other_value = temp["Other Lang"]
            del temp["Other Lang"]
        if "Patch files" in temp:
            patch_value = temp["Patch files"]
            del temp["Patch files"]
        if "Log files" in temp:
            log_value = temp["Log files"]
            del temp["Log files"]
        programm_value = total_lines - text_value - patch_value - md_value - log_value

        # Сортировка оставшихся данных от большего к меньшему исключая нулевые значения
        temp_filtered = {k: v for k, v in temp.items() if v != 0}
        df = pd.DataFrame({'Language': list(temp_filtered.keys()), 'Count': list(temp_filtered.values())})
        df = df.sort_values('Count', ascending=False)

        # Построение гистограммы
        with plt.style.context('cyberpunk'):
            colors = plt.cm.plasma(np.linspace(0.2, 1, len(df)))
            ax = df.plot(x='Language', kind='bar', stacked=False, alpha=0.8, figsize=(16, 9), legend=False)
            ax.set_ylim(top=ax.get_ylim()[1] * 1.1)
            for i, p in enumerate(ax.patches):
                p.set_facecolor(colors[len(colors) - 1 - i])    # Градиент баров обратный
                # p.set_facecolor(colors[i % len(colors)])      # Градтент баров прямой
                ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', rotation=30)
            plt.xticks(range(len(df)), df['Language'], fontsize=10, ha='center')
            plt.gcf().autofmt_xdate()
            # Добавление легенды с текстовыми метками
            legend_elements = [
                Line2D([0], [0], color=plt.cm.rainbow(0.0), lw=8, label=f'Total Lines: {total_lines}'),
                Line2D([0], [0], color=plt.cm.rainbow(0.2), lw=8, label=f'Program Code: {programm_value}'),
                Line2D([0], [0], color=plt.cm.rainbow(0.4), lw=8, label=f'Markdown Lines: {md_value}'),
                Line2D([0], [0], color=plt.cm.rainbow(0.6), lw=8, label=f'Any Text Lines: {text_value}'),
                Line2D([0], [0], color=plt.cm.rainbow(0.8), lw=8, label=f'Log files Lines: {log_value}'),
                Line2D([0], [0], color=plt.cm.rainbow(1.0), lw=8, label=f'Other Lang Code: {other_value}')
            ]
            ax.legend(handles=legend_elements, fontsize=14, loc='upper right')
            plt.tight_layout()

        histogram_chart_pdf_path = os.path.join(reports_dir, 'histogram_chart.pdf')
        plt.savefig(histogram_chart_pdf_path, format="pdf", dpi=300, orientation='portrait', bbox_inches='tight')

        # Построение кольцевой диаграммы
        with plt.style.context('cyberpunk'):
            sizes = df['Count']
            labels = [f"{lang} ({count})" if count / sum(sizes) >= 0.015 else '' for lang, count in zip(df['Language'], sizes)]
            explode = (0.1,) * len(df)
            colors = plt.cm.plasma(np.linspace(0.2, 1, len(df['Language'])))
            fig, ax = plt.subplots(figsize=(16, 9))
            wedges, labels, text_handles = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                                  autopct=lambda pct: f"{pct:.1f}%" if pct > 1.5 else None, shadow=True,
                                                  startangle=45, wedgeprops=dict(width=0.5), rotatelabels=True, pctdistance=0.75)
            for label, text_handle in zip(labels, text_handles):
                if label.get_text() == '':
                    text_handle.set_alpha(0)
            ax.axis('equal')

        donat_chart_pdf_path = os.path.join(reports_dir, 'donat_chart.pdf')
        plt.savefig(donat_chart_pdf_path, format="pdf", dpi=300, orientation='portrait', bbox_inches='tight')

    # Запись словаря result в файл count.csv
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


    def run(self):
        result, total_lines = self.analyze_projects()
        self.write_results_to_file(result, self.languages, total_lines, self.reports_dir)
        self.generate_visualizations(result, total_lines, self.languages, self.reports_dir)
        print(f"Total lines of code: {total_lines}")


if __name__ == '__main__':
    code_stats = CodeLineMeter()
    code_stats.run()
