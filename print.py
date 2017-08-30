# AUTHOR sylxjtu (sylxjtu@outlook.com)
import datetime
import os
import sys
import shutil
import printConf
import re
from collections import OrderedDict

# initialize languages
languages = {'.cpp': 'cpp', '.txt': 'text'}
codeFiles = OrderedDict({})

def _tex_escape(text):
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless ',
        '>': r'\textgreater ',
    }
    regex = re.compile('|'.join(re.escape(key) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

def generateHeader(setting):
    # Set document class
    ret = ""
    ret += "\\documentclass[%s]{%s}\n" % (setting.PAPER_SIZE, setting.DOCUMENT_CLASS)
    # Set packages
    for package in setting.PACKAGES:
        ret += "\\usepackage{%s}\n" % (package)
    # Set section break
    if setting.SECTION_BREAK:
        ret += r"\newcommand{\sectionbreak}{\clearpage}" + "\n"
        ret += r"\newcommand{\subsectionbreak}{\clearpage}" + "\n"
    # Set font
    ret += "\\setmonofont{%s}\n" % (setting.CODE_FONT)
    ret += "\\setCJKmainfont{%s}\n" % (setting.CJK_FONT)
    ret += "\\setCJKmonofont{%s}\n" % (setting.CJK_FONT)
    # Set minted language setting
    for language in setting.LANGUAGE_SETTINGS:
        lsetting = ','.join(
        ['='.join(ls) if isinstance(ls, tuple) else ls for ls in setting.LANGUAGE_SETTINGS[language]]
        )
        ret += "\\setminted[%s]{%s}\n" % (language, lsetting)
    # Set geomentry
    gsetting = ','.join(
    ['='.join(ls) if isinstance(ls, tuple) else ls for ls in setting.GEOMENTRY_SETTINGS]
    )
    ret += "\\geometry{%s}\n" % (gsetting)
    # Set title
    ret += "\\title{%s}\n" % (setting.TITLE)
    # Set date
    ret += "\\date{%s}\n" % (setting.DATE)
    # Set author
    ret += "\\author{%s}\n" % (setting.AUTHOR)
    # Document Begin
    ret += (
    r'\begin{document}' '\n'
    r'\maketitle'       '\n'
    r'\newpage'         '\n'
    r'\tableofcontents' '\n'
    r'\newpage'         '\n'
    )
    return ret

def generateSection(title):
    return "\\section{%s}\n" % _tex_escape(title)

def generateFile(directory, filename):
    fname, extname = os.path.splitext(filename) 
    ret = ""
    ret += "\\subsection{%s}\n" % _tex_escape(fname)
    ret += "\\begin{minted}{%s}\n" % languages[extname]
    try:
        f = open(os.path.join(directory, filename), encoding="utf-8-sig")
        ret += f.read().replace('\t', '  ')
    except UnicodeDecodeError:
        f.close()
        f = open(os.path.join(directory, filename))
        ret += f.read().replace('\t', '  ')
    f.close()
    ret += "\\end{minted}\n"
    return ret

footer = r"\end{document}" '\n'

#Change dir to script dir
os.chdir(sys.path[0])

#Mkdir dist
if os.path.exists("dist"):
    shutil.rmtree("dist")
os.makedirs("dist")
os.chdir("dist")

for root, dirs, files in os.walk('..', topdown=True):
    dirs[:] = [d for d in dirs if d[0] != '.']
    for f in files:
        extname = os.path.splitext(f)[1]
        if(extname not in languages): continue
        codeFiles.setdefault(root, []).append(f)

with open('out.tex', 'w', encoding="utf8") as fh:
    fh.write("%% Auto Generated on %s\n" % datetime.datetime.today().isoformat(' '))
    fh.write(generateHeader(printConf))
    for directory in codeFiles:
        directoryName = os.path.basename(directory)
        fh.write(generateSection(directoryName))
        for codeFile in codeFiles[directory]:
            fh.write(generateFile(directory, codeFile))
    fh.write(footer)

os.system("xelatex -shell-escape out.tex")
os.system("xelatex -shell-escape out.tex")
