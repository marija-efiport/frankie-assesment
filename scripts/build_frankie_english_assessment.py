from pathlib import Path
from collections import Counter
import json,math,re,html
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader,PdfWriter

R=Path(__file__).resolve().parent.parent
T=R/'tmp/pdfs/frankie-english';T.mkdir(parents=True,exist_ok=True)
OUT=R/'output/pdf/Frankie-Usage-and-Answer-Assessment.pdf'
read=lambda p:json.loads((R/p).read_text(encoding='utf-8'))
D=read('outputs/frankie-numerical-review/verified-counts.json')
A=read('outputs/frankie-numerical-review/engagement-and-response.json')
O=read('outputs/frankie-numerical-review/reviewed-optouts.json')
I=read('tmp/message-analysis/user-intents.json')
source=R/'output/frankie-export-20261013T095511Z/messages.jsonl'
spec={
 'E1':('Daily menu',[144673,144672]),
 'E2':('Canvas navigation',[135915,135914,135913,135911]),
 'E3':('Retake schedule',[247835,247833,247832,247831,247829]),
 'E4':('Stop request',[424419,424418,424417,424416]),
 'E5':('Event booking',[176988,176981,176980]),
 'E6':('Context-dependent event question',[904,903,902,901,900]),
 'E7':('IT support with knowledge references',[25924,25923]),
 'E8':('Lunch opt-out',[133725]),
 'E9':('Event opt-out',[321665]),
 'E10':('Only reply when asked',[423867]),
 'E11':('Reduced frequency',[113449]),
}
want={n for _,ns in spec.values() for n in ns};raw={}
for n,l in enumerate(source.open(encoding='utf-8'),1):
 if n in want:
  r=json.loads(l);raw[n]=r|{'source_line':n}
assert set(raw)==want
evidence={k:{'title':title,'lines':ns,'messages':[raw[n] for n in ns]} for k,(title,ns) in spec.items()}
for name,file in [('Regular','arial.ttf'),('Bold','arialbd.ttf'),('Italic','ariali.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
W,H=595.276,841.89;M=38;CW=W-2*M
NAVY=HexColor('#102D45');INK=HexColor('#18354A');TEAL=HexColor('#078879');BLUE=HexColor('#3F74C3');GOLD=HexColor('#E4AD45');RED=HexColor('#C75C5C');PURPLE=HexColor('#8B71BB');GRAY=HexColor('#A6B4C3');MUTED=HexColor('#5C7081');PALE=HexColor('#F2F6F8');LINE=HexColor('#DCE5EB')
c=canvas.Canvas(str(T/'body.pdf'),pagesize=(W,H));c.setTitle('Frankie | Usage and Answer Assessment');c.setAuthor('Frankie export assessment');page=0
def num(n):return f'{n:,}'
def pct(n,d):return f'{100*n/d:.2f}%'
def text(s,x,y,size=10,font='Regular',color=INK):c.setFillColor(color);c.setFont(font,size);c.drawString(x,H-y-size,str(s))
def right(s,x,y,size=10,font='Regular',color=INK):c.setFillColor(color);c.setFont(font,size);c.drawRightString(x,H-y-size,str(s))
def para(s,x,y,w,size=10,color=INK):
 p=Paragraph(s,ParagraphStyle('p',fontName='Regular',fontSize=size,leading=size*1.35,textColor=color));_,h=p.wrap(w,H)
 assert y+h<798,(page,s[:70],y,h)
 p.drawOn(c,x,H-y-h);return y+h
def box(x,y,w,h,fill=PALE,r=8):c.setFillColor(fill);c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=0)
def line(y):c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,H-y,W-M,H-y)
def new(title,subtitle,section):
 global page
 if page:c.showPage()
 page+=1;c.setFillColor(TEAL);c.rect(0,H-7,W,7,fill=1,stroke=0)
 text('FRANKIE  /  USAGE & ANSWER ASSESSMENT',M,25,8,'Bold',TEAL);right(section,W-M,25,8,'Bold',MUTED)
 text(title,M,53,24,'Bold',NAVY);para(subtitle,M,90,CW,10,MUTED)
 line(807);text('Export: 16 Apr 2025 - 13 Oct 2026  |  Assessment: 13 Oct 2026',M,817,7.5,color=MUTED);right(f'{page} / 8',W-M,816,8,'Bold',MUTED)
