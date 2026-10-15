from pathlib import Path
import re, html, csv, json, sys
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT
from pypdf import PdfReader
from reportlab.graphics.shapes import Drawing, Rect, String, Line

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'outputs/frankie-project-assessment'
OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
TEXT=(SRC/'Frankie-project-assessment.md').read_text(encoding='utf-8')
REVISED={r['topic']:r for r in csv.DictReader((SRC/'use-case-ranking-after-first-review.csv').open(encoding='utf-8-sig'))}
REVIEW=json.loads((SRC/'unclear-topic-review-summary.json').read_text(encoding='utf-8'))
FILTERED='--exclude-opening-week-dates' in sys.argv
EXTENDED='--include-next-week' in sys.argv
FILTERED=FILTERED or EXTENDED
if FILTERED:
    stem='topics-without-opening-and-next-week' if EXTENDED else 'topics-without-opening-week-dates'
    REVISED={r['topic']:r for r in csv.DictReader((SRC/(stem+'.csv')).open(encoding='utf-8-sig'))}
    FILTER_SUMMARY=json.loads((SRC/(stem+'-summary.json')).read_text(encoding='utf-8'))
for name,file in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold')
NAVY=colors.HexColor('#242424'); TEAL=colors.HexColor('#606060'); MUTED=colors.HexColor('#707070')
W=499
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=9.4,leading=13,textColor=NAVY),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.3,leading=11.5,textColor=NAVY),
 'head':ParagraphStyle('head',fontName='Bold',fontSize=8.2,leading=11,textColor=NAVY),
 'title':ParagraphStyle('title',fontName='Bold',fontSize=26,leading=31,textColor=NAVY,spaceAfter=15),
 'sub':ParagraphStyle('sub',fontName='Bold',fontSize=13,leading=17,textColor=TEAL,spaceAfter=12),
 'eyebrow':ParagraphStyle('eyebrow',fontName='Bold',fontSize=9,leading=13,textColor=TEAL,spaceAfter=10),
}
def p(s,style='body'):
    s=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',s)
    s=s.replace('—','-').replace('–','-').replace('→','to')
    s=html.escape(s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    return Paragraph(s,styles[style])
def extract(start):
    lines=TEXT.splitlines(); i=next(i for i,v in enumerate(lines) if v.startswith(start)); result=[]
    for v in lines[i:]:
        if not v.startswith('|'): break
        cells=[x.strip() for x in v.strip('|').split('|')]
        if all(re.fullmatch(r'[-: ]+',x) for x in cells):continue
        result.append(cells)
    return result
def table(rows,widths,small=False):
    data=[[p(v,'head' if i==0 else ('small' if small else 'body')) for v in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8E8E8')),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F7F7')]),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#BDBDBD')),
        ('LINEBELOW',(0,-1),(-1,-1),.6,colors.HexColor('#D9D9D9'))]))
    return t
story=[]
def title(n,label,heading):
    story.extend([p(f'FRANKIE / {n:02d} / {label.upper()}','eyebrow'),p(heading,'title')])
def add(rows,widths,small=False):story.extend([table(rows,widths,small),Spacer(1,16)])
def page():story.append(PageBreak())

title(1,'Overview','Frankie usage report')
story.extend([p('16 April 2025 - 13 October 2026','sub'),Spacer(1,8)])
add([[('Full-history messages and users' if FILTERED else 'Messages and users'),'Total','Included in the count'],
 ['Messages sent by users','**93,987**','Questions, follow-ups and other replies'],
 ['Messages sent by Frankie','**332,665**','168,409 regular + 164,256 automatic/template messages'],
 ['Users who sent messages','**3,838**','Exported identifiers; student status is not verified'],
 ['Users with no sent messages','335','Present in the export, with no inbound messages'],
 ['Unknown sender','429','Records excluded from both message totals']],[180,75,244])
story.extend([Spacer(1,10),p('Most-used topics outside excluded dates' if FILTERED else 'What users asked for most','sub')])
chart=Drawing(W,214)
labels=['Lunch / canteen','Events / clubs','Registration / tickets','Classes / timetables','Opening Week']
values=[int(REVISED[t]['grouped_requests']) for t in ['Food / lunch / canteen','Events / clubs / networking','Registration / tickets / attendance','Timetables / classes / courses','Opening Week / onboarding']]
if FILTERED:
    top=[r for t,r in REVISED.items() if t!='Other / context-dependent text'][:5]
    short_labels={'Food / lunch / canteen':'Lunch / canteen','Events / clubs / networking':'Events / clubs','Registration / tickets / attendance':'Registration / tickets','Timetables / classes / courses':'Classes / timetables','Exams / grades / assignments':'Exams / grades','Opening Week / onboarding':'Opening Week'}
    labels=[short_labels.get(r['topic'],r['topic']) for r in top]
    values=[int(r['grouped_requests']) for r in top]
