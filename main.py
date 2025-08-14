import os
import datetime
import shutil
import logging
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dotenv import load_dotenv
from git import Repo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplcyberpunk

# Для совместимости с более старыми версиями Matplotlib
from matplotlib.lines import Line2D

# Загружаем переменные окружения
load_dotenv()

@dataclass
class RepoStats:
    """Класс для хранения статистики по репозиторию."""
    url: str
    name: str
    language_lines: dict
    total_lines: int

class CodeLineMeter:
    """Основной класс для анализа проектов."""
    def __init__(self, lang_file='lang_dict.json', projects_file='project.txt'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_dir = os.path.join(base_dir, 'logs')
        self.reports_dir = os.path.join(base_dir, 'reports')
        self.repo_folder = os.path.join(base_dir, "repo")

        self.languages = self.load_languages(lang_file)
        # Создаем обратный словарь для быстрого поиска языка по расширению
        self.ext_to_lang = {ext: lang for lang, extensions in self.languages.items() for ext in extensions}
        self.projects = self.load_projects(projects_file)
        self.results = []
        self.global_start_time = datetime.datetime.now()

        self._create_directories()
        self.logger = self._setup_logging()

    def load_languages(self, file_path):
        """Загружает словарь языков из JSON-файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {file_path} не найден.")

    def load_projects(self, file_path):
        """Загружает список проектов из текстового файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл {file_path} не найден.")

    def _create_directories(self):
        """Создает необходимые директории."""
        for path in [self.log_dir, self.reports_dir, self.repo_folder]:
            os.makedirs(path, exist_ok=True)

    def _setup_logging(self):
        """Настраивает логирование с ротацией файлов."""
        logger = logging.getLogger("CodeLineMeter")
        logger.setLevel(logging.INFO)
        
        # Убираем дублирование логов в консоль
        # Устанавливаем file handler для записи в файл
        fh = logging.FileHandler(os.path.join(self.log_dir, 'info.log'))
        formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger

    def _clone_repository(self, project_url):
        """Клонирует репозиторий."""
        repo_name = project_url.split("/")[-1].replace(".git", "")
        repo_dir = os.path.join(self.repo_folder, repo_name)
        
        try:
            full_url = f"https://{os.getenv('GIT_USERNAME')}:{os.getenv('GIT_TOKEN')}@" + project_url.replace("https://", "")
            self.logger.info(f"Cloning repository: {repo_name}")
            Repo.clone_from(full_url, repo_dir)
            return repo_name, repo_dir
        except Exception as e:
            self.logger.error(f"Failed to clone {project_url}: {e}")
            return None, None

    def _count_lines(self, repo_path):
        """Подсчитывает строки кода, используя оптимизированный поиск по расширению."""
        language_lines = {lang: 0 for lang in self.languages}
        total_lines = 0

        for root, _, files in os.walk(repo_path):
            for file in files:
                _, ext = os.path.splitext(file)
                # Быстрый поиск языка по расширению через словарь
                lang = self.ext_to_lang.get(ext.lower())
                if lang:
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            non_empty = sum(1 for line in f if line.strip())
                            language_lines[lang] += non_empty
                            total_lines += non_empty
                    except (IOError, UnicodeDecodeError) as e:
                        self.logger.warning(f"Could not read {file}: {e}")
        
        return language_lines, total_lines

    def _analyze_project(self, project_url):
        """Анализирует один проект."""
        repo_name, repo_path = self._clone_repository(project_url)
        if not repo_path:
            return None

        language_lines, total_lines = self._count_lines(repo_path)
        shutil.rmtree(repo_path, ignore_errors=True)
        return RepoStats(project_url, repo_name, language_lines, total_lines)

    def analyze_projects(self):
        """Анализирует все проекты с использованием многопоточности."""
        self.logger.info(f"Analyzing {len(self.projects)} projects...")
        # Увеличиваем количество потоков для ускорения клонирования
        max_workers = os.cpu_count() or 4
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(self._analyze_project, self.projects):
                if result:
                    self.results.append(result)
        self.logger.info("Project analysis complete.")

    def save_csv(self):
        """Сохраняет результаты в CSV-файл."""
        data = []
        for res in self.results:
            row = {
                "Project URL": res.url,
                "Project Name": res.name,
                **res.language_lines,
                "Total lines": res.total_lines
            }
            data.append(row)

        df = pd.DataFrame(data)
        csv_path = os.path.join(self.reports_dir, 'count.csv')
        df.to_csv(csv_path, sep=';', encoding='utf-8-sig', index=False)
        self.logger.info(f"Report saved to {csv_path}")

    def generate_charts(self):
        """Генерирует гистограмму и круговую диаграмму."""
        
        # Используем pandas для агрегации данных, это быстрее и читабельнее
        df = pd.DataFrame([res.language_lines for res in self.results]).fillna(0).T
        df['Total'] = df.sum(axis=1)
        df = df[df['Total'] > 0].sort_values('Total', ascending=False)

        # Гистограмма
        with plt.style.context('cyberpunk'):
            fig, ax = plt.subplots(figsize=(16, 9))
            colors = plt.cm.plasma(np.linspace(0.2, 1, len(df)))
            
            df['Total'].plot(kind='bar', ax=ax, color=colors)
            ax.set_title("Distribution of Lines of Code by Language")
            ax.set_xlabel("Language")
            ax.set_ylabel("Lines of Code")

            # Добавляем подписи к столбцам
            for p in ax.patches:
                ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='bottom', rotation=30)
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.reports_dir, 'histogram_chart.pdf'), dpi=300)
            plt.close(fig)
            self.logger.info("Histogram chart generated.")

        # Круговая диаграмма
        with plt.style.context('cyberpunk'):
            fig, ax = plt.subplots(figsize=(16, 9))
            ax.pie(
                df['Total'], labels=df.index,
                autopct=lambda pct: f"{pct:.1f}%" if pct > 1.5 else '',
                startangle=45, wedgeprops=dict(width=0.5)
            )
            ax.axis('equal')
            ax.set_title("Percentage of Lines of Code by Language")
            plt.tight_layout()
            plt.savefig(os.path.join(self.reports_dir, 'donut_chart.pdf'), dpi=300)
            plt.close(fig)
            self.logger.info("Donut chart generated.")


    def run(self):
        """Запускает весь процесс анализа."""
        self.analyze_projects()
        self.save_csv()
        
        if self.results:
            self.generate_charts()
            total = sum(r.total_lines for r in self.results)
            print(f"Total lines of code: {total:,}")
            self.logger.info(f"Total lines of code: {total}")
        else:
            print("No projects were analyzed.")
            self.logger.warning("No projects were analyzed.")

if __name__ == '__main__':
    CodeLineMeter().run()