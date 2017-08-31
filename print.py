# AUTHOR sylxjtu (sylxjtu@outlook.com)
import datetime
import os
import sys
import shutil
import printConf as setting
import re
from hashlib import md5
from collections import OrderedDict

def _tex_escape(text):
    """
    Escape raw text into tex text
    """
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

def generateHeader():
    """
    Generate tex file header
    """
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
    """
    Generate section (corresponding to a directory)
    """
    return "\\section{%s}\n" % _tex_escape(title)

def generateSubsection(title):
    """
    Generate subsection (corresponding to a file)
    """
    return "\\subsection{%s}\n" % _tex_escape(title)

def _safeReadfile(filepath):
    """
    Read file with correct encoding
    """
    ret = None
    for enc in setting.POSSIBLE_ENCODING:
        f = open(filepath, encoding = enc)
        try:
            ret = f.read()
            f.close()
            return ret
        except UnicodeDecodeError:
            f.close()
            pass
    raise UnicodeDecodeError('All possible encoding failed for {0}, please add its encoding in config'.format(filepath))

def mintedGenerator(mintedClass):
    def generateFile(directory, filename):
        fname, extname = os.path.splitext(filename)
        ret = ""
        ret += generateSubsection(fname)
        ret += "\\begin{minted}{%s}\n" % mintedClass
        ret += _safeReadfile(os.path.join(directory, filename)).replace('\t', ' ' * setting.TAB_SIZE)
        ret += "\\end{minted}\n"
        return ret
    return generateFile

def pdfGenerator(directory, filename):
    fname, extname = os.path.splitext(filename)
    md5filename = md5(os.path.join(directory, filename).encode('utf-8')).hexdigest() + '.pdf'
    shutil.copyfile(os.path.join(directory, filename), os.path.join('.', 'pdfs', md5filename))
    ret = ""
    ret += generateSubsection(fname)
    ret += "\\includepdf[pages=-]{%s}\n" % os.path.join('.', 'pdfs', md5filename).replace('\\', '/')
    return ret

footer = "\\end{document}\n"

# initialize languages
languages = {'.cpp': mintedGenerator('cpp'), '.txt': mintedGenerator('text'), '.pdf': pdfGenerator}
codeFiles = OrderedDict({})

# Change dir to script dir
os.chdir(sys.path[0])

# Mkdir dist
if os.path.exists("dist"):
    shutil.rmtree("dist")
os.makedirs("dist")
os.chdir("dist")
os.makedirs("pdfs")

for root, dirs, files in os.walk('..', topdown=True):
    dirs[:] = [d for d in dirs if d[0] != '.']
    for f in files:
        extname = os.path.splitext(f)[1]
        if(extname not in languages): continue
        codeFiles.setdefault(root, []).append(f)

with open('out.tex', 'w', encoding="utf8") as fh:
    fh.write("%% Automatically Generated at %s by codeprint (github.com/sylxjtu/codeprint)\n" % datetime.datetime.today().isoformat(' '))
    fh.write(generateHeader())
    for directory in codeFiles:
        directoryName = os.path.basename(directory)
        fh.write(generateSection(directoryName))
        for codeFile in codeFiles[directory]:
            extname = os.path.splitext(codeFile)[1]
            fh.write(languages[extname](directory, codeFile))
    fh.write(footer)

os.system("xelatex -shell-escape out.tex")
os.system("xelatex -shell-escape out.tex")