left=139; scale=310/10000
for tick in [0,2000,4000,6000,8000,10000]:
    x=left+tick*scale
    chart.add(Line(x,30,x,203,strokeColor=colors.HexColor('#E0E0E0'),strokeWidth=.5))
    chart.add(String(x,15,f'{tick:,}',fontName='Body',fontSize=8,textAnchor='middle',fillColor=MUTED))
for i,(label,value) in enumerate(zip(labels,values)):
    y=178-i*34
    chart.add(String(left-12,y+6,label,fontName='Body',fontSize=10,textAnchor='end',fillColor=NAVY))
    chart.add(Rect(left,y,value*scale,22,fillColor=colors.HexColor('#4472C4'),strokeColor=None))
    chart.add(String(left+value*scale+7,y+6,f'{value:,}',fontName='Bold',fontSize=9,fillColor=NAVY))
story.extend([chart,Spacer(1,12)])
if FILTERED:
    dates_text='2025: 25-29 August and 1-7 September. 2026: 24-28 August and 31 August-6 September. All dates inclusive; intervening weekends retained.' if EXTENDED else '25-29 August 2025 and 24-28 August 2026, inclusive. All user messages on these dates removed from the topic analysis.'
    add([['Excluded dates',dates_text],['Scope','Only the topic chart and topic rankings use filtered data. Overview totals, event-sending history and all other sections retain the full history.']],[110,389],True)
else:
    add([['Chart measure','Related messages grouped into help requests (estimate). Includes the first targeted review: 180 previously unclear groups reassigned.'],['Scope','All exported messages were processed. Topic and response categories remain estimates, not verified complete-answer or accuracy rates.']],[110,389],True)

ranking=extract('| What users asked about |')
for row in ranking[1:-1]:
    key='Other / context-dependent text' if row[0]=='Topic unclear without conversation context' else row[0]
    revised=REVISED[key]
    row[1:4]=[f"{int(revised[k]):,}" for k in ['grouped_requests','distinct_users','user_messages']]
    if key=='Other / context-dependent text':
        row[0]='Topic still unclear / not yet reviewed'
        row[4]='Context-dependent questions and other wording still awaiting classification.'
if FILTERED:
    ranking=[ranking[0]]+[[('Topic still unclear / not yet reviewed' if t=='Other / context-dependent text' else t),f"{int(r['grouped_requests']):,}",f"{int(r['distinct_users']):,}",f"{int(r['user_messages']):,}",('Context-dependent questions and other wording still awaiting classification.' if t=='Other / context-dependent text' else r['example'])] for t,r in REVISED.items()]+[ranking[-1]]
headers=['What users asked about','Help requests*','Users','User messages','Actual user message']
page();title(2,'Filtered use cases' if FILTERED else 'Use cases','Most-used topics and examples')
add([headers]+ranking[1:11],[120,58,45,64,212],True)
add([['How to read this table','Meaning'],['Help requests*','Related messages counted together automatically (estimate). One need can be split, or several combined.'],['Users / user messages','Each user counts once per topic. Message counts include questions, follow-ups and thanks inside the grouped requests.']],[120,379],True)
review_table=[['First targeted review','Groups reassigned','First targeted review','Groups reassigned'],
 ['Lunch / canteen','103','Opening Week','24'],
 ['Language / assistant capabilities','26','Events','12'],
 ['Student documents / administration','12','Campus / careers','2 / 1'],
 ['Total moved out of unclear','180','User messages in those groups','263'],
 ['Remaining unclear / unreviewed','12,033','Previously unclear','12,213']]
if FILTERED:
    review_table=[['Filtered topic counts','Total','Filtered topic counts','Total'],
     ['User messages removed',f"{FILTER_SUMMARY['raw_user_messages_removed']:,}",'User messages retained',f"{FILTER_SUMMARY['raw_user_messages_retained']:,}"],
     ['Groups retained',f"{FILTER_SUMMARY['groups_retained']:,}",'Groups fully removed',f"{FILTER_SUMMARY['groups_removed']:,}"],
     ['Filtering rule','Local dates','Time zone','Europe/Budapest']]
rt=table(review_table,[160,85,169,85],True)
rt.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
story.append(rt)
if FILTERED:
    story.extend([Spacer(1,6),p(f"Original groups and corrected labels retained; {len(FILTER_SUMMARY['boundary_groups'])} groups cross a date boundary. Only outside-date user messages count, including examples. Opening Week questions on other dates remain included. Topic tables cover {FILTER_SUMMARY['grouped_user_messages_retained']:,} of the {FILTER_SUMMARY['raw_user_messages_retained']:,} retained user messages.",'small')])
