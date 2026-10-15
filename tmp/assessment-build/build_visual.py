from pathlib import Path
import sys,html,math
sys.path.insert(0,r'C:/Users/ilic/AppData/Local/uv/cache/archive-v0/n10Xfaj6sTF2htIT')
import pymupdf as f
R=Path(r'C:/Users/ilic/Downloads/Frankie-Handover'); O=R/'output/assessment';Q=R/'tmp/assessment-build/visual';Q.mkdir(parents=True,exist_ok=True)
W,H=1600,900
N='#132B40';T='#007F82';A='#C45A24';C='#F7F5EF';M='#526574';L='#C8D5D7';WHITE='#FFFFFF';PALE='#E4F0ED'
fonts={k:f.Font(fontfile='C:/Windows/Fonts/'+v) for k,v in {'R':'arial.ttf','B':'arialbd.ttf'}.items()}
doc=f.open();svgs=[];p=None;svg=[]
def rgb(c):return tuple(int(c[i:i+2],16)/255 for i in (1,3,5))
def rect(x,y,w,h,fill,stroke=None):
 p.draw_rect(f.Rect(x,y,x+w,y+h),color=rgb(stroke) if stroke else None,fill=rgb(fill),width=1)
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or "none"}"/>')
def line(x1,y1,x2,y2,c=L,width=2,arrow=False):
 p.draw_line(f.Point(x1,y1),f.Point(x2,y2),color=rgb(c),width=width)
 svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{width}"/>')
 if arrow:
  a=math.atan2(y2-y1,x2-x1)
  for delta in [-.48,.48]:line(x2,y2,x2-17*math.cos(a+delta),y2-17*math.sin(a+delta),c,width)
def txt(s,x,y,w,size=28,b=False,c=N,leading=1.27):
 font='B' if b else 'R';lines=[]
 for para in s.split('\n'):
  current=''
  for word in para.split():
   trial=(current+' '+word).strip()
   if fonts[font].text_length(trial,fontsize=size)>w and current:lines.append(current);current=word
   else:current=trial
  lines.append(current)
 for a in lines:
  p.insert_text((x,y+size),a,fontname=font,fontsize=size,color=rgb(c))
  svg.append(f'<text x="{x}" y="{y+size}" fill="{c}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{700 if b else 400}">{html.escape(a)}</text>')
  y+=size*leading
 assert y<890,(s[:30],y)
 return y
def new(num,title,subtitle,dark=False):
 global p,svg
 p=doc.new_page(width=W,height=H);svg=[]
 for k,v in {'R':'arial.ttf','B':'arialbd.ttf'}.items():p.insert_font(fontname=k,fontfile='C:/Windows/Fonts/'+v)
 rect(0,0,W,H,N if dark else C)
 txt('FRANKIE  /  MIGRATION ASSESSMENT',72,37,1300,18,True,c='#72D3C6' if dark else T)
 txt(f'{num:02} / 06',1405,37,125,18,c=WHITE if dark else M)
 txt(title,72,98,1456,52,True,c=WHITE if dark else N)
 txt(subtitle,72,173,1456,28,c='#BBD8DE' if dark else M)
def footer(source,dark=False):
 txt(source,72,847,1450,15,c='#BBD8DE' if dark else M)
 svgs.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" role="img" aria-label="Frankie migration assessment slide">'+''.join(svg)+'</svg>')
def take(s,dark=False):
 line(72,758,1528,758,'#416274' if dark else L)
 txt(s,72,783,1455,28,True,c='#72D3C6' if dark else T)

new(1,'What we have. What we still need.','Frankie migration assessment | Current state and required handover materials',True)
txt('We have a description\nof the solution.',72,286,840,61,True,c=WHITE)
txt('We still need the assets and access to prove\nthat FS can build, deploy and operate it.',72,480,920,34,c='#BBD8DE')
txt('THE ASSESSMENT MUST ESTABLISH',1070,293,460,19,True,c='#72D3C6')
for n,(a,b) in enumerate([('What transfers','Applications, data and responsibilities'),('What is missing','Code, databases, configuration and access'),('What work remains','Changes needed to run the systems at FS')]):
 y=350+n*116;txt(str(n+1).zfill(2),1070,y,65,28,True,c='#72D3C6');txt(a,1140,y,380,28,True,c=WHITE);txt(b,1140,y+41,380,23,c='#BBD8DE')
