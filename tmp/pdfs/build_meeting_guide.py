from pathlib import Path
import sys
sys.path.insert(0, r'C:/Users/ilic/AppData/Local/uv/cache/archive-v0/n10Xfaj6sTF2htIT')
import pymupdf as fitz

ROOT = Path(r'C:/Users/ilic/Downloads/Frankie-Handover')
OUT = ROOT / 'output/pdf/Frankie-Migration-Meeting-Guide.pdf'
QA = ROOT / 'tmp/pdfs/meeting-guide-qa'
OUT.parent.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
doc = fitz.open()
W, H = 595.276, 841.89
M = 44
CW = W - 2*M
NAVY = (0.10, 0.17, 0.25)
TEAL = (0.00, 0.39, 0.43)
TEXT = (0.17, 0.21, 0.26)
MUTED = (0.37, 0.43, 0.49)
LINE = (0.82, 0.86, 0.89)
PALE = (0.94, 0.97, 0.97)
WHITE = (1, 1, 1)
font_paths = {'R': 'arial.ttf', 'B': 'arialbd.ttf', 'I': 'ariali.ttf'}
fonts = {k: fitz.Font(fontfile='C:/Windows/Fonts/'+v) for k,v in font_paths.items()}

def wrap(text, width, size, font='R'):
    lines=[]
    for para in text.split('\n'):
        words=para.split()
        if not words:
            lines.append('')
            continue
        line=''
        for word in words:
            trial=(line+' '+word).strip()
            if fonts[font].text_length(trial, fontsize=size)>width and line:
                lines.append(line);line=word
            else: line=trial
        lines.append(line)
    return lines

def text(p, s, y, x=M, width=CW, size=10.3, font='R', color=TEXT, leading=None):
    leading=leading or size*1.38
    for line in wrap(s,width,size,font):
        p.insert_text((x,y+size),line,fontname=font,fontsize=size,color=color)
        y+=leading
    return y

def rule(p,y,x=M,width=CW):
    p.draw_line((x,y),(x+width,y),color=LINE,width=.7)

def newpage(section,title,subtitle=None):
    p=doc.new_page(width=W,height=H)
    for k,v in font_paths.items():p.insert_font(fontname=k,fontfile='C:/Windows/Fonts/'+v)
    p.draw_rect(fitz.Rect(0,0,W,7),color=None,fill=TEAL)
    text(p,'FRANKIE  /  TECHNICAL MIGRATION',26,size=8.5,font='B',color=TEAL)
    text(p,section.upper(),48,size=8.5,font='B',color=MUTED)
    y=text(p,title,68,size=24,font='B',color=NAVY,leading=29)
    if subtitle:y=text(p,subtitle,y+10,size=10.3,color=MUTED)
    return p,y+22

def label(p,s,y):
    return text(p,s.upper(),y,size=8.2,font='B',color=TEAL,leading=11)

def bullet(p,s,y,size=10.4):
    p.draw_circle((M+3,y+6),1.6,color=None,fill=TEAL)
    return text(p,s,y,x=M+13,width=CW-13,size=size)+6

def question(p,num,title,source,finding,ask,evidence,y,height):
    top=y
    p.draw_rect(fitz.Rect(M,y,M+29,y+25),color=None,fill=TEAL)
    text(p,f'{num:02}',y+5,x=M+6,width=24,size=10,font='B',color=WHITE)
    text(p,title,y+1,x=M+40,width=CW-40,size=13,font='B',color=NAVY)
    y+=34
    y=text(p,source,y,size=8.3,color=MUTED)+7
    y=label(p,'Documented finding',y)
    y=text(p,finding,y+2,size=10.1)+8
    y=label(p,'Ask in the meeting',y)
    y=text(p,ask,y+2,size=10.5,font='B')+8
    y=text(p,'Evidence to request: '+evidence,y,size=9.4,color=MUTED)
    bottom=top+height
    if y>bottom-19:raise RuntimeError(f'Question {num} overflows: {y} > {bottom-19}')
    rule(p,bottom-10)
    return bottom

