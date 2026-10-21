"""Genera los PDF desde Markdown y figuras desde CSV, sin modificar el juego.

Uso: python herramientas/generar_entregables.py
Dependencias: herramientas/requirements-documentos.txt.
IA: Codex implementó esta herramienta documental; validación por renderizado y extracción.
"""
from pathlib import Path
import csv
import html
import re
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from markdown_it import MarkdownIt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                               Image, PageBreak, Preformatted, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'entregables'
FIG = ROOT / 'docs/figuras'
INK = colors.HexColor('#16324f')
TEAL = colors.HexColor('#007e87')
GRAY = colors.HexColor('#536578')
WIDTH = A4[0] - 84
MD = MarkdownIt('commonmark').enable('table')
FONTDIR = Path(matplotlib.get_data_path()) / 'fonts/ttf'
for name, file in [('Text','DejaVuSans.ttf'), ('TextBold','DejaVuSans-Bold.ttf'),
                   ('TextItalic','DejaVuSans-Oblique.ttf'), ('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR/file)))
pdfmetrics.registerFontFamily('Text', normal='Text', bold='TextBold', italic='TextItalic', boldItalic='TextBold')
STYLES = {
    'body': ParagraphStyle('body', fontName='Text', fontSize=9.2, leading=13.8,
                           spaceAfter=7, textColor=INK, splitLongWords=True),
    'h1': ParagraphStyle('h1', fontName='TextBold', fontSize=24, leading=31,
                         textColor=INK, spaceAfter=20, keepWithNext=True),
    'h2': ParagraphStyle('h2', fontName='TextBold', fontSize=14, leading=19,
                         textColor=TEAL, spaceBefore=15, spaceAfter=9, keepWithNext=True),
    'h3': ParagraphStyle('h3', fontName='TextBold', fontSize=11, leading=15,
                         textColor=INK, spaceBefore=10, spaceAfter=6, keepWithNext=True),
    'cell': ParagraphStyle('cell', fontName='Text', fontSize=7.6, leading=10.6, textColor=INK),
    'headcell': ParagraphStyle('headcell', fontName='TextBold', fontSize=7.6, leading=10.6, textColor=colors.white),
    'caption': ParagraphStyle('caption', fontName='TextItalic', fontSize=8, leading=11,
                             textColor=GRAY, spaceAfter=12),
    'code': ParagraphStyle('code', fontName='Mono', fontSize=7.2, leading=10,
                          backColor=colors.HexColor('#eef3f7'), borderPadding=8,
                          spaceBefore=5, spaceAfter=12),
}


def figures():
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'axes.labelcolor':'#16324f','text.color':'#16324f'})
    with (ROOT/'resultados/E4_profundidad.csv').open() as f:
        rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(8.6,4.4),layout='constrained')
    for alg,color,label in [('MINIMAX','#16324f','Minimax'),('ALFA_BETA','#007e87','Alfa-beta')]:
        r=[x for x in rows if x['algoritmo']==alg]
        xs=[int(x['profundidad']) for x in r]; ys=[int(x['nodos_evaluados']) for x in r]
        ax.plot(xs,ys,'o-',label=label,color=color,lw=2)
        for x,y in zip(xs,ys):
            if not (alg=='MINIMAX' and x==1):
                ax.annotate(f'{y:,}'.replace(',',' '),(x,y),xytext=(0,7 if alg=='MINIMAX' else -16),textcoords='offset points',ha='center',fontsize=9)
    ax.set(yscale='log',xlabel='Profundidad (acciones individuales)',ylabel='Hojas evaluadas · escala logarítmica',xticks=[1,2,3,4,5],ylim=(5,65000))
    ax.grid(axis='y',alpha=.18); ax.legend(frameon=False); ax.set_title('Más horizonte requiere más exploración',loc='left',fontweight='bold',pad=14)
    fig.savefig(FIG/'profundidad.png',dpi=200); plt.close(fig)
    with (ROOT/'resultados/E5_orden.csv').open() as f:
        rows=[r for r in csv.DictReader(f) if r['profundidad']=='4']
    fig,ax=plt.subplots(figsize=(8.6,3.8),layout='constrained')
    left=[0]*len(rows)
    for key,label,color in [('nodos_evaluados','Hojas','#16324f'),('evaluaciones_ordenamiento','Ordenamiento','#007e87'),('evaluaciones_desglose','Desglose','#e6ab4c')]:
        val=[int(r[key]) for r in rows]; ax.barh([r['orden'] for r in rows],val,left=left,label=label,color=color,height=.5)
        left=[a+b for a,b in zip(left,val)]
    for i,v in enumerate(left): ax.text(v+100,i,str(v),va='center',fontsize=10)
    ax.invert_yaxis(); ax.set(xlabel='Evaluaciones totales',xlim=(0,12000)); ax.grid(axis='x',alpha=.15)
    ax.set_title('Orden heurístico: contar también el trabajo de ordenar',loc='left',fontweight='bold',pad=14)
    ax.legend(frameon=False,loc='lower right'); fig.savefig(FIG/'orden.png',dpi=200); plt.close(fig)


def normalize(text):
    return text.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u00a0',' ')


def inline(tokens, source):
    parts=[]
    for t in tokens or []:
        if t.type=='text': parts.append(html.escape(normalize(t.content)))
        elif t.type=='code_inline': parts.append('<font name="Mono" size="8">'+html.escape(normalize(t.content))+'</font>')
        elif t.type in ('softbreak','hardbreak'): parts.append('<br/>' if t.type=='hardbreak' else ' ')
        elif t.type=='strong_open': parts.append('<b>')
        elif t.type=='strong_close': parts.append('</b>')
        elif t.type=='em_open': parts.append('<i>')
        elif t.type=='em_close': parts.append('</i>')
        elif t.type=='link_open':
            href=t.attrGet('href')
            if not href.startswith(('http:', 'https:', 'mailto:','#')):
                target=(source.parent/href).resolve()
                try: href='https://github.com/danielqh1408/Proyecto1Inteligentes/blob/main/'+str(target.relative_to(ROOT))
                except ValueError: href=''
            parts.append('<a href="'+html.escape(href,quote=True)+'" color="#007e87">' if href else '<u>')
        elif t.type=='link_close': parts.append('</a>')
        elif t.type=='image': parts.append(html.escape(t.content))
    return ''.join(parts)


def make_pdf(source, filename, subtitle):
    tokens=MD.parse(source.read_text())
    title=tokens[1].content
    story=[Spacer(1,50),Paragraph('TACTICALGRID',STYLES['h2']),Paragraph(html.escape(title),STYLES['h1']),
           Paragraph(subtitle,STYLES['body']),Spacer(1,22),
           Paragraph('Proyecto 1 · Sistemas Inteligentes I<br/>Universidad de Caldas<br/>Ingeniería de Sistemas y Computación',STYLES['body']),
           Spacer(1,16),Paragraph('<b>Daniel Quintero Hurtado</b><br/><b>Juan David Ocampo González</b>',STYLES['body']),
           Paragraph('Docente: Jairo I. Vélez B.<br/>Edición: 21 de octubre de 2026',STYLES['body']),Spacer(1,30),
           Paragraph('Fuentes editables, escenarios y evidencia reproducible acompañan este PDF en el repositorio.',STYLES['caption']),PageBreak(),
           Paragraph('Contenido',STYLES['h2'])]
    for i,t in enumerate(tokens):
        if t.type=='heading_open' and t.tag=='h2':
            story.append(Paragraph(inline(tokens[i+1].children,source),STYLES['body']))
    story.append(PageBreak())
    # Saltar título y datos de portada del Markdown, hasta el primer capítulo.
    i=next(i for i,t in enumerate(tokens) if t.type=='heading_open' and t.tag=='h2')
    list_depth=0; bullet_pending=False
    while i<len(tokens):
        t=tokens[i]
        if t.type=='heading_open':
            style=STYLES.get(t.tag,STYLES['h3']); story.append(Paragraph(inline(tokens[i+1].children,source),style)); i+=3; continue
        if t.type in ('bullet_list_open','ordered_list_open'): list_depth+=1
        elif t.type in ('bullet_list_close','ordered_list_close'): list_depth-=1
        elif t.type=='list_item_open': bullet_pending=True
        elif t.type=='paragraph_open':
            it=tokens[i+1]
            images=[x for x in it.children or [] if x.type=='image']
            if images:
                for im in images:
                    path=(source.parent/im.attrGet('src')).resolve()
                    from PIL import Image as PILImage
                    with PILImage.open(path) as img: w,h=img.size
                    scale=min(WIDTH/w,330/h)
                    story.append(KeepTogether([Spacer(1,8),Image(str(path),width=w*scale,height=h*scale),Spacer(1,5),Paragraph(html.escape(im.content),STYLES['caption'])]))
            else:
                text=inline(it.children,source)
                style=STYLES['body']
                if list_depth:
                    style=ParagraphStyle('list',parent=style,leftIndent=12*list_depth,firstLineIndent=0)
                    if bullet_pending: text='• '+text; bullet_pending=False
                if len(it.children or []) == 3 and it.children[0].type == 'strong_open':
                    style=ParagraphStyle('label',parent=style,keepWithNext=True)
                story.append(Paragraph(text,style))
            i+=3; continue
        elif t.type=='fence':
            lines=[]
            for line in normalize(t.content).splitlines():
                lines+=textwrap.wrap(line,width=104,replace_whitespace=False,drop_whitespace=False) or ['']
            block = Preformatted('\n'.join(lines),STYLES['code'])
            story.append(KeepTogether([block]) if len(lines) <= 40 else block)
        elif t.type=='table_open':
            rows=[]; row=[]; header=True; i+=1
            while tokens[i].type!='table_close':
                tt=tokens[i]
                if tt.type=='tbody_open': header=False
                if tt.type=='tr_open': row=[]
                if tt.type=='inline': row.append(Paragraph(inline(tt.children,source),STYLES['headcell' if header else 'cell']))
                if tt.type=='tr_close': rows.append(row)
                i+=1
            n=len(rows[0]); widths=[WIDTH/n]*n
            if n==2: widths=[WIDTH*.32,WIDTH*.68]
            if n==3: widths=[WIDTH*.27,WIDTH*.24,WIDTH*.49]
            table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f5f8'),colors.white]),
                ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('LINEBELOW',(0,0),(-1,0),.6,TEAL)]))
            story.extend([KeepTogether([table]) if len(rows) <= 7 else table,Spacer(1,10)])
        i+=1
    def page(canvas,doc):
        canvas.saveState()
        if doc.page>1:
            canvas.setStrokeColor(TEAL); canvas.setLineWidth(.5); canvas.line(42,A4[1]-32,A4[0]-42,A4[1]-32)
            canvas.setFont('Text',7.2); canvas.setFillColor(GRAY)
            canvas.drawString(42,A4[1]-25,'TacticalGrid · '+title)
        canvas.setFont('Text',7); canvas.setFillColor(GRAY)
        canvas.drawString(42,24,'Sistemas Inteligentes I · 21 octubre 2026')
        canvas.drawRightString(A4[0]-42,24,str(doc.page)); canvas.restoreState()
    doc=SimpleDocTemplate(str(OUT/filename),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=47,bottomMargin=44,
        title=title,author='Daniel Quintero Hurtado; Juan David Ocampo González',subject=subtitle)
    doc.build(story,onFirstPage=page,onLaterPages=page)
    print(filename)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    figures()
    for source,name,subtitle in [
        ('MANUAL_USUARIO.md','Manual_usuario_TacticalGrid.pdf','Instalación, controles, verificación y recorrido de los diez casos.'),
        ('DOCUMENTO_TECNICO.md','Documento_tecnico_TacticalGrid.pdf','Modelado, algoritmos, evaluación adversarial, experimentación y trazabilidad.')]:
        make_pdf(ROOT/'docs'/source,name,subtitle)