take('Current position: documentation received; technical handover and migration readiness not yet verified.',True)
footer('8 October 2026 | Document-based assessment. No live code, database or infrastructure audit has been performed.',True)

new(2,'The system we are taking over','The Dashboard and CRM rely on services beyond their own codebases')
# Explicitly requested system diagram: component nodes and directed calls.
nodes=[(72,318,430,210,'Dashboard','Staff interface','Events, conversations and tickets',T),(585,318,430,210,'CRM / backend','Data and APIs','Serves Dashboard requests',T),(1098,318,430,210,'Mindsmiths platform','Licensed services','Agents, routing and channels',N)]
for x,y,w,h,title,label,body,color in nodes:
 rect(x,y,w,h,WHITE,color);txt(label.upper(),x+25,y+22,w-50,18,True,c=color);txt(title,x+25,y+68,w-50,31,True,c=color);txt(body,x+25,y+123,w-50,25)
line(507,416,575,416,T,4,True);line(1020,416,1088,416,T,4,True)
txt('CRM API',505,363,80,16,True,c=T);txt('Platform\nservices',1017,350,81,16,True,c=T)
txt('WORKING HANDOVER FOCUS',72,272,943,19,True,c=T);txt('RETAINED UNDER LICENSE',1098,272,430,19,True,c=N)
txt('BookStack',72,586,280,30,True,c=A);txt('Knowledge content and management. Also identified for migration in the platform document; inclusion must be confirmed.',365,582,1150,28)
take('Transferring the Dashboard and CRM does not automatically create an independent system.')
footer('Sources: Dashboard status; Platform status; Frankie Handover overview, pp. 2 and 5. Arrows show documented service dependencies.')

new(3,'What the documentation tells us','A technical starting point that still needs verification against production')
xs=[72,490,1009]; widths=[418,519,519]
rect(72,270,1456,65,N)
for x,w,s in zip(xs,widths,['Area','Dashboard','CRM / backend']):txt(s,x+20,283,w-40,27,True,c=WHITE)
rows=[['Application','React / Redux frontend','Python / Django service'],['Data and connections','Uses the CRM API','PostgreSQL, Redis and platform adapters'],['Hosting and delivery','FS AWS; staging and production on one server','Mindsmiths CI; Azure Container Registry'],['Release process','Manual SSH / rsync deployment','Supplier-managed build process']]
y=335
for i,row in enumerate(rows):
 h=80 if i!=2 else 104
 if i%2==0:rect(72,y,1456,h,PALE)
 for j,s in enumerate(row):txt(s,xs[j]+20,y+17,widths[j]-40,27,j==0)
 y+=h
txt('Also received: product workflows, API descriptions, a handover proposal and FS migration requirements.',72,707,1456,24,c=M)
take('These are documented descriptions. Production code, data and configuration still need to be checked.')
footer('Sources: Dashboard and Platform status documents; Technical documentation; Handover overview; FS migration framework.')

