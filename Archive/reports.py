import circlify
import matplotlib.pyplot as plt
import mplcyberpunk
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class CodeLineMeter:
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

        # Построение гистограммы
        fig = px.bar(df, x='Language', y='Count', text='Count', color='Language',
                     color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_traces(texttemplate='%{text}', textposition='outside', textangle=-30, textfont=dict(size=16))
        annotations = []
        fig.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            width=1600, height=900, margin=dict(t=15, l=15, r=15, b=15),
            xaxis_title='Programming languages',
            yaxis_title='Total rows',
            xaxis=dict(title_font=dict(size=25), tickfont=dict(size=16), tickangle=-30),
            yaxis=dict(title_font=dict(size=25), tickfont=dict(size=16), linewidth=1),
            annotations=annotations,
            showlegend=False
        )
        fig.add_annotation(
            text=f'<b>Total Lines: <span style="color: red;">{total_lines}</span></b><br>'
                f'<b>Program Code: <span style="color: blue;">{programm_value}</span></b><br>'
                f'<b>Markdown Lines: <span style="color: green;">{md_value}</span></b><br>'
                f'<b>Any Text Lines: <span style="color: orange;">{text_value}</span></b><br>'
                f'<b>Other Code Lines: <span style="color: purple;">{other_value}</span></b>',
            xref='paper', yref='paper',
            x=0.9, y=0.97,
            showarrow=False,
            font=dict(size=20),
            align='left',
            bgcolor='white'
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
            legend=dict(font=dict(size=14)),
            legend_orientation="v",
            annotations=[dict(text='Соотношение<br>количества строк<br>программного кода<br>в Git<br>репозитории(ях)',
            x=0.5, y=0.5, font_size=30, showarrow=False)]
        )

        donut_diagram_pdf_path = os.path.join(reports_dir, 'donut_diagram.pdf')
        fig.write_image(donut_diagram_pdf_path, engine="kaleido", format="pdf", width=1920, height=1080, scale=1.25)

        # Построение диаграммы пузырьки в пузыре
        circles = circlify.circlify(df['Count'].tolist(), 
                            show_enclosure=False, 
                            target_enclosure=circlify.Circle(x=0, y=0)
                           )
        circles.reverse()
        fig, ax = plt.subplots(figsize=(14, 14), facecolor='white')
        ax.axis('off')
        lim = max(max(abs(circle.x)+circle.r, abs(circle.y)+circle.r,) for circle in circles)
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)
        # Рисуем круги
        for circle, label, emi, color in zip(circles, df['Language'], df['Count'], 
                                             plt.cm.turbo(np.linspace(0, 1, len(df['Language'])))):
            x, y, r = circle
            ax.add_patch(plt.Circle((x, y), r, alpha=0.9, color = color))
            plt.annotate(label +'\n'+ format(emi, ","), (x,y), size=15, va='center', ha='center')
        plt.xticks([])
        plt.yticks([])
        bubble_in_bubble_pdf_path = os.path.join(reports_dir, 'bubble_in_bubble.pdf')
        plt.savefig(bubble_in_bubble_pdf_path, format="pdf", dpi=300, orientation='portrait', bbox_inches='tight')


        # Построение пузырьковой диаграммы
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Language'],
            y=df['Count'],
            mode='markers',
            marker=dict(
                size=df['Count'],
                sizemode='diameter',
                sizeref=0.8 * df['Count'].max() / 100.0,
                sizemin=15,
                color=df['Count'],  # Используем столбец 'Count' для определения цвета пузырьков
                colorscale='mrybm',  # Выбираем цветовую схему (можно выбрать другую схему)
                showscale=True,  # Показываем шкалу цвета
                colorbar=dict(tickfont=dict(size=18)),  # Устанавливаем размер шрифта Цветового столба
            )
        ))

        fig.update_layout(
            title={
                    'text': 'Пузырьковая диаграмма',
                    'x': 0.5,
                    'font': {'size': 36}
                    },
            xaxis_title='Языки программирования',
            yaxis_title='Количество строк кода',
            xaxis=dict(title_font=dict(size=25), tickfont=dict(size=20)),
            yaxis=dict(title_font=dict(size=25), tickfont=dict(size=20)),
            plot_bgcolor='white', paper_bgcolor='white',
        )

        bubble_chart_pdf_path = os.path.join(reports_dir, 'bubble_chart.pdf')
        fig.write_image(bubble_chart_pdf_path, engine="kaleido", format="pdf", width=1920, height=1080, scale=1.25)


        # Построение Polar диаграммы
        plt.gcf().set_size_inches(14, 14)
        sns.set_style('darkgrid')
        # Установим максимальное значение
        max_val = max(df['Count'])*1.10
        ax = plt.subplot(projection='polar')
        for i in range(len(df)):
            ax.barh(i, list(df['Count'])[i]*2*np.pi/max_val,
            label=list(df['Language'])[i], color=plt.cm.plasma(i/len(df)))
        # Зададим внутренний график
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(1)
        ax.set_rlabel_position(-1)
        ax.set_thetagrids([], labels=[])
        ax.set_rgrids(range(len(df)), labels= df['Count'])
        # Установим проекцию
        ax = plt.subplot(projection='polar')
        plt.legend(bbox_to_anchor=(1, 1), loc=2)
        polar_chart_pdf_path = os.path.join(reports_dir, 'polar_chart.pdf')
        plt.savefig(polar_chart_pdf_path, format="pdf", dpi=300, orientation='portrait', bbox_inches='tight')


        # Построение Радиальной диаграммы
        plt.figure(figsize=(12, 12))
        ax = plt.subplot(111, polar=True)
        plt.axis()
        # Установим минимальное и максимальное значение
        lowerLimit = 0
        max_v = df['Count'].max()
        # Установим высоту и ширину
        heights = df['Count']
        width = 2 * np.pi / len(df.index)
        # Установим индекс и угол
        indexes = list(range(1, len(df.index) + 1))
        angles = [element * width for element in indexes]
        # Градиент цветов по языкам
        colors = plt.cm.viridis(np.linspace(0, 1, len(df.index)))
        bars = ax.bar(x=angles, height=heights, width=width, bottom=lowerLimit,
                      linewidth=1, edgecolor="white", color=colors)
        labelPadding = 15
        for bar, angle, height, label in zip(bars, angles, heights, df['Language']):
            rotation = np.rad2deg(angle)
            alignment = ""
            # Разберемся с направлением
            if angle >= np.pi / 2 and angle < 3 * np.pi / 2:
                alignment = "right"
                rotation = rotation + 180
            else:
                alignment = "left"
            ax.text(x=angle, y=lowerLimit + bar.get_height() + labelPadding,
                    s=label, ha=alignment, va='center', rotation=rotation,
                    rotation_mode="anchor", color='Black')
            ax.set_thetagrids([], labels=[])
            
            ax.text(x=angle, y=lowerLimit + bar.get_height() / 2,
                    s=height, ha=alignment, va='center', rotation=rotation,
                    rotation_mode="anchor", color='white')

        radial_chart_pdf_path = os.path.join(reports_dir, 'radial_chart.pdf')
        plt.savefig(radial_chart_pdf_path, format="pdf", dpi=300, orientation='portrait', bbox_inches='tight')