def note(s,y=783):para(s,M,y,CW,7.5,MUTED)
def donut(cx,cy,r,values,colors,center,sub):
 total=sum(values);a=90
 for v,col in zip(values,colors):
  ext=-360*v/total;c.setFillColor(col);c.wedge(cx-r,H-cy-r,cx+r,H-cy+r,a,ext,fill=1,stroke=0)
  if v/total>.085:
   ang=math.radians(a+ext/2);c.setFillColor(NAVY if col in [GRAY,GOLD] else white);c.setFont('Bold',9);c.drawCentredString(cx+math.cos(ang)*r*.8,H-cy+math.sin(ang)*r*.8-3,f'{100*v/total:.1f}%')
  a+=ext
 c.setFillColor(white);c.circle(cx,H-cy,r*.57,fill=1,stroke=0);c.setFillColor(NAVY);c.setFont('Bold',19);c.drawCentredString(cx,H-cy+2,center);c.setFillColor(MUTED);c.setFont('Regular',8);c.drawCentredString(cx,H-cy-14,sub)
def legend(x,y,w,items,total,step=36):
 for label,n,col in items:
  box(x,y+3,8,8,col,2);text(label,x+16,y,9);right(f'{num(n)}  |  {pct(n,total)}',x+w,y+14,8,color=MUTED);y+=step
def callout(title,body,y,h=66,col=TEAL):
 box(M,y,CW,h);box(M,y,4,h,col,1);text(title,M+14,y+10,11,'Bold',col);end=para(body,M+14,y+29,CW-28,9.5);assert end<y+h-5
def table(headers,rows,y,widths,rowh=24,size=9):
 box(M,y,CW,25,NAVY,3);x=M
 for h,w in zip(headers,widths):text(h,x+8,y+7,8,'Bold',white);x+=w
 y+=25
 for idx,row in enumerate(rows):
  if idx%2==0:box(M,y,CW,rowh,PALE,0)
  x=M
  for j,(v,w) in enumerate(zip(row,widths)):
   if j==0:text(v,x+8,y+5,size)
   else:right(v,x+w-9,y+5,size,'Bold' if j==len(row)-1 else 'Regular')
   x+=w
  y+=rowh
 return y
def link_example(k,x,y):
 uid=evidence[k]['messages'][0]['conversation_user_id'];url='https://frankie.frankfurt-school.de/dashboard/conversation/'+uid
 text(k+'  |  Open conversation',x,y,8,'Bold',BLUE);c.linkURL(url,(x,H-y-13,x+145,H-y),relative=0,thickness=0)
def card(x,y,w,h,k,title,body,verdict,col=TEAL):
 box(x,y,w,h);box(x,y,w,4,col,0);text(title,x+12,y+14,11,'Bold',col)
 end=para(body,x+12,y+38,w-24,9.5);end=para('<b>Assessment:</b> '+verdict,x+12,end+10,w-24,9.2)
 assert end<y+h-30,(title,end,y+h)
 link_example(k,x+12,y+h-22)

new('What Frankie is used for','A full-export assessment, with real examples and explicit percentage bases.','01 / OVERVIEW')
for x,v,label in [(M,'427,081','message records'),(M+178,'93,987','user messages'),(M+356,'3,838','users who sent a message')]:
 box(x,126,163,76);text(v,x+12,139,25,'Bold',NAVY);text(label,x+12,177,8.5,color=MUTED)
