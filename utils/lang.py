# Инициализация словаря с языками программирования и списком форматов файлов для каждого языка
lang_dict = {
    'Python': ['.py', '.bzl', '.cgi', '.fcgi', '.gyp', '.lmi', '.pyde', '.pyp', '.pyt', '.pyw', '.rpy', '.tac', '.wsgi',
               '.xpy', '.pytb'],
    'Java': ['.java', '.jsp'],
    'C': ['.c', '.cats', '.h', '.idc', '.w'],
    'C++': ['.cpp', '.c++', '.cc', '.cp', '.cxx', '.h', '.h++', '.hh', '.hpp', '.hxx', '.inc', '.inl', '.ipp', '.tcc',
            '.tpp'],
    'Objective-C/C++/J': ['.m', '.h', '.mm', 'j', '.sj'],
    'C#': ['.cs', '.cake', '.cshtml', '.csx'],
    'JavaScript': ['.js', '.mjs', '.jsx', '._js', '.bones', '.es', '.es6', '.frag', '.gs', '.jake', '.jscad', '.jsfl',
                   '.jsm', '.jss', '.njs', '.pac', '.sjs', '.ssjs', '.sublime-build', '.sublime-commands',
                   '.sublime-completions', '.sublime-keymap', '.sublime-macro', '.sublime-menu', '.sublime-mousemap',
                   '.sublime-project', '.sublime-settings', '.sublime-theme', '.sublime-workspace', '.sublime_metrics',
                   '.sublime_session', '.xsjs', '.xsjslib'],
    'PHP': ['.php', '.aw', '.ctp', '.fcgi', '.inc', '.php3', '.php4', '.php5', '.phps', '.phpt'],
    'Ruby': ['.rb', '.builder', '.fcgi', '.gemspec', '.god', '.irbrc', '.jbuilder', '.mspec', '.pluginspec', '.podspec',
             '.rabl', '.rake', '.rbuild', '.rbw', '.rbx', '.ru', '.ruby', '.thor', '.watchr'],
    'Swift': ['.swift', '.swiftmodule', '.swiftdoc', '.xcassets', '.xcconfig', '.entitlements', '.xcscheme',
              '.pbxproj'],
    'Go': ['.go', 'go.mod', 'go.sum', '_test.go'],
    'Rust': ['.rs', '.rs.in'],
    'Kotlin': ['.kt', '.ktm', '.kts'],
    'Lua': ['.lua', '.luna', '.lunaire', '.anair'],
    'Scala': ['.scala', '.sc'],
    'TypeScript': ['.ts', '.tsx'],
    'SQL': ['.pls', '.pck', '.pkb', '.pks', '.plb', '.plsql', '.sql', '.cql', '.ddl', '.inc', '.prc', '.tab', '.udf',
            '.viw', '.db2'],
    'Shell': ['.sh', '.bash', '.bats', '.cgi', '.command', '.fcgi', '.ksh', '.sh.in', '.tmux', '.tool', '.zsh',
              '.sh-session'],
    'PowerShell': ['.ps1', '.psd1', '.psm1'],
    'Batch': ['.bat', '.cmd'],
    'Perl': ['.pl', '.al', '.cgi', '.fcgi', '.perl', '.ph', '.plx', '.pm', '.pod', '.psgi', '.t'],
    'HTML': ['.html', '.rhtml', '.htm', '.html.hl', '.inc', '.st', '.xht', '.xhtml', '.mustache', '.jinja', '.eex',
             '.phtml'],
    'CSS': ['.css', '.mss', '.scss'],
    'Basic': ['.bb', '.decls', '.pb', '.pbi', '.rbbas', '.rbfrm', '.rbmnu', '.rbres', '.rbtbar', '.rbuistate', '.vb',
              '.bas', '.cls', '.frm', '.frx', '.vba', '.vbhtml', '.vbs'],
    'Pascal/Delphi': ['.pas', '.dfm', '.dpr', '.dpk', '.dproj', '.fmx', '.bpl', '.inc', '.lpr', '.pp', '.cp', '.cps'],
    'FORTRAN': ['.f90', '.f', '.f03', '.f08', '.f77', '.f95', '.for', '.fpp'],
    'Kobol': ['.cob', '.cbl', '.ccp', '.cobol', '.cpy'],
    'Groovy': ['.groovy', '.grt', '.gtpl', '.gvy', '.gsp'],
    'JSON': ['.json', '.geojson', '.lock', '.topojson', '.json5', '.jsonld', '.jq'],
    'YAML': ['.yml', '.reek', '.rviz', '.sublime-syntax', '.syntax', '.yaml', '.yaml-tmlanguage'],
    'XML': ['.xml', '.io', '.ant', '.axml', '.ccxml', '.clixml', '.cproject', '.csl', '.csproj', '.ct', '.dita',
            '.ditamap', '.ditaval', '.dll.config', '.dotsettings', '.filters', '.fsproj', '.fxml', '.glade', '.gml',
            '.grxml', '.iml', '.ivy', '.jelly', '.jsproj', '.kml', '.launch', '.mdpolicy', '.mxml', '.nproj', '.nuspec',
            '.odd', '.osm', '.plist', '.pluginspec', '.props', '.ps1xml', '.psc1', '.pt', '.rdf', '.rss', '.scxml',
            '.srdf', '.storyboard', '.stTheme', '.sublime-snippet', '.targets', '.tmCommand', '.tml', '.tmLanguage',
            '.tmPreferences', '.tmSnippet', '.tmTheme', '.ui', '.urdf', '.ux', '.vbproj', '.vcxproj',
            '.vssettings', '.vxml', '.wsdl', '.wsf', '.wxi', '.wxl', '.wxs', '.x3d', '.xacro', '.xaml', '.xib', '.xlf',
            '.xliff', '.xmi', '.xml.dist', '.xproj', '.xsd', '.xul', '.zcml'],
    'Markdown': ['.md', '.rmd', '.markdown', '.mkd', '.mkdn', '.mkdown', '.ron'],
    'Text': ['.txt', '.doc', '.docx', '.fr', '.nb', '.ncl', '.no', '.textile', '.csv', '.asciidoc', '.adoc',
             '.asc', '.creole', '.po', '.pot', '.haml', '.haml.deface', '.handlebars', '.hbs', '.mediawiki', '.wiki',
             '.org', '.rst', '.rest'],
    'Log files': ['.log', '.irclog', '.weechatlog', '.sv', '.svh', '.vh'],
    'Config files': ['.env', '.venv', '.conf', '.config', '.cfg', '.ini', '.prefs', '.pro', '.properties', '.nginxconf',
                     '.vhost'],
    'Other Lang': ['.asc', '.mod', '.g4', '.apib', '.apl', '.dyalog', '.ascx', '.ashx', '.asmx', '.aspx', '.ads',
                   '.agda', '.als', '.scpt', '.arc', '.aj', '.asm', '.inc', '.nasm', '.ahk', '.ahkl', '.au3', '.awk',
                   '.auk', '.gawk', '.mawk', '.nawk', '.befunge', '.bison', '.bmx', '.bsv', '.boo', '.b', '.bf', '.brs',
                   '.bro', '.chs', '.clp', '.cmake', '.cmake.in', '.capnp', '.ceylon', '.chpl', '.ch', '.ck', '.cirru',
                   '.clw', '.icl', '.dcl', '.click', '.clj', '.boot', '.cl2', '.cljc', '.cljs', '.cljr', '.cljs.hl',
                   '.cljscm', '.cljx', '.hic', '.coffee', '._coffee', '.cake', '.cjsx', '.cson', '.iced', '.cfm',
                   '.cfml', '.cfc', '.lisp', '.asd', '.cl', '.l', '.lsp', '.ny', '.podsl', '.sexp', '.cl', '.coq', '.v',
                   '.cr', '.feature', '.cu', '.cuh', '.cy', '.pyx', '.pxd', '.pxi', '.d', '.di', '.dart', '.com', '.dm',
                   '.diff', '.patch', '.djs', '.dylan', '.dyl', '.intr', '.lid', '.E', '.ecl', '.eclxml', '.sch',
                   '.brd', '.epj', '.e', '.ex', '.exs', '.elm', '.el', '.emacs', '.emacs.desktop', '.em',
                   '.emberscript', '.erl', '.es', '.escript', '.hrl', '.xrl', '.yrl', '.fs', '.fsi', '.fsx', '.factor',
                   '.fy', '.fancypack', '.fan', '.fs', '.fth', '.4th', '.f', '.for', '.forth', '.fr', '.frt', '.fs',
                   '.ftl', '.fr', '.gms', '.g', '.gap', '.gd', '.gi', '.tst', '.s', '.ms', '.gd', '.glsl', '.fp',
                   '.frag', '.frg', '.fs', '.fsh', '.fshader', '.geo', '.geom', '.glslv', '.gshader', '.shader',
                   '.vert', '.vrx', '.vsh', '.vshader', '.gml', '.kid', '.ebuild', '.eclass', '.glf', '.gp', '.gnu',
                   '.gnuplot', '.plot', '.plt', '.golo', '.gs', '.gst', '.gsx', '.vark', '.grace', '.gradle', '.gf',
                   '.hcl', '.tf', '.hlsl', '.fx', '.fxh', '.hlsli', '.hh', '.hb', '.hs', '.lhs', '.hsc', '.hx', '.hxsl',
                   '.hy', '.bf', '.pro', '.dlm', '.ipf', '.idr', '.lidr', '.ni', '.i7x', '.iss', '.ik', '.thy', '.ijs',
                   '.flex', '.jflex', '.jsx', '.jade', '.j', '.jl', '.ipynb', '.krl', '.sch', '.brd', '.kicad_pcb',
                   '.kit', '.lfe', '.ll', '.lol', '.lsl', '.lslp', '.lvproj', '.lasso', '.las', '.lasso8', '.lasso9',
                   '.ldml', '.latte', '.lean', '.hlean', '.less', '.l', '.lex', '.ly', '.ily', '.b', '.liquid',
                   '.lagda', '.litcoffee', '.lhs', '.ls', '._ls', '.xm', '.x', '.xi', '.lgt', '.logtalk', '.lookml',
                   '.ls', '.fcgi', '.nse', '.pd_lua', '.rbxs', '.wlua', '.mumps', '.m4', '.ms', '.mcr', '.mtml', '.muf',
                   '.mak', '.d', '.mk', '.mkfile', '.mako', '.mao', '.mask', '.mathematica', '.cdf', '.ma', '.mt',
                   '.nb', '.nbp', '.wl', '.wlt', '.matlab', '.maxpat', '.maxhelp', '.maxproj', '.mxt', '.pat', '.moo',
                   '.metal', '.minid', '.druby', '.duby', '.mir', '.mirah', '.mo', '.mod', '.mms', '.mmk', '.monkey',
                   '.moo', '.moon', '.myt', '.nl', '.nsi', '.nsh', '.n', '.axs', '.axi', '.axs.erb', '.axi.erb',
                   '.nlogo', '.nl', '.lisp', '.lsp', '.nim', '.nimrod', '.nit', '.nix', '.nu', '.numpy', '.numpyw',
                   '.numsc', '.ml', '.eliom', '.eliomi', '.ml4', '.mli', '.mll', '.mly', '.omgrofl', '.opa', '.opal',
                   '.cl', '.opencl', '.scad', '.ox', '.oxh', '.oxo', '.oxygene', '.oz', '.pwn', '.inc', '.pov', '.pan',
                   '.psc', '.parrot', '.pasm', '.pir', '.6pl', '.6pm', '.nqp', '.p6', '.p6l', '.p6m', '.pl', '.pl6',
                   '.pm', '.pm6', '.pkl', '.l', '.pig', '.pike', '.pmod', '.pod', '.pogo', '.pony', '.ps', '.eps',
                   '.pde', '.pl', '.pro', '.prolog', '.yap', '.spin', '.proto', '.asc', '.pub', '.pd', '.pb', '.pbi',
                   '.purs', '.qml', '.qbs', '.pro', '.pri', '.r', '.rd', '.rsx', '.raml', '.rdoc', '.rkt', '.rktd',
                   '.rktl', '.scrbl', '.rl', '.reb', '.r2', '.r3', '.rebol', '.red', '.reds', '.cw', '.rs', '.rsh',
                   '.robot', '.rg', '.sas', '.smt2', '.smt', '.sage', '.sagews', '.sls', '.sass', '.sbt', '.scaml',
                   '.scm', '.sld', '.sls', '.sps', '.ss', '.sci', '.sce', '.tst', '.self', '.shen', '.sl', '.slim',
                   '.smali', '.st', '.tpl', '.sp', '.sma', '.nut', '.stan', '.ML', '.fun', '.sig', '.sml', '.do',
                   '.ado', '.doh', '.ihlp', '.mata', '.matah', '.sthlp', '.styl', '.sc', '.scd', '.txl', '.tcl', '.adp',
                   '.tm', '.tcsh', '.csh', '.tex', '.aux', '.bbx', '.bib', '.cbx', '.cls', '.dtx', '.ins', '.lbx',
                   '.ltx', '.mkii', '.mkiv', '.mkvi', '.sty', '.toc', '.tea', '.thrift', '.tu', '.twig', '.upc', '.uno',
                   '.uc', '.ur', '.urs', '.vcl', '.vhdl', '.vhd', '.vhf', '.vhi', '.vho', '.vhs', '.vht', '.vhw',
                   '.vala', '.vapi', '.v', '.veo', '.vim', '.volt', '.vue', '.owl', '.webidl', '.x10', '.xc',
                   '.xsp-config', '.xsp.metadata', '.xpl', '.xproc', '.xquery', '.xq', '.xql', '.xqm', '.xqy', '.xs',
                   '.xslt', '.xsl', '.xojo_code', '.xojo_menu', '.xojo_report', '.xojo_script', '.xojo_toolbar',
                   '.xojo_window', '.xtend', '.yang', '.y', '.yacc', '.yy', '.zep', '.zimpl', '.zmpl', '.zpl', '.ec',
                   '.eh', '.edn', '.fish', '.mu', '.nc', '.ooc', '.wisp', '.prg', '.ch', '.prw'],
}
