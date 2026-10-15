from pathlib import Path
import sys,html,json
sys.path.insert(0,r'C:/Users/ilic/AppData/Local/uv/cache/archive-v0/n10Xfaj6sTF2htIT')
import pymupdf as fitz
R=Path(r'C:/Users/ilic/Downloads/Frankie-Handover');O=R/'output/assessment';O.mkdir(exist_ok=True,parents=True)
Q=R/'tmp/assessment-build/current-state';Q.mkdir(exist_ok=True,parents=True)
slides=[
dict(title='Frankie migration readiness',subtitle='Current state and required handover materials',kind='cover',items=[
'We have an initial description of the solution.',
'We still need the technical assets and access to verify that FS can run and maintain it.'],take='Purpose: establish what is available, what is missing and what each party must provide.',source='Document-based assessment | 8 October 2026 | Live systems, repositories and databases have not been verified.'),
dict(title='What is being handed over?',subtitle='The supplied documents describe the following components',headers=['Component','Purpose','Documented position'],rows=[
['Dashboard','Staff interface for events, tickets and conversations','FS handover; hosting already described as FS-managed AWS'],
['CRM / backend','Data and APIs supporting the Dashboard','Identified for transfer to FS'],
['BookStack','Knowledge content and its management','Also identified for migration in the platform status document'],
['Mindsmiths platform','Agents, routing and channel services','Remains licensed in the handover proposal']],take='Confirm the final component list. Dashboard / CRM is the working focus; BookStack must not be silently excluded.',source='Sources: Dashboard status; Platform status; Handover overview, pp. 2 and 5. These describe intended transfer, not completed delivery.'),
dict(title='What have we received?',subtitle='The package provides descriptions and requirements',headers=['Material','What it tells us','What it does not establish'],rows=[
['Component status documents','Stacks, hosting and build/deployment descriptions','Access to the actual code, data and configuration'],
['Product / technical documentation','Workflows, APIs and selected integrations','That all descriptions match current production'],
['Handover overview','Proposed ownership and transition','An agreed and completed asset transfer'],
['FS framework and supplier policies','Expected tools, controls and responsibilities','Implemented controls and operational readiness']],take='Documentation supports discovery. We need executable assets and observed evidence to complete the assessment.',source='Sources: Dashboard and Platform status; Technical documentation; Handover overview; FS framework; supplier policy set.'),
dict(title='Dashboard: current state and gaps',subtitle='Documented status must be checked against the running application',headers=['Documented current state','What we need to receive','What we will verify'],rows=[
['React / Redux application; Node / Yarn build','Repository, production commit/tag, lockfile and build instructions','A reproducible build from the delivered source'],
['Frontend uses the CRM API','Environment settings, API endpoints and authentication details','Login, permissions and key Dashboard-to-CRM flows'],
['FS AWS; staging and production on one server','Current resource inventory, hosting configuration and access owners','Whether hosting needs migration or only alignment'],
['Manual SSH / rsync deployment','Release/rollback procedure, artifacts and known issues','FS can deploy and recover a version']],take='Hosting at FS does not by itself establish control over the source, release process or backend dependencies.',source='Source: Frankie Dashboard IT handover status.docx. Requests and verification criteria are proposed assessment actions.'),
dict(title='CRM: current state and gaps',subtitle='Code, data and platform dependencies must be assessed together',headers=['Documented current state','What we need to receive','What we will verify'],rows=[
['Django / Python; Forge and adapter packages','Repository, production version, private package access and usage rights','Build and runtime feasibility in FS'],
['PostgreSQL and Redis','Read-only access or copies, schemas, volumes and storage inventory','Data relationships, transfer scope and actual Redis use'],
['Mindsmiths CI / Azure Container Registry','Build files, image version, deployment configuration and runtime processes','Repeatable deployment in FS staging'],
['Connections to licensed platform services','API contracts, network/authentication needs and support boundaries','Required integrations continue working from FS']],take='Receiving CRM source code alone does not prove that the service can operate in our environment.',source='Sources: Platform status; Technical documentation, pp. 172, 182-190 and 200-220. Current implementation remains unverified.'),
dict(title='What we need from the suppliers',subtitle='One agreed evidence package, with named owners and delivery dates',headers=['Delivery','Required content','Proposed provider'],rows=[
['Source and build','Repos, production versions, dependencies, build files and tests','Sawraft: Dashboard; Mindsmiths: CRM'],
['Data','Database copies/access, schemas, attachments and export/restore process','Mindsmiths; data owners to confirm'],
['Runtime and interfaces','Configuration, service inventory, integrations and license boundaries','Mindsmiths + Sawraft; contract owners'],
['Operations','Test accounts, walkthroughs, release/rollback, backup and support','Component owners + FS hosting owner']],take='For each delivery: identify the provider, FS recipient, agreed date and any item that cannot be supplied.',source='Basis: gaps in component status documents; FS framework; Questions for Mindsmiths. Requests have not been sent; ownership is proposed.'),
dict(title='What FS needs to prepare',subtitle='The target environment is the other half of migration readiness',headers=['FS responsibility','Required decision or input','Assessment outcome'],rows=[
['Infrastructure / DevOps','Hosting, database services, environments, networking and available capacity','A target design compatible with the actual system'],
['Development / integration owners','Repositories, CI/CD requirements and access to FS integrations','A repeatable delivery process and working connections'],
['Security / service operations','Service accounts, secrets, review criteria, monitoring and restore expectations','Agreed controls and operational acceptance'],
['Business / service owner','Required live workflows, support ownership and allowed service interruption','Clear acceptance criteria and transition responsibilities']],take='Confirm BookStack scope and retained Mindsmiths services before finalizing the target design.',source='Source: FS migration framework, sections 1-5. Named owners, capacity and implementation details remain to be confirmed.'),
dict(title='How we complete the assessment',subtitle='Each step produces evidence for the migration decision',headers=['Step','What we do','What we can conclude'],rows=[
['1. Receive and map','Link functions, repos, services, databases, integrations and owners','What transfers and what remains external'],
['2. Reproduce and test','Build applications, deploy in staging and exercise key workflows','What works and which changes are required'],
['3. Rehearse data transfer','Restore agreed data; reconcile records, relationships and attachments','Whether the proposed transfer is complete and repeatable'],
['4. Size and recommend','Define work packages, dependencies, acceptance and recovery criteria','Effort ranges, responsibilities and a supportable migration plan']],take='A reliable migration estimate follows these checks. No delivery date or headcount is established by the current documents.',source='Proposed assessment approach based on the FS framework. Execution and production migration are subsequent activities.'),
dict(title='Immediate next steps',subtitle='The requested outcome of this discussion',kind='list',items=[
('Confirm the handover boundary','Agree the component list, BookStack inclusion and services that remain with Mindsmiths.'),
('Assign evidence deliveries','Name supplier and FS contacts; agree dates for repositories, databases and runtime configuration.'),
('Provide the FS target requirements','Confirm infrastructure, access and operational expectations before technical validation.'),
('Schedule the technical assessment','Review the delivered assets with the suppliers, then return with findings and a migration estimate.')],take='Current position: enough information to organize the assessment; insufficient verified evidence to confirm migration readiness.',source='Assessment conclusion from the supplied package. Missing evidence does not mean the relevant asset or capability does not exist.'),
dict(title='Source register',subtitle='Local documents supporting this assessment',kind='sources',items=[
('Component status','Frankie Dashboard IT handover status.docx; Frankie platform IT handover status.docx. Both in the Migration into FS IT Ecosystem folder.'),
('Technical documentation','Frankie product and technical dosumentation 20261001.pdf. References in this deck use PDF page numbers.'),
('Handover and FS requirements','Frankie_Handover_Presentation_vF.pdf (June 2026); Framework for Migrating External Projects into FS IT Ecosystem_v1.0.docx (18 June 2025).'),
('Policies and outstanding questions','Frankie Platform ISO documentation folder; [FRANKIE]Questions for Mindsmiths team.docx. Questions are not supplier answers.')],take='Descriptions can reflect different dates. Production versions, current access and completed handover must be verified separately.',source='Prepared 8 October 2026. External linked resources were not accessed. No live code, database or infrastructure audit was performed.')
]
W,H=1280,720;navy=(.08,.15,.23);teal=(0,.36,.39);gray=(.36,.4,.44)
fonts={k:fitz.Font(fontfile='C:/Windows/Fonts/'+v) for k,v in {'R':'arial.ttf','B':'arialbd.ttf'}.items()}
def lines(s,w,size,font):
    out=[];line=''
    for word in s.split():
        t=(line+' '+word).strip()
        if fonts[font].text_length(t,fontsize=size)>w and line:out.append(line);line=word
        else:line=t
    return out+[line]