donut(149,316,88,[93987,168409,164256,429],[TEAL,BLUE,GRAY,GOLD],'427,081','all records')
legend(285,241,270,[('Incoming user messages',93987,TEAL),('Outbound replies',168409,BLUE),('Template messages',164256,GRAY),('Staff / UCS messages',429,GOLD)],427081,step=39)
callout('Events dominate outgoing templates', '127,810 event and Opening Week templates = <b>77.81%</b> of 164,256 templates. Invitations account for 97,975 records.',429)
callout('Main identifiable questions: food, events and registration','Lunch: <b>15.81%</b>; events: <b>14.30%</b>; registration: <b>5.97%</b> of 58,449 classified requests. Context-dependent messages remain a large classification gap.',507,73,BLUE)
callout('Frequent replies; correctness still needs validation','<b>98.97%</b> of classified request turns have a subsequent outgoing record within 30 minutes. This measures response coverage, not successful or correct answers.',592,73,BLUE)
callout('Repeat use across the entire exported history','<b>3,059 users (79.70%)</b> wrote in at least two different weeks; <b>83 (2.16%)</b> wrote in 27 or more weeks. Percentages use all 3,838 users who ever wrote.',678,73,GOLD)
note('Sources: S1-S4. Users = distinct conversation user IDs; total histories: 4,173. Definitions and source index: page 8.')

new('Questions and event use cases','Request topic percentages use 58,449 classified incoming requests as the denominator.','02 / DEMAND')
topics=[('Other / context-dependent',23859),('Lunch / food',9239),('Events / clubs / networking',8357),('Registration / tickets',3492),('Timetables / classes',3067),('Opening Week / onboarding',2546),('Exams / grades',2069),('Campus / facilities',1765),('IT / Canvas / accounts',1315),('Other classified topics',2740)]
assert sum(v for _,v in topics)==58449
table(['Question / request topic','Records','Share'],[(k,num(v),pct(v,58449)) for k,v in topics],127,[337,95,CW-432],22)
box(M,389,CW,93)
para('<b>"Other" does not mean an unclear question.</b><br/>E6: after an invitation to Co-Founder Wanted 9.0, the student asks <b>"What is it about"</b>. Frankie replies: <i>"It\'s a two-day startup event for aspiring founders..."</i><br/>The question is clear in context; standalone text rules miss the event reference.',M+12,400,CW-24,9.5)
link_example('E6',M+12,461)
text('Most common event function: invitations',M,501,13,'Bold',NAVY)
table(['Event-related template type','Records','% of all templates'],[
 ('Invitations',num(97975),pct(97975,164256)),('Event digests',num(20135),pct(20135,164256)),('Opening Week logistics',num(5088),pct(5088,164256)),('Confirmations / reminders / cancellations',num(4612),pct(4612,164256)),('All event-related templates',num(127810),pct(127810,164256))],527,[311,82,CW-393],23,8.8)
para('<b>Top named campaign:</b> Real Estate Career Day, 4,265 messages (4.80% of 88,866 named invitations in two template families). These are sending volumes, not attendance or ticket conversion.',M,680,CW,9.5)
note('Sources: S1, S3, S4. Automated topic estimates retain the original narrow 89-message opt-out label; page 6 expands that review.')

new('Where answers come from','BookStack is part of the knowledge setup; the dashboard also exposes separate operational data.','03 / SOURCES')
box(M,128,CW,82)
para('<b>Verified in the live FS dashboard:</b> Knowledge Base contains Programs, Modules, FS Staff and <b>Bookstack</b>. The Bookstack link opens a separate BookStack service, which requires its own login.<br/><b>Documented knowledge path:</b> BookStack pages → BookStackManager sync → internal paragraph search (TextEmbedder) → Frankie answer.',M+12,139,CW-24,10)
text('Source markers on outbound reply records',M,231,13,'Bold',NAVY)
donut(143,360,90,[36782,2132,129495],[TEAL,BLUE,GRAY],'168,409','outbound records')
legend(267,284,288,[('Knowledge references present',36782,TEAL),('Event ID; no knowledge reference',2132,BLUE),('Neither source marker recorded',129495,GRAY)],168409,step=47)
para('<b>76.89% without markers does not mean 76.89% unsupported.</b> The export cannot prove the exact origin of these replies. References identify retrieved material, not necessarily which statement used it.',M,464,CW,9.5,MUTED)
box(M,515,CW,152)
text('E7 / A traceable knowledge answer',M+12,526,11,'Bold',TEAL)
para('<b>Student:</b> "When can I go to the it support?"<br/><b>Frankie:</b> "You can visit the IT Student Support Desk in the library. It\'s open Monday to Friday from 12:00 to 14:00 and 16:00 to 17:00."<br/><b>Recorded reference:</b> file 27, "27 - IT Support (all-programs)", plus paragraph IDs and retrieval scores. Other references were also attached.',M+12,550,CW-24,9.5)
link_example('E7',M+12,644)
para('<b>Other routes:</b> event invitations and booking workflows use CRM/event data; the documented CanteenManager collects menus from a canteen website; UCS carries staff messages. These routes are not interchangeable with BookStack content.',M,693,CW,9.5)
note('Sources: S1, S2, S5. Documentation: pp. 116-119, 121-124, 154-156. Live BookStack pages were not accessible beyond login.')