new(4,'What we still cannot establish','Four questions the supplied documents cannot answer on their own')
blocks=[('01','Can we build it?','Need: repositories, production versions, build files and access to dependencies.'),('02','Can we move the data?','Need: schemas, database access or copies, attachment locations and export/restore procedures.'),('03','Will it work at FS?','Need: deployment configuration, integration contracts and connectivity to retained services.'),('04','Can we maintain it?','Need: release and recovery procedures, monitoring, known issues and support responsibilities.')]
for i,(n,a,b) in enumerate(blocks):
 x=72+(i%2)*758;y=284+(i//2)*218
 txt(n,x,y,100,44,True,c=A);txt(a,x+110,y+5,585,34,True);txt(b,x+110,y+70,565,29)
take('Without these checks, effort, timing and operational readiness remain uncertain.')
footer('Assessment implications of the gaps in Dashboard and Platform status and the FS migration framework. No failure is assumed.')

new(5,'What we need to receive','A concrete handover package from the suppliers, matched to an FS target')
cols=[(72,445,'SAWRAFT','Dashboard',[
'Repository, history and production version',
'Build instructions, dependencies and environment settings',
'CRM connection and authentication details',
'Deployment / rollback and technical walkthrough']),
(574,445,'MINDSMITHS','CRM and platform connections',[
'CRM source and required package access',
'Database access / copies, schemas and storage inventory',
'Build and deployment files; runtime configuration',
'Integration contracts, license boundaries and operations']),
(1076,452,'FS','Target environment',[
'Hosting, databases and network requirements',
'Repositories, deployment and access standards',
'Technical and service owners',
'Operational acceptance criteria'])]
for x,w,label,sub,items in cols:
 txt(label,x,273,w,28,True,c=T);txt(sub,x,317,w,24,c=M)
 y=379
 for item in items:
  txt('•',x,y,22,25,True,c=A);end=txt(item,x+27,y,w-27,27);y=end+22
 assert y<752,(label,y)
take('Agree a provider, an FS recipient, a delivery date and a verification method for every item.')
footer('Proposed requests based on supplied materials. BookStack package to be added if included. Named owners and dates are not yet agreed.')

new(6,'What the completed assessment delivers','Evidence for a migration decision and an estimate we can explain',True)
items=[('01','Map the system','Connect applications, repositories, databases, integrations and owners.'),('02','Validate feasibility','Build and deploy in FS staging. Test key workflows and trial data transfer.'),('03','Identify the work','Separate direct transfers from configuration changes, code changes and supplier support.'),('04','Plan and estimate','Define work packages, responsibilities, dependencies, effort ranges and acceptance criteria.')]
for i,(n,a,b) in enumerate(items):
 x=72+i*380
 txt(n,x,283,300,54,True,c='#72D3C6')
 if i<3:line(x+110,324,x+336,324,'#72D3C6',3,True)
 txt(a,x,386,335,32,True,c=WHITE);txt(b,x,485,330,28,c='#BBD8DE')
take('Next: confirm scope and obtain the repositories, databases and deployment materials.',True)
footer('Proposed assessment sequence | Effort ranges and migration dates follow technical verification and confirmed team availability.',True)

pdf=R/'output/pdf/Frankie-Migration-Assessment-Visual-6-Slides.pdf';doc.save(pdf)
for i,p in enumerate(doc):p.get_pixmap(matrix=f.Matrix(.8,.8)).save(Q/f'slide-{i+1}.png')
for start in range(0,6,2):
 sh=f.open();pg=sh.new_page(width=1600,height=1800)
 for j in range(2):pg.show_pdf_page(f.Rect(0,j*900,1600,(j+1)*900),doc,start+j)
 pg.get_pixmap(matrix=f.Matrix(.6,.6)).save(Q/f'sheet-{start//2+1}.png')
css='*{box-sizing:border-box}body{margin:0;background:#0b1b29;font-family:Arial}section{width:min(100vw,1600px);margin:24px auto;box-shadow:0 5px 28px #0005}svg{display:block;width:100%;height:auto}nav{position:fixed;bottom:15px;right:20px;display:flex;gap:8px;z-index:9}button{border:1px solid #88bfc0;background:#132b40;color:white;padding:10px 15px;font-size:16px;cursor:pointer}body.present section{display:none;margin:0;width:min(100vw,177.77vh)}body.present section.active{display:block}body.present{display:flex;align-items:center;justify-content:center;min-height:100vh}@media print{@page{size:landscape;margin:0}body{background:white}section,body.present section{display:block;margin:0;width:100%;box-shadow:none;break-after:page}nav{display:none}}'
js='const ss=[...document.querySelectorAll("section")];let n=0;function go(d){n=Math.max(0,Math.min(ss.length-1,n+d));ss.forEach((s,i)=>s.classList.toggle("active",i===n));if(!document.body.classList.contains("present"))ss[n].scrollIntoView({behavior:"smooth"});}function present(){document.body.classList.toggle("present");go(0)}document.addEventListener("keydown",e=>{if(["ArrowRight","PageDown"," "].includes(e.key)){e.preventDefault();go(1)}if(["ArrowLeft","PageUp"].includes(e.key)){e.preventDefault();go(-1)}if(e.key==="Escape")document.body.classList.remove("present")});go(0);'
(O/'Frankie-Migration-Assessment-Visual-6-Slides.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Frankie migration assessment</title><style>'+css+'</style><body>'+''.join('<section>'+s+'</section>' for s in svgs)+'<nav><button onclick="go(-1)" aria-label="Previous slide">Previous</button><button onclick="go(1)" aria-label="Next slide">Next</button><button onclick="present()">Present</button></nav><script>'+js+'</script></body></html>',encoding='utf8')
print('Created 6-slide PDF and vector HTML presentation.')