# 1. Brief with a usable agenda rather than an empty cover.
p,y=newpage('Meeting brief','Frankie migration\nMeeting guide','Dashboard and CRM handover | Prepared 7 October 2026')
y=label(p,'Purpose',y)
y=text(p,'Establish what is required to run and maintain the existing Dashboard and CRM in our environment, with the Mindsmiths platform remaining in use.',y+4,size=12)+19
p.draw_rect(fitz.Rect(M,y,W-M,y+91),color=None,fill=PALE)
text(p,'Confirmed working scope',y+12,x=M+13,width=CW-26,size=11,font='B',color=NAVY)
text(p,'Migrate the existing Dashboard and CRM. Preserve current functionality and the required links to Mindsmiths. A replacement platform and new features are outside this discussion. BookStack migration is not assumed.',y+33,x=M+13,width=CW-26,size=10.3)
y+=111
y=label(p,'Open with this',y)
y=text(p,'"We would like to confirm the exact materials, access and configuration needed to migrate the Dashboard and CRM, validate their connection to your platform, and agree on support responsibilities."',y+4,size=11.2,font='I')+21
y=label(p,'Discussion order',y)
for s in [
    'Data and usage: message storage, the 50,000-message dump, linked users and existing quality records (page 2).',
    'Technical dependencies: MongoDB access, build tooling and the integration boundary (page 3).',
    'Current-version questions: documented defects, configuration and conflicting descriptions (page 4).',
    'Operational readiness: working features, deployment and knowledge retrieval (page 5).',
    'Deliverables, ownership, dates and acceptance of the migration (pages 6-7).']:
    y=bullet(p,s,y+4,size=10.2)
y+=10
y=label(p,'Evidence limits',y)
y=text(p,'The findings are based on supplied documentation, not a production inspection. Approximately 50,000 messages and 7% usage are stakeholder-reported figures; their period and calculation remain unverified. References such as T, D and P are defined on page 7.',y+4,size=9.3,color=MUTED)
assert y<779,y

# 2-5. Twelve focused talking points, three per page.
sections=[
('01 / Data and usage','Start with the actual data','Confirm what is stored, what can be delivered and how usage is measured.',[
('Conversation history and the database dump','T, pp. 196-200 | Conversations API',
 'GET /conversations retrieves message history, but the section does not identify its underlying database or fully describe ApiMessage.',
 'Where are the 50,000 messages physically stored? Are they part of the CRM database or retained on Mindsmiths? Can you provide the relevant database dump and explain how the migrated CRM will read them?',
 'Schema and restore instructions; period, counts, attachments and linked records. Protect personal data while retaining stable analysis IDs.'),
('User records and the reported 7% usage','T, pp. 86, 94-95, 133 and 206-220',
 'An active user is defined as someone who sent at least one message in a period. Profiles can exist before engagement, and student records are linked to profiles separately.',
 'How was 7% calculated? Which period and student population were used? Can we reproduce it from messages and the user list, including people with no messages?',
 'Calculation, exclusions, registration status, identity mapping and a consistent anonymized user key.'),
('Quality records and activity beyond messages','T, pp. 103-109, 123, 176-186, 225 and 230',
 'The documents describe event reactions, menu activity, conversation excerpts, issue tags and tickets. An excerpt is created after a configurable inactivity period.',
 'Which of these records are actually retained? Can we link them to the messages and users? How many conversations were reviewed, and what issues and resolutions were recorded?',
 'Reviews, tickets and outcomes; invitation and attendance records; available activity logs and retention rules.')]),
('02 / Platform dependencies','Confirm what must stay connected','Receiving the CRM source code does not establish that it can run independently.',[
('Direct access to the Mindsmiths database','T, pp. 188-190 | Human intervention',
 'The CRM reads the intervention status directly from MongoDB collection relationManagerDB.summary and sends commands through RelationManager.',
 'Is this direct database connection still used in production? How will our CRM access it after migration? Are there other direct reads or writes between the systems?',
 'Connection inventory, access permissions, network configuration, supported interface and change ownership.'),
('Build tooling and private dependencies','P, Custom CRM service / Build and Deployment',
 'The CRM uses Mindsmiths CI and Azure Container Registry. The package list includes Forge and other Mindsmiths dependencies.',
 'Which packages and images will we be able to access and use? Will you provide the build files and pipeline configuration, and demonstrate a build and deployment from our environment?',
 'Production commit, dependency lockfiles, build scripts, registry access, configuration template and usage rights.'),
('Missing integration boundary','T, p. 151; pp. 172, 182, 186 and 200-205',
 'The Integration Architecture section is an unfilled outline. Other sections show dependencies for event publishing, email and KPI calculations.',
 'Which Mindsmiths services must the migrated CRM reach? For each connection, what are the endpoint, authentication, network requirements, payload and failure behavior?',
 'Current API specification, examples, test endpoints and service contacts. Include workers, scheduled jobs and direct database access.')]),
('03 / Current-version checks','Resolve documented inconsistencies','Ask whether each issue still applies; do not assume it remains a production defect.',[
('Hardcoded ticket assignment','T, p. 135 | Roles and responsibilities',
 'The Knowledge Base Manager user ID is described as hardcoded. Changing the person would require an application update until this is resolved.',
 'Has the hardcoded assignment been removed? If not, what must change for our accounts? Are any other user IDs, URLs or environment values hardcoded?',
 'Fix status, production version and the configuration or code changes needed for migration.'),
('Possible defect in event reporting','T, p. 173 | Interim report',
 'The document explicitly notes that an Accepted invitation may increment invites_rejected_count.',
 'Was this defect confirmed and fixed? In which version? Were historical reports affected, and can you reconcile reported totals with the underlying invitation records?',
 'Issue and fix reference, test result and example reconciliation. This does not itself show that the 7% figure is wrong.'),
('Conflicting descriptions of the live system','T, pp. 11, 27, 94-95, 130 and 141-146',
 'Email is described as Gmail API and as AWS SES/SMTP. Verification uses a link in one section and a PIN in another. Infrastructure descriptions also differ.',
 'Which descriptions match the version we will receive? Do any of these flows coexist? Please identify current settings and mark obsolete sections.',
 'Dated production configuration and a corrected description. Confirm actual resource ownership and locations.')]),
('04 / Operational readiness','Define what we will support','Agree on demonstrated behavior and repeatable operating procedures.',[
('Working features versus unfinished scope','T, p. 14; pp. 30, 85, 133-134 and 269; H, p. 2',
 'Waiting lists and some analytics sections are marked unfinished, while other analytics are described as available. The mobile application is described as a prototype.',
 'Which features are currently operational, disabled or unfinished? Can we validate the migration against a checklist of the exact functions that work today?',
 'Live demonstration, test accounts, production feature list and acceptance checks. Do not assume prototype features are in scope.'),
('Dashboard deployment and recovery','D, Current project environment and tools',
 'The document describes SSH/rsync deployment, staging and production on the same server, and incomplete knowledge of the server details.',
 'Who can provide the actual server configuration and deployment procedure? How will we publish changes and restore the previous version or data if a release fails?',
 'Deployment scripts, environment settings, backup and restore procedure, tested rollback and monitoring access.'),
('Knowledge retrieval and answer quality','T, pp. 18, 27, 154-156, 230 and 272',
 'Quality assurances are not accompanied by evaluation results. The manual describes isolated paragraphs, and synchronization and access tags affect available knowledge.',
 'Can you trace an incorrect answer to the content used, its permissions and synchronization state? Does the paragraph-context limitation still apply, and how do you verify corrections?',
 'Reviewed examples, current retrieval settings and synchronization logs. A hallucination issue category is not proof of its frequency.')])
]
num=1
for sec,title,sub,qs in sections:
    p,y=newpage(sec,title,sub)
    for q in qs:
        y=question(p,num,*q,y=y,height=212)
        num+=1
    assert y<784,(sec,y)