new('What a question receives','Separate response coverage, visible links and assessed answer quality.','04 / RESPONSES')
donut(143,226,85,[55223,1636,18,593],[TEAL,BLUE,GOLD,RED],'57,470','request turns')
legend(267,132,288,[('First reply: outbound',55223,TEAL),('First reply: template',1636,BLUE),('First reply: staff / UCS',18,GOLD),('No outgoing within 30 minutes',593,RED)],57470,step=39)
para('<b>98.97% receive a subsequent outgoing record within 30 minutes.</b> For all 89,410 user turns, including non-requests, the rate is 98.03%. Consecutive incoming messages within 30 minutes form one turn. Temporal matching can include unrelated notifications.',M,329,CW,9.5)
box(M,402,CW,63)
para('<b>Links:</b> 14,058 of 168,409 outbound records contain a visible URL: <b>8.35%</b>. Including structured payload URLs gives 14,502 records: <b>8.61%</b>.<br/>These are message-record rates, not the percentage of users who clicked or solved their task.',M+12,412,CW-24,9.5)
text('Answer-quality pilot: 40 reviewed cases',M,486,13,'Bold',NAVY)
donut(143,613,83,[12,18,7,3],[TEAL,BLUE,RED,GOLD],'40','reviewed cases')
legend(267,530,288,[('Direct substantive answer',12,TEAL),('Partial / navigation / referral',18,BLUE),('Unresolved / visible problem',7,RED),('Action status unverified',3,GOLD)],40,step=38)
para('<b>This is not an overall success rate.</b> The pilot takes four cases from each of ten groups and is not weighted to usage. A useful link can fully solve a navigation question; a direct answer can still contain an unverified fact.',M,720,CW,9.5,MUTED)
note('Sources: S1, S3, S4, S6. Coverage uses time-based matching; quality uses a small content review. Do not combine their percentages.')

new('Real messages: good and bad','Short excerpts; German messages are translated into English and marked as translations.','05 / EXAMPLES')
cw=(CW-15)/2
card(M,129,cw,230,'E2','A link solved the task',
 '<b>Student:</b> "Hi where can I find my schedule for my classes"<br/><b>Frankie:</b> "Your lecture schedule is in Canvas, under the Calendar icon on the left menu bar."<br/><b>Student:</b> "Yes it worked thank you!!!"',
 'User-confirmed navigation success. A Canvas link accompanies the guidance.')
card(M+cw+15,129,cw,230,'E3','A link did not give the date',
 '<b>Student:</b> asks for a business administration retake date.<br/><b>Frankie:</b> points to TimeEdit.<br/><b>Student:</b> "Can\'t you just give me the schedule?" <i>(translated)</i>',
 'The requested date or schedule is not supplied in the excerpt.',RED)
card(M,376,cw,230,'E4','Stop request enters wrong flow',
 '<b>Student:</b> "Stop texting me"<br/><b>Frankie:</b> "Hey there, I\'m Frankie" [onboarding template].<br/><b>Student:</b> "Or how about you just leave me alone" [emoji omitted].',
 'Visible intent-routing failure. The conversation does not prove whether subscription settings changed.',RED)
card(M+cw+15,376,cw,230,'E5','Booking works; formatting fails',
 '<b>Frankie:</b> "you\'ve successfully booked a seat" [confirmation excerpt].<br/><b>Confirmation field:</b> "Date &amp; Time: Foyer"<br/><b>Student:</b> "Now it worked." <i>(translated)</i>',
 'User reports success, but the date/time field visibly contains a location.',GOLD)
