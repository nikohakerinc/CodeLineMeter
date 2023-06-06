import os
import gitlab
import logging
import csv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv


load_dotenv()
GIT_URL = os.getenv('GIT_URL')
GIT_TOKEN = os.getenv('GIT_TOKEN')
GIT_USERNAME = os.getenv('GIT_USERNAME')
GIT_PASSWORD = os.getenv('GIT_PASSWORD')

gl = gitlab.Gitlab(GIT_URL, private_token=GIT_TOKEN)

# Создаем директорию для логов, если она не существует
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Задаем уровень логов
logging.basicConfig(filename=os.path.join(log_dir, 'info.log'), level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

gl = gitlab.Gitlab(GIT_URL, private_token=GIT_TOKEN)

# Инициализация словаря с языками программирования
languages = {
    'Python': ['.py', '.bzl', '.cgi', '.fcgi', '.gyp', '.lmi', '.pyde', '.pyp', '.pyt', '.pyw', '.rpy', '.tac', '.wsgi', '.xpy', '.pytb'],
    'Java': ['.java', '.jsp'],
    'C': ['.c', '.cats', '.h', '.idc', '.w'],
    'C++': ['.cpp', '.c++', '.cc', '.cp', '.cxx', '.h', '.h++', '.hh', '.hpp', '.hxx', '.inc', '.inl', '.ipp', '.tcc', '.tpp'],
    'Objective-C/C++/J': ['.m', '.h', '.mm', 'j', '.sj'],
    'C#': ['.cs', '.cake', '.cshtml', '.csx'],
    'JavaScript': ['.js', '.mjs', '.jsx', '._js', '.bones', '.es', '.es6', '.frag', '.gs', '.jake', '.jscad', '.jsfl', '.jsm', '.jss', '.njs', '.pac', '.sjs', '.ssjs', '.sublime-build', '.sublime-commands', '.sublime-completions', '.sublime-keymap', '.sublime-macro', '.sublime-menu', '.sublime-mousemap', '.sublime-project', '.sublime-settings', '.sublime-theme', '.sublime-workspace', '.sublime_metrics', '.sublime_session', '.xsjs', '.xsjslib'],
    'PHP': ['.php', '.aw', '.ctp', '.fcgi', '.inc', '.php3', '.php4', '.php5', '.phps', '.phpt'],
    'Ruby': ['.rb','.builder', '.fcgi', '.gemspec', '.god', '.irbrc', '.jbuilder', '.mspec', '.pluginspec', '.podspec', '.rabl', '.rake', '.rbuild', '.rbw', '.rbx', '.ru', '.ruby', '.thor', '.watchr'],
    'Swift': ['.swift', '.swiftmodule', '.swiftdoc', '.xcassets', '.xcconfig', '.entitlements', '.xcscheme', '.pbxproj'],
    'Go': ['.go', 'go.mod', 'go.sum', '_test.go'],
    'Rust': ['.rs', '.rs.in'],
    'Kotlin': ['.kt', '.ktm', '.kts'],
    'TypeScript': ['.ts', '.tsx'],
    'SQL': ['.pls', '.pck', '.pkb', '.pks', '.plb', '.plsql', '.sql', '.cql', '.ddl', '.inc', '.prc', '.tab', '.udf', '.viw', '.db2'],
    'Shell': ['.sh', '.bash', '.bats', '.cgi', '.command', '.fcgi', '.ksh', '.sh.in', '.tmux', '.tool', '.zsh', '.sh-session'],
    'PowerShell': ['.ps1', '.psd1', '.psm1'],
    'Batch': ['.bat', '.cmd'],
    'Perl': ['.pl', '.al', '.cgi', '.fcgi', '.perl', '.ph', '.plx', '.pm', '.pod', '.psgi', '.t'],
    'HTML': ['.html', '.rhtml', '.htm', '.html.hl', '.inc', '.st', '.xht', '.xhtml', '.mustache', '.jinja', '.eex', '.phtml'],
    'CSS': ['.css', '.mss', '.scss'],
    'Basic': ['.bb', '.decls', '.pb', '.pbi', '.rbbas', '.rbfrm', '.rbmnu', '.rbres', '.rbtbar', '.rbuistate', '.vb', '.bas', '.cls', '.frm', '.frx', '.vba', '.vbhtml', '.vbs'],
    'Pascal': ['.pas', '.dfm', '.dpr', '.inc', '.lpr', '.pp', '.cp', '.cps'],
    'FORTRAN': ['.f90', '.f', '.f03', '.f08', '.f77', '.f95', '.for', '.fpp'],
    'Kobol': ['.cob', '.cbl', '.ccp', '.cobol', '.cpy'],
    'Groovy': ['.groovy', '.grt', '.gtpl', '.gvy', '.gsp'],
    'JSON': ['.json', '.geojson', '.lock', '.topojson', '.json5', '.jsonld', '.jq'],
    'YAML': ['.yml', '.reek', '.rviz', '.sublime-syntax', '.syntax', '.yaml', '.yaml-tmlanguage'],
    'XML': ['.xml', '.io', '.ant', '.axml', '.ccxml', '.clixml', '.cproject', '.csl', '.csproj', '.ct', '.dita', '.ditamap', '.ditaval', '.dll.config', '.dotsettings', '.filters', '.fsproj', '.fxml', '.glade', '.gml', '.grxml', '.iml', '.ivy', '.jelly', '.jsproj', '.kml', '.launch', '.mdpolicy', '.mxml', '.nproj', '.nuspec', '.odd', '.osm', '.plist', '.pluginspec', '.props', '.ps1xml', '.psc1', '.pt', '.rdf', '.rss', '.scxml', '.srdf', '.storyboard', '.stTheme', '.sublime-snippet', '.targets', '.tmCommand', '.tml', '.tmLanguage', '.tmPreferences', '.tmSnippet', '.tmTheme', '.ui', '.urdf', '.ux', '.vbproj', '.vcxproj', '.vssettings', '.vxml', '.wsdl', '.wsf', '.wxi', '.wxl', '.wxs', '.x3d', '.xacro', '.xaml', '.xib', '.xlf', '.xliff', '.xmi', '.xml.dist', '.xproj', '.xsd', '.xul', '.zcml'],
    'Markdown': ['.md', '.rmd', '.markdown', '.mkd', '.mkdn', '.mkdown', '.ron'],
    'Text': ['.txt', '.doc', '.docx', '.fr', '.nb', '.ncl', '.no', '.textile', '.csv', '.asciidoc', '.adoc', '.asc', '.creole', '.po', '.pot', '.haml', '.haml.deface', '.handlebars', '.hbs', '.mediawiki', '.wiki', '.org', '.rst', '.rest'],
    'Log files': ['.log', '.irclog', '.weechatlog', '.sv', '.svh', '.vh'],
    'Config files': ['.env', '.venv', '.conf', '.config', '.cfg', '.ini', '.prefs', '.pro', '.properties', '.nginxconf', '.vhost'],
    'Other Lang': ['.asc', '.mod', '.g4', '.apib', '.apl', '.dyalog', '.ascx', '.ashx', '.asmx', '.aspx', '.ads', '.agda', '.als', '.scpt', '.arc', '.aj', '.asm', '.inc', '.nasm', '.ahk', '.ahkl', '.au3', '.awk', '.auk', '.gawk', '.mawk', '.nawk', '.befunge', '.bison', '.bmx', '.bsv', '.boo', '.b', '.bf', '.brs', '.bro', '.chs', '.clp', '.cmake', '.cmake.in', '.capnp', '.ceylon', '.chpl', '.ch', '.ck', '.cirru', '.clw', '.icl', '.dcl', '.click', '.clj', '.boot', '.cl2', '.cljc', '.cljs', '.cljs.hl', '.cljscm', '.cljx', '.hic', '.coffee', '._coffee', '.cake', '.cjsx', '.cson', '.iced', '.cfm', '.cfml', '.cfc', '.lisp', '.asd', '.cl', '.l', '.lsp', '.ny', '.podsl', '.sexp', '.cl', '.coq', '.v', '.cr', '.feature', '.cu', '.cuh', '.cy', '.pyx', '.pxd', '.pxi', '.d', '.di', '.com', '.dm', '.diff', '.patch', '.djs', '.dylan', '.dyl', '.intr', '.lid', '.E', '.ecl', '.eclxml', '.sch', '.brd', '.epj', '.e', '.ex', '.exs', '.elm', '.el', '.emacs', '.emacs.desktop', '.em', '.emberscript', '.erl', '.es', '.escript', '.hrl', '.xrl', '.yrl', '.fs', '.fsi', '.fsx', '.factor', '.fy', '.fancypack', '.fan', '.fs', '.fth', '.4th', '.f', '.for', '.forth', '.fr', '.frt', '.fs', '.ftl', '.fr', '.gms', '.g', '.gap', '.gd', '.gi', '.tst', '.s', '.ms', '.gd', '.glsl', '.fp', '.frag', '.frg', '.fs', '.fsh', '.fshader', '.geo', '.geom', '.glslv', '.gshader', '.shader', '.vert', '.vrx', '.vsh', '.vshader', '.gml', '.kid', '.ebuild', '.eclass', '.glf', '.gp', '.gnu', '.gnuplot', '.plot', '.plt', '.golo', '.gs', '.gst', '.gsx', '.vark', '.grace', '.gradle', '.gf', '.hcl', '.tf', '.hlsl', '.fx', '.fxh', '.hlsli', '.hh', '.hb', '.hs', '.hsc', '.hx', '.hxsl', '.hy', '.bf', '.pro', '.dlm', '.ipf', '.idr', '.lidr', '.ni', '.i7x', '.iss', '.ik', '.thy', '.ijs', '.flex', '.jflex', '.jsx', '.jade', '.j', '.jl', '.ipynb', '.krl', '.sch', '.brd', '.kicad_pcb', '.kit', '.lfe', '.ll', '.lol', '.lsl', '.lslp', '.lvproj', '.lasso', '.las', '.lasso8', '.lasso9', '.ldml', '.latte', '.lean', '.hlean', '.less', '.l', '.lex', '.ly', '.ily', '.b', '.liquid', '.lagda', '.litcoffee', '.lhs', '.ls', '._ls', '.xm', '.x', '.xi', '.lgt', '.logtalk', '.lookml', '.ls', '.lua', '.fcgi', '.nse', '.pd_lua', '.rbxs', '.wlua', '.mumps', '.m4', '.ms', '.mcr', '.mtml', '.muf', '.mak', '.d', '.mk', '.mkfile', '.mako', '.mao', '.mask', '.mathematica', '.cdf', '.ma', '.mt', '.nb', '.nbp', '.wl', '.wlt', '.matlab', '.maxpat', '.maxhelp', '.maxproj', '.mxt', '.pat', '.moo', '.metal', '.minid', '.druby', '.duby', '.mir', '.mirah', '.mo', '.mod', '.mms','.mmk', '.monkey', '.moo', '.moon', '.myt', '.nl', '.nsi', '.nsh', '.n', '.axs', '.axi', '.axs.erb', '.axi.erb', '.nlogo', '.nl', '.lisp', '.lsp', '.nim', '.nimrod', '.nit', '.nix', '.nu', '.numpy', '.numpyw', '.numsc', '.ml', '.eliom', '.eliomi', '.ml4', '.mli', '.mll', '.mly', '.omgrofl', '.opa', '.opal', '.cl', '.opencl', '.scad', '.ox', '.oxh', '.oxo', '.oxygene', '.oz', '.pwn', '.inc', '.pov', '.pan', '.psc', '.parrot', '.pasm', '.pir', '.6pl', '.6pm', '.nqp', '.p6', '.p6l', '.p6m', '.pl', '.pl6', '.pm', '.pm6', '.pkl', '.l', '.pig', '.pike', '.pmod', '.pod', '.pogo', '.pony', '.ps', '.eps', '.pde', '.pl', '.pro', '.prolog', '.yap', '.spin', '.proto', '.asc', '.pub', '.pp', '.pd', '.pb', '.pbi', '.purs', '.qml', '.qbs', '.pro', '.pri', '.r', '.rd', '.rsx', '.raml', '.rdoc', '.rkt', '.rktd', '.rktl', '.scrbl', '.rl', '.reb', '.r2', '.r3', '.rebol', '.red', '.reds', '.cw', '.rs', '.rsh', '.robot', '.rg', '.sas', '.smt2', '.smt', '.sage', '.sagews', '.sls', '.sass', '.scala', '.sbt', '.sc', '.scaml', '.scm', '.sld', '.sls', '.sps', '.ss', '.sci', '.sce', '.tst', '.self', '.shen', '.sl', '.slim', '.smali', '.st', '.tpl', '.sp', '.sma', '.nut', '.stan', '.ML', '.fun', '.sig', '.sml', '.do', '.ado', '.doh', '.ihlp', '.mata', '.matah', '.sthlp', '.styl', '.sc', '.scd', '.txl', '.tcl', '.adp', '.tm', '.tcsh', '.csh', '.tex', '.aux', '.bbx', '.bib', '.cbx', '.cls', '.dtx', '.ins', '.lbx', '.ltx', '.mkii', '.mkiv', '.mkvi', '.sty', '.toc', '.tea', '.thrift', '.tu', '.twig', '.upc', '.uno', '.uc', '.ur', '.urs', '.vcl', '.vhdl', '.vhd', '.vhf', '.vhi', '.vho', '.vhs', '.vht', '.vhw', '.vala', '.vapi', '.v', '.veo', '.vim', '.volt', '.vue', '.owl', '.webidl', '.x10', '.xc', '.xsp-config', '.xsp.metadata', '.xpl', '.xproc', '.xquery', '.xq', '.xql', '.xqm', '.xqy', '.xs', '.xslt', '.xsl', '.xojo_code', '.xojo_menu', '.xojo_report', '.xojo_script', '.xojo_toolbar', '.xojo_window', '.xtend', '.yang', '.y', '.yacc', '.yy', '.zep', '.zimpl', '.zmpl', '.zpl', '.ec', '.eh', '.edn', '.fish', '.mu', '.nc', '.ooc', '.wisp', '.prg','.ch', '.prw'],
}

# Инициализация счётчика строк кода и результирующего словаря
sum = 0
result = {}

# Создаём файл 'count.csv' и записываем в него названия колонок
with open('count.csv', 'a') as f:
    keys = ";".join(languages.keys())
    f.write(f"Project URL;Project Name;{keys};Total lines of code\n")

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

        result[repo_url] = (project_dir,) + tuple(language_lines.values()) + (total_lines,)

    # Добавляем количество строк кода проекта к общему счетчику
    sum += total_lines
    
    # Удаление скаченного репозитория
    os.system(f"rm -rf {repo_dir}")         # Если код запускается Linux
    # os.system(f"rm -rf {repo_dir}")         # Чтоб наверняка удалил папку
    os.system(f"rd /s /q {repo_dir}")       # Если код запускается в Windows
    # os.system(f"rd /s /q {repo_dir}")       # Чтоб наверняка удалил папку

# Запись результатов в файл count.csv
with open('count.csv', 'a') as f:
    for repo_url, values in result.items():
        line = f"{repo_url};{';'.join(map(str, values))}\n"
        f.write(line)

try:
    # Инициализация словаря temp
    temp = {
        'Python': 0,
        'Java': 0,
        'C': 0,
        'C++': 0,
        'Objective-C/C++/J': 0,
        'C#': 0,
        'JavaScript': 0,
        'PHP': 0,
        'Ruby': 0,
        'Swift': 0,
        'Go': 0,
        'Rust': 0,
        'Kotlin': 0,
        'TypeScript': 0,
        'SQL': 0,
        'Shell': 0,
        'PowerShell': 0,
        'Batch': 0,
        'Perl': 0,
        'HTML': 0,
        'CSS': 0,
        'Basic': 0,
        'Pascal': 0,
        'FORTRAN': 0,
        'Kobol': 0,
        'Groovy': 0,
        'JSON': 0,
        'YAML': 0,
        'XML': 0,
        'Markdown': 0,
        'Text': 0,
        'Log files': 0,
        'Config files': 0,
        'Other Lang': 0
    }

    # Чтение файла count.csv и суммирование значений по колонкам
    with open('count.csv', 'r') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)  # Пропуск заголовков колонок
        for row in reader:
            # Исключаем 1(Project URL), 2(Project Name) и последнюю колонки (Total lines)
            for i, value in enumerate(row[2:-1]):
                temp[list(temp.keys())[i]] += int(value)

    # Фильтрация колонок содержащих только нулевых значений
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

    # Запись гистограммы в файл gistogram.pdf в горизонтальной ориентации
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

    # Запись кольцевой диаграммы в файл ring_diagram.pdf в горизонтальной ориентации
    fig.write_image("ring_diagram.pdf", engine="kaleido", format="pdf", width=1920, height=1080, scale=1.25)
except:
    # Добавляем отступы и записываем общее количество строк кода в конец файла count.csv
    with open('count.csv', 'a') as f:
        f.write('\n\n')
        f.write(f"Total lines of code:; {sum}")

print(f"Total lines of code: {sum}")