# 6. Compact, actionable deliverables register.
p,y=newpage('05 / Requested materials','Migration delivery checklist','Ask for a responsible contact and a delivery date for each item. Mark unavailable items explicitly.')
rows=[
('A','Source code','Dashboard and CRM repositories, history, production commit/tag, tests and known issues.'),
('B','CRM data','CRM database dump, schema, table relationships, restore procedure and associated files.'),
('C','Message data','Dump containing approximately 50,000 messages, or the separate relevant database; complete history, linked records, dates and documented exclusions.'),
('D','Usage and quality','Linked users including inactive profiles; 7% calculation; reports, reviews, tickets and available activity records.'),
('E','Reproducible build','Setup guide, dependencies, private package access, container build files and registry permissions.'),
('F','Configuration and access','Environment-variable template, endpoints and securely provisioned service credentials; inventory of settings outside Git.'),
('G','Platform connectivity','API contracts, direct database connections, network rules, background processes and jobs. Confirm access and support rights.'),
('H','Test and validation','Test environment and accounts, protected test data, existing tests and agreed critical workflows.'),
('I','Operations and support','Deployment/rollback, backup/restore, logs and alerts, incidents, manual tasks and named support contacts.'),
('J','Cutover plan','Final data synchronization, addresses and integrations to change, write ownership, downtime, rollback and responsibilities.')
]
p.draw_rect(fitz.Rect(M,y,W-M,y+25),color=None,fill=NAVY)
text(p,'ID',y+7,x=M+9,width=25,size=8.5,font='B',color=WHITE)
text(p,'REQUESTED DELIVERABLE',y+7,x=M+44,width=CW-55,size=8.5,font='B',color=WHITE)
y+=25
for id_,title,body in rows:
    needed=24+len(wrap(body,CW-60,9.5))*12.5+7
    p.draw_rect(fitz.Rect(M+9,y+12,M+18,y+21),color=LINE,width=.8)
    text(p,id_,y+29,x=M+10,width=20,size=8,font='B',color=MUTED)
    text(p,title,y+7,x=M+44,width=CW-55,size=10.3,font='B',color=NAVY)
    text(p,body,y+24,x=M+44,width=CW-60,size=9.5,leading=12.5)
    y+=max(needed,58)
    rule(p,y)