box(M,625,CW,118)
text('E1 / Direct practical information: daily menu',M+12,637,11,'Bold',TEAL)
para('<b>Student:</b> "What is the menu today"<br/><b>Frankie:</b> provides a dated menu with dishes and prices, including pumpkin cream soup.<br/><b>Assessment:</b> the requested content is delivered in chat; historical menu accuracy was not independently verified.',M+12,662,CW-24,9.5)
link_example('E1',M+12,720)
note('Source: S1. E1-E5 are illustrative cases, not a random sample. Exact source rows, conversation links and dates: page 8.')

new('Stop and unsubscribe requests','Full-export bilingual search, followed by review of message intent and nearby context.','06 / NOTIFICATIONS')
S=O['summary'];assert S['confirmed_messages']==166
for x,v,label in [(M,'166','verified stop / opt-out messages'),(M+178,'103','distinct requesting users'),(M+356,'24','users who asked more than once')]:
 box(x,127,163,72);text(v,x+12,136,26,'Bold',NAVY);para(label,x+12,173,141,8.3,MUTED)
donut(143,313,85,[83,76,6,1],[BLUE,TEAL,GOLD,GRAY],'166','verified messages')
assert S['scope_counts']=={'Lunch/menu':76,'General/unspecified messages':83,'Other specific content':1,'Events/workshops/ads':6}
legend(267,232,288,[('General / unspecified messages',83,BLUE),('Lunch / menu',76,TEAL),('Events / workshops / ads',6,GOLD),('Other specific content',1,GRAY)],166,step=38)
para('<b>0.18%</b> of all 93,987 incoming messages are verified opt-out requests. <b>2.68%</b> of 3,838 users who ever wrote made at least one. Scope uses wording and nearby context. General stop requests may include events; the six event-related cases do not measure all event dissatisfaction.',M,415,CW,9.5)
box(M,491,CW,155)
text('What users actually wrote',M+12,502,12,'Bold',NAVY)
para('<b>E8 / Lunch:</b> "stop lunch updates but keep other updates"<br/><br/><b>E9 / Events:</b> "i dont want you new event alerts anymore"<br/><br/><b>E10 / On demand only:</b> "Please do not send me anymore messages unless I ask you something"',M+12,530,CW-24,10)
callout('Count intent separately from whether the system complied','Of 338 screened candidates: 166 confirmed, 165 excluded, 5 ambiguous, 1 frequency-reduction request and 1 account-deletion request. E4 shows a wrong response; no overall unsubscribe-compliance rate is established.',662,85,GOLD)
note('Source: S1, S7. This broader review replaces the previous narrow 89-message count. Free-text search may still miss paraphrases.')

new('Repeat use across the whole history','16 April 2025 - 13 October 2026: 546 calendar days spanning 79 calendar weeks.','07 / REPEAT USE')
F=A['whole_history']
for x,v,label in [(M,'3,838','users who ever sent a message'),(M+178,str(round(F['average_dau_complete_dates'])),'average daily active users'),(M+356,str(round(F['average_wau_complete_weeks'])),'average weekly active users')]:
 box(x,128,163,73);text(v,x+12,138,26,'Bold',NAVY);para(label,x+12,175,141,8.2,MUTED)
wk=['1 week','2-4 weeks','5-12 weeks','13-26 weeks','27+ weeks'];cols=[GRAY,BLUE,TEAL,PURPLE,GOLD]
donut(143,320,87,[F['active_week_bins'][k] for k in wk],cols,'3,838','ever-active users')
legend(267,235,288,[('Active in '+k,F['active_week_bins'][k],col) for k,col in zip(wk,cols)],3838,step=36)
text('Total active days per user across the full history',M,438,12,'Bold',NAVY)
dy=['1 day','2-3 days','4-7 days','8-14 days','15-30 days','31-60 days','61+ days']
table(['Distinct active days','Users','% of 3,838'],[(k,num(F['active_day_bins'][k]),pct(F['active_day_bins'][k],3838)) for k in dy],465,[337,82,CW-419],23)
para('<b>Repeat use:</b> 3,173 users (82.67%) wrote on multiple days; 3,059 (79.70%) wrote in multiple weeks. The highest observed totals are 109 active days and 47 active weeks. No user wrote in every calendar week of the full export.',M,666,CW,9.5)
para('Weeks need not be consecutive. This is lifetime frequency, not a retention rate: users joined at different times. The 335 histories with no incoming messages are excluded from the chart.',M,729,CW,9,MUTED)
note('S1, S4. Active = incoming message; Frankfurt time. Rounded averages exclude partial boundary dates/weeks (544 days; 77 weeks).')