def tx(p,s,x,y,w,size=23,font='R',color=navy):
    for line in lines(s,w,size,font):p.insert_text((x,y+size),line,fontname=font,fontsize=size,color=color);y+=size*1.25
    return y
doc=fitz.open();htmlslides=[]
for i,s in enumerate(slides):
    p=doc.new_page(width=W,height=H)
    for k,v in {'R':'arial.ttf','B':'arialbd.ttf'}.items():p.insert_font(fontname=k,fontfile='C:/Windows/Fonts/'+v)
    tx(p,s['title'],64,44,1152,44 if i==0 else 34,'B')
    tx(p,s['subtitle'],64,108,1152,23,color=teal)
    body=''
    if 'rows' in s:
        widths=[320,435,397] if i in [3,4] else [290,467,395]
        xs=[64,64+widths[0],64+widths[0]+widths[1]];y=172
        for j,h in enumerate(s['headers']):tx(p,h,xs[j],y,widths[j]-25,21,'B',teal)
        y+=42
        for row in s['rows']:
            end=max(tx(p,v,xs[j],y,widths[j]-27,23,'B' if j==0 else 'R') for j,v in enumerate(row))
            y=end+23
        assert y<585,(i,y)
        body='<table><thead><tr>'+''.join('<th>'+html.escape(v)+'</th>' for v in s['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(v)+'</td>' for v in row)+'</tr>' for row in s['rows'])+'</tbody></table>'
    elif s['kind']=='cover':
        y=240
        for item in s['items']:y=tx(p,item,64,y,1070,32)+35
        body=''.join('<p class="opening">'+html.escape(v)+'</p>' for v in s['items'])
    else:
        y=172;size=21 if s['kind']=='sources' else 23
        for a,b in s['items']:
            y=tx(p,a,64,y,1152,size,'B',teal)+6
            y=tx(p,b,64,y,1152,size)+20
            body+='<h2>'+html.escape(a)+'</h2><p>'+html.escape(b)+'</p>'
        assert y<585,(i,y)
    tx(p,s['take'],64,589,1152,21,'B',teal)
    tx(p,s['source'],64,661,1105,12,color=gray)
    tx(p,f'{i+1:02}',1180,674,45,14,color=gray)
    htmlslides.append('<section aria-label="Slide '+str(i+1)+'"><h1>'+html.escape(s['title'])+'</h1><p class="subtitle">'+html.escape(s['subtitle'])+'</p>'+body+'<p class="take">'+html.escape(s['take'])+'</p><footer>'+html.escape(s['source'])+' | '+str(i+1)+' / '+str(len(slides))+'</footer></section>')
out=R/'output/pdf/Frankie-Migration-Current-State-and-Required-Inputs.pdf';doc.save(out)
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1,1)).save(Q/f'slide-{i+1}.png')
for start in range(0,len(doc),4):
    sh=fitz.open();pg=sh.new_page(width=1280,height=720)
    for j in range(min(4,len(doc)-start)):
        x=(j%2)*640;y=(j//2)*360;pg.show_pdf_page(fitz.Rect(x,y,x+640,y+360),doc,start+j)
    pg.get_pixmap().save(Q/f'sheet-{start//4+1}.png')
css='*{box-sizing:border-box}body{margin:0;background:#e9eef1;color:#142637;font:22px/1.3 Arial}section{background:#fff;max-width:1280px;min-height:720px;padding:44px 64px;margin:28px auto}h1{font-size:42px;margin:0 0 12px}.subtitle{font-size:25px;color:#005c64;margin:0 0 32px}h2{font-size:23px;color:#005c64;margin:20px 0 5px}p{margin:8px 0 20px}table{width:100%;border-collapse:collapse;table-layout:fixed}th,td{text-align:left;vertical-align:top;padding:10px 22px 16px 0}th{color:#005c64;font-size:21px}td:first-child{font-weight:bold}th:first-child{width:26%}.take{font-size:23px;color:#005c64;font-weight:bold;margin-top:30px}footer{font-size:13px;color:#5b6670}.opening{font-size:34px;margin:55px 0}nav{position:fixed;right:16px;bottom:12px;background:#142637;padding:8px;border-radius:6px;z-index:2}button{font:16px Arial;padding:8px;margin:0 4px;cursor:pointer}@media print{@page{size:landscape;margin:8mm}body{background:white}section{margin:0;break-after:page;min-height:0;font-size:17px}nav{display:none}}'
js='const slides=[...document.querySelectorAll("section")];let n=0;function go(d){n=Math.max(0,Math.min(slides.length-1,n+d));slides[n].scrollIntoView({behavior:"smooth",block:"start"});}document.addEventListener("keydown",e=>{if(["ArrowRight","PageDown"].includes(e.key)){e.preventDefault();go(1)}if(["ArrowLeft","PageUp"].includes(e.key)){e.preventDefault();go(-1)}});'
(O/'Frankie-Migration-Current-State-and-Required-Inputs.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Frankie migration readiness</title><style>'+css+'</style><body>'+''.join(htmlslides)+'<nav aria-label="Slide navigation"><button onclick="go(-1)">Previous</button><button onclick="go(1)">Next</button></nav><script>'+js+'</script></body></html>',encoding='utf8')
print('Created English presentation: '+str(len(slides))+' slides, PDF and HTML.')