assert y<769,y
text(p,'Data for usage analysis and data required to operate the migrated CRM may overlap, but must be scoped and checked separately.',y+12,size=9,color=MUTED)

# 7. Decisions and source key.
p,y=newpage('06 / Meeting close','Decisions and next actions','Complete with the supplier before closing the meeting.')
for s in [
    'Confirm the exact Dashboard/CRM transfer boundary, retained Mindsmiths dependencies and responsibility for each side.',
    'Agree on data access and dumps, production version, test environment and a technical walkthrough.',
    'Agree on a trial migration, acceptance checks, cutover support and ongoing incident escalation.']:
    y=bullet(p,s,y,size=10.2)
y+=9
cols=[M,M+230,M+355,W-M]
headers=['Action / deliverable','Owner','Due date / status']
p.draw_rect(fitz.Rect(M,y,W-M,y+25),color=None,fill=NAVY)
for j,h in enumerate(headers):text(p,h,y+7,x=cols[j]+8,width=cols[j+1]-cols[j]-15,size=8.7,font='B',color=WHITE)
y+=25
for i in range(5):
    for x in cols:p.draw_line((x,y),(x,y+35),color=LINE,width=.6)
    y+=35;rule(p,y)
y+=18
p.draw_rect(fitz.Rect(M,y,W-M,y+87),color=None,fill=PALE)
text(p,'Proposed technical acceptance point',y+11,x=M+12,width=CW-24,size=10.7,font='B',color=NAVY)
text(p,'Our team can build and run the Dashboard and CRM in our test environment, restore the required data, connect to the retained Mindsmiths services and complete the agreed critical workflows using the delivered materials and agreed support.',y+32,x=M+12,width=CW-24,size=10.1)
y+=105
y=label(p,'Source key',y)
sources=[
('T','Frankie product and technical dosumentation 20261001.pdf','274-page product, technical and user documentation; page numbers refer to this PDF.'),
('D','Frankie Dashboard IT handover status.docx','Dashboard environment, tooling and deployment description.'),
('P','Frankie platform IT handover status.docx','CRM / BookStack description, dependencies and build process.'),
('H','Frankie_Handover_Presentation_vF.pdf','June 2026 handover overview and component boundary.'),
('F','Framework for Migrating External Projects into FS IT Ecosystem_v1.0.docx','18 June 2025; FS and implementation-partner responsibilities.')]
for key,name,desc in sources:
    y=text(p,key+'  '+name,y+7,size=8.5,font='B',color=NAVY)
    y=text(p,desc,y+1,size=8.1,color=MUTED)
assert y<780,y

# Final consistent page furniture and metadata.
for i,p in enumerate(doc):
    rule(p,800)
    text(p,'FRANKIE  |  Meeting preparation  |  7 October 2026',809,size=8,color=MUTED)
    s=f'{i+1} / {len(doc)}'
    p.insert_text((W-M-fonts['B'].text_length(s,fontsize=8.5),817.5),s,fontname='B',fontsize=8.5,color=TEAL)
doc.set_metadata({'title':'Frankie Dashboard and CRM Migration - Meeting Guide','author':'','subject':'Evidence-based questions, requested materials and migration acceptance','keywords':'Frankie, CRM, Dashboard, migration, handover'})
doc.set_toc([[1,'Meeting brief',1],[1,'Data and usage',2],[1,'Platform dependencies',3],[1,'Current-version checks',4],[1,'Operational readiness',5],[1,'Requested materials',6],[1,'Decisions and source key',7]])
doc.subset_fonts()
doc.save(OUT,garbage=4,deflate=True)
doc.close()

check=fitz.open(OUT)
assert len(check)==7,len(check)
for i,p in enumerate(check):
    p.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(QA/f'page-{i+1}.png')
    for b in p.get_text('dict')['blocks']:
        if b['type']!=0:continue
        for ln in b['lines']:
            for sp in ln['spans']:
                r=fitz.Rect(sp['bbox'])
                assert r.x0>=M-1 and r.x1<=W-M+1,(i+1,sp['text'],r)
                assert r.y0>=15 and r.y1<=830,(i+1,sp['text'],r)
content='\n'.join(p.get_text() for p in check)
for term in ['50,000','7%','relationManagerDB.summary','invites_rejected_count','BookStack','Acceptance']:
    assert term.lower() in content.lower(),term
print('Created:',OUT)
print('Pages:',len(check),'Bytes:',OUT.stat().st_size)
print('All text bounding boxes are within page margins; rendered every page for visual review.')