new('Evidence and reading the numbers','Every chart states its denominator. Examples link to the relevant dashboard conversation.','08 / TRACEABILITY')
c.bookmarkPage('sources')
para('<b>S1 / Complete export:</b> output/frankie-export-20261013T095511Z/messages.jsonl; 427,081 records, not the shortened conversation preview.<br/><b>S2 / Live dashboard:</b> <link href="https://frankie.frankfurt-school.de/dashboard/knowledge" color="#3F74C3">FS Dashboard - Knowledge Base</link>; Bookstack opens <link href="https://bookstack.bookstack-8.frankie.mindsmiths.io/" color="#3F74C3">the linked BookStack service</link>. Checked 13 Oct 2026.<br/><b>S3 / Verified counts and topics:</b> verified-counts.json and user-intents.json.<br/><b>S4 / Activity and response calculations:</b> engagement-and-response.json.<br/><b>S5 / Technical documentation:</b> "Frankie product and technical dosumentation 20261001.pdf", pp. 116-119, 121-124, 154-156.<br/><b>S6 / Quality pilot:</b> tmp/message-analysis/outcome-review.json.<br/><b>S7 / Opt-out audit:</b> reviewed-optouts.json; all screened cases retain decisions.',M,129,CW,9.2)
text('Example source index',M,331,12,'Bold',NAVY)
rows=[]
for k,(title,ns) in spec.items():
 date=raw[ns[0]]['timestamp'][:10];rows.append((k+'  '+title,date,', '.join(map(str,ns))))
table(['Example','Date (UTC)','Export row(s)'],rows,355,[218,82,CW-300],22,7.6)
y=641
para('<b>Interpretation:</b> request topics are automated estimates. Reply coverage is a 30-minute temporal association, not proof of relevance. Source references are retrieval metadata, not factual validation. The 40-case quality pilot is not representative enough for an overall good/bad percentage.',M,y,CW,9)
para('<b>Counting:</b> user IDs represent conversation histories, not verified unique people. Repeated requests remain separate records. All 824 repeated message IDs have differing timestamps and are retained; exact user + message ID + timestamp duplicate keys: 0. The export is not an atomic snapshot.',M,702,CW,8.7)
note('The PDF embeds an English evidence manifest, calculation summaries and audited source rows. No Excel file is required.',778)
c.save()
reader=PdfReader(T/'body.pdf');assert len(reader.pages)==8
writer=PdfWriter();writer.clone_document_from_reader(reader)
manifest={'source':str(source),'sha256':D['source_sha256'],'examples':evidence,'activity_and_response':A,'optout_summary':S,'source_files':{'S3_counts':str(R/'outputs/frankie-numerical-review/verified-counts.json'),'S3_topics':str(R/'tmp/message-analysis/user-intents.json'),'S4':str(R/'outputs/frankie-numerical-review/engagement-and-response.json'),'S5':str(R/'8. Frankie product and technical documentation/Frankie product and technical dosumentation 20261001.pdf'),'S6':str(R/'tmp/message-analysis/outcome-review.json'),'S7':str(R/'outputs/frankie-numerical-review/reviewed-optouts.json')},'note':'Raw source messages preserve their original language. All report prose is in English.'}
writer.add_attachment('Frankie-evidence-and-calculations.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8'))
writer.add_attachment('Frankie-optout-audit.json',json.dumps(O,ensure_ascii=False,indent=2).encode('utf-8'))
with OUT.open('wb') as f:writer.write(f)
check=PdfReader(OUT);alltext='\n'.join(p.extract_text() or '' for p in check.pages)
for s in ['427,081','98.97%','21.84%','76.89%','166','79.70%','What is it about','BookStack']:assert s in alltext,s
(T/'extracted-text.txt').write_text(alltext,encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':len(check.pages),'bytes':OUT.stat().st_size,'attachments':len(check.attachments)}))
