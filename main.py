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
from matplotlib.lines import Line2D
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Comment
from pygments.util import ClassNotFound

# Загружаем переменные окружения из файла .env
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
    def __init__(self, projects_file='project.txt'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_dir = os.path.join(base_dir, 'logs')
        self.reports_dir = os.path.join(base_dir, 'reports')
        self.repo_folder = os.path.join(base_dir, "repo")

        self.projects = self.load_projects(projects_file)
        self.results = []
        self.global_start_time = datetime.datetime.now()

        self._create_directories()
        self.logger = self._setup_logging()

    def load_projects(self, file_path):
        """Загружает список проектов из текстового файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.logger.error(f"Файл {file_path} не найден.")
            return []

    def _create_directories(self):
        """Создает необходимые директории."""
        for path in [self.log_dir, self.reports_dir, self.repo_folder]:
            os.makedirs(path, exist_ok=True)

    def _setup_logging(self):
        """Настраивает логирование."""
        logger = logging.getLogger("CodeLineMeter")
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(os.path.join(self.log_dir, 'info.log'))
        formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        fh.setFormatter(formatter)
        if not logger.handlers:
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
            shutil.rmtree(repo_dir, ignore_errors=True)
            return None, None

    def _count_lines(self, repo_path):
        """
        Подсчитывает строки кода, исключая комментарии.
        Использует Pygments для определения языка и токенизации.
        """
        language_lines = {}
        total_lines = 0

        for root, _, files in os.walk(repo_path):
            for file in files:
                filepath = os.path.join(root, file)
                
                try:
                    # Читаем содержимое файла и определяем лексер
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lexer = guess_lexer_for_filename(filepath, content, encoding='utf-8')

                except (ClassNotFound, UnicodeDecodeError, FileNotFoundError) as e:
                    self.logger.warning(f"Could not process {file}: {e}")
                    continue

                lang = lexer.name
                language_lines.setdefault(lang, 0)

                non_comment_lines = 0
                current_line_has_code = False
                
                tokens = lexer.get_tokens(content)
                for token_type, value in tokens:
                    if Comment in token_type:
                        continue
                    
                    if value.strip():
                        current_line_has_code = True
                    
                    if '\n' in value:
                        if current_line_has_code:
                            non_comment_lines += 1
                        current_line_has_code = False
                
                if current_line_has_code:
                    non_comment_lines += 1

                language_lines[lang] += non_comment_lines
                total_lines += non_comment_lines
    
        return {lang: count for lang, count in language_lines.items() if count > 0}, total_lines

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
        if not self.projects:
            self.logger.warning("No projects found in project.txt.")
            return

        self.logger.info(f"Analyzing {len(self.projects)} projects...")
        max_workers = os.cpu_count() or 4
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(self._analyze_project, self.projects):
                if result:
                    self.results.append(result)
        self.logger.info("Project analysis complete.")

    def save_csv(self):
        """Сохраняет результаты в CSV-файл."""
        if not self.results:
            self.logger.warning("No results to save.")
            return
            
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
        if not self.results:
            self.logger.warning("No data to generate charts.")
            return

        df = pd.DataFrame([res.language_lines for res in self.results]).fillna(0).T
        df['Total'] = df.sum(axis=1)
        df = df[df['Total'] > 0].sort_values('Total', ascending=False)

        if df.empty:
            self.logger.warning("No code lines found to generate charts.")
            return

        # Гистограмма
        with plt.style.context('cyberpunk'):
            fig, ax = plt.subplots(figsize=(16, 10))
            colors = plt.cm.turbo(np.linspace(0.2, 1, len(df)))
            
            bars = plt.bar(df.index, df['Total'], color=colors)
            
            ax.set_title("Distribution of Lines of Code by Language")
            ax.set_xlabel("Language")
            ax.set_ylabel("Lines of Code")

            plt.xticks(rotation=45, ha='right')
            
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{int(height):,}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', rotation=30)
            
            legend_elements = [Line2D([0], [0], color=c, lw=4, label=l) for c, l in zip(colors, df.index)]
            ax.legend(handles=legend_elements, title="Languages", loc='upper right')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.reports_dir, 'histogram_chart.pdf'), dpi=300)
            plt.close(fig)
            self.logger.info("Histogram chart generated.")

        # Круговая диаграмма
        with plt.style.context('cyberpunk'):
            sizes = df['Total']
            labels = [f"{lang} ({int(count):,})" if count / sum(sizes) >= 0.015 else '' for lang, count in zip(df.index, sizes)]
            explode = [0.1 if lang == df.index[0] else 0 for lang in df.index]
            colors = plt.cm.plasma(np.linspace(0.1, 1, len(df)))
            
            fig, ax = plt.subplots(figsize=(16, 10))
            wedges, text_labels, pct_texts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                                  autopct=lambda pct: f"{pct:.1f}%" if pct > 1.5 else '',
                                                  startangle=90, wedgeprops=dict(width=0.5), rotatelabels=True)
            
            # Настройка видимости для меток и текста процентов
            for label, pct_text in zip(text_labels, pct_texts):
                if label.get_text() == '':
                    label.set_alpha(0)  # Скрываем метки для мелких секторов
                    pct_text.set_alpha(0)  # Скрываем проценты для этих же секторов
                else:
                    label.set_color('white')
                    label.set_fontsize(12)
                    pct_text.set_color('white')
                    pct_text.set_fontsize(12)

            ax.axis('equal')
            # ax.set_title("Percentage of Lines of Code by Language")
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.reports_dir, 'donut_chart.pdf'), dpi=300, orientation='portrait', bbox_inches='tight')
            plt.close(fig)
            self.logger.info("Donut chart generated.")

    def run(self):
        start_time = datetime.datetime.now()
        self.logger.info("Starting code line meter...")

        self.analyze_projects()
        self.save_csv()
        self.generate_charts()
        
        if self.results:
            total_lines = sum(r.total_lines for r in self.results)
            print(f"Total lines of code: {total_lines:,}")
            self.logger.info(f"Total lines of code: {total_lines}")
        else:
            print("No projects were analyzed.")
            self.logger.info("No projects were analyzed.")

        end_time = datetime.datetime.now()
        duration = end_time - start_time
        self.logger.info(f"Process finished in {duration}")
        print(f"Process finished in {duration}")


if __name__ == '__main__':
    # Убедитесь, что у вас установлен pygments: pip install pygments
    CodeLineMeter().run()