page();title(3,'Topics and events','Other topics and event messages')
add([headers]+ranking[11:-1],[120,58,45,64,212],True)
story.append(p('Event sending: full history' if FILTERED else 'When did event messages start?', 'sub'))
events=extract('| Milestone |')
# Keep the same evidence and milestones in a compact table.
events[-2]=['Messages counted','Automatic event templates','Includes invitations, confirmations, reminders, digests, cancellations and Opening Week logistics.']
events[-1]=['First observed','Export starts 16 April 2025','Earlier sending is unknown; this is not a verified launch date.']
event_table=table(events,[105,128,266],True)
event_table.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(event_table)


page();title(4,'Usage over time','When did usage rise and fall?')
story.extend([Image(str(SRC/'frankie-usage-over-time.png'),width=W,height=W*8/14),Spacer(1,15)])
trend=extract('| What stands out |')
add(trend[:6],[150,115,234],True)
add([['Coverage','First and last weeks are incomplete and excluded from peak/change comparisons. Counts include only user-sent messages.']],[120,379],True)

page();title(5,'Regular use','Do users keep coming back?')
add([['Return at any later week','What it means'],['**2,978 of 3,817 users (78.02%)**','Sent a message in a later fully observed week. Gaps are allowed; users have at least two full weeks since their first recorded message.']],[190,309])
r=extract('| Week after each user')
compact=[['Since first message','Users included','Used that week (gaps allowed)','Used EVERY week (no gaps)']]
for v in r[1:7]:compact.append([v[0],v[1],f'{v[2]} ({v[3]})',f'{v[4]} ({v[5]})'])
add(compact,[120,85,147,147])
add([['Counting rule','Meaning'],['Users included','Only users whose full period fits before the export ends. For four weeks, at least four full weeks must have passed since the first recorded message.'],['Use and weeks','At least one user message per seven-day period, starting at the first recorded message. Notifications alone do not count.'],['Limits','Earlier use is unknown. Rows overlap; a missed week does not prove permanent abandonment.']],[120,379])


page();title(6,'Responses','Does Frankie provide an answer?')
a=extract('| What was detected')
a[0]=['Detected message content','Messages','Share*','How to interpret it']
add(a,[156,61,52,230],True)
add([['*Share of regular messages','Automatic wording rules classify every regular outgoing message once. Percentages exclude templates. One message is not one request; several messages may answer one need.']],[156,343],True)

page();title(7,'Sources and limitations','Where does the information come from?')
s=extract('| User need |');s[0]=['User need','Source path','Observed response','Observed limitation']
add(s,[79,132,132,156],True)
add([['Evidence','Consolidated conversation export and Frankie technical documentation (1 October 2026). Examples show observed responses, not overall accuracy or satisfaction.']],[79,420],True)


class NumberedCanvas(canvas.Canvas):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.saved=[]
    def showPage(self):self.saved.append(dict(self.__dict__));self._startPage()
    def save(self):
        for state in self.saved:
            self.__dict__.update(state)
            self.setStrokeColor(colors.HexColor('#BDBDBD'));self.setLineWidth(.5);self.line(48,802,547,802)
            self.setFillColor(MUTED);self.setFont('Body',8)
            self.drawString(48,27,'Frankie | Topic date exclusion | 15 October 2026' if FILTERED else 'Frankie | Usage and value assessment | 14 October 2026')
            self.drawRightString(547,27,f'{self._pageNumber} / {len(self.saved)}')
            super().showPage()
        super().save()

target=OUT/('Frankie-usage-excluding-opening-week-dates.pdf' if FILTERED else 'Frankie-usage-and-value-assessment.pdf')
if EXTENDED:target=OUT/'Frankie-usage-excluding-opening-and-next-week.pdf'
doc=SimpleDocTemplate(str(target),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=58,bottomMargin=48,title='Frankie - Usage and value assessment',author='Frankie project assessment')
doc.build(story,canvasmaker=NumberedCanvas)
reader=PdfReader(target)
print('Pages:',len(reader.pages))
for i,page in enumerate(reader.pages,1):print(i,len(page.extract_text()),page.extract_text()[:65].replace('\n',' '))
assert len(reader.pages)==7, 'Unexpected page overflow'
assert all(v in '\n'.join(p.extract_text() for p in reader.pages) for v in ['93,987','13,000','66,952',(f"{int(REVISED['Other / context-dependent text']['grouped_requests']):,}" if FILTERED else '12,213')])
