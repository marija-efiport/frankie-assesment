from pathlib import Path
import sys, html, json
sys.path.insert(0, r'C:/Users/ilic/AppData/Local/uv/cache/archive-v0/n10Xfaj6sTF2htIT')
import pymupdf as fitz
ROOT=Path(r'C:/Users/ilic/Downloads/Frankie-Handover')
OUT=ROOT/'output/pdf'; OUT.mkdir(exist_ok=True,parents=True)
TMP=ROOT/'tmp/assessment-build'
NAVY=(.08,.16,.24); TEAL=(0,.38,.40); GREY=(.34,.39,.44)
fonts={k:fitz.Font(fontfile='C:/Windows/Fonts/'+v) for k,v in {'R':'arial.ttf','B':'arialbd.ttf'}.items()}
sections=[
('Assessment conclusion',[
('Current finding','The handover package supports an initial migration assessment. It does not yet demonstrate that Frankie can be transferred or replaced safely. Production access, source repositories, data exports and operational evidence have not been validated in this assessment.'),
('What we have','A June 2026 handover proposal; separate Dashboard and platform status documents; a 274-page product and technical document; the FS migration framework; supplier security policies; and earlier local assessment notes.'),
('What we need','An agreed migration scope, evidence of actual use, a verified inventory of live functions and dependencies, access to transferable assets, and named owners for delivery and continued support.'),
('Decision supported now','Start evidence collection and scope confirmation. Keep production migration approval pending until the acceptance gates in this report have evidence and accountable owners.'),
('Basis and limitations','Document-based assessment dated 8 October 2026. Sources describe systems at different times. No live systems, source code, actual messages, contracts or staffing availability were audited. Missing evidence means readiness is unproven; it does not prove a control or capability is absent.')], 'Sources: H pp. 2-8; D; P; F; local notes A and B.'),
('Scope and migration options',[
('Unresolved direction','Local note A says the existing system stays with the supplier and FS builds new. Local note B describes taking over selected parts while replacing the licensed platform. The June handover proposal instead retains Mindsmiths on license. These are materially different scopes; no final selection is assumed here.'),
('Option 1: selected-component handover','Transfer Dashboard, CRM and BookStack while keeping Mindsmiths licensed, as described in H and P. Assess code rights, reproducible builds, licensed interfaces and supplier support. This can establish FS ownership of selected components but retains the platform dependency.'),
('Option 2: takeover plus replacement','Take over usable components and replace the licensed runtime. Assess each CRM dependency and the full behavior behind events, conversations, human replies, reporting and knowledge retrieval. Reuse is conditional on rights and technical evidence.'),
('Option 3: new platform','Build an independently operated replacement while the supplier operates the existing service. Agree which live functions and data must carry over, the permitted interfaces and exports, and the duration of parallel support. Existing code transfer is not automatically required.'),
('Common assessment boundary','Document the present service first. Confirm current-function parity and exclusions with the product owner; do not treat every prototype or proposed feature as a migration requirement. Leadership must confirm the target direction and who maintains the current system.')], 'Sources: H pp. 2, 5, 7; P; A; B. Options and implications are assessment analysis.'),
('What the documents describe',[
('Dashboard','A static React/Redux application using the CRM API. D reports FS-managed AWS hosting, staging and production on one server, manual SSH/rsync deployment and no automatic CI/CD at the time of writing. Hosting at FS alone does not establish full operational ownership.'),
('CRM and data','P describes Django/Python with PostgreSQL and Redis. Builds use Mindsmiths CI and Azure Container Registry. The dependency list includes Forge and platform adapter packages. A source-code handover alone does not demonstrate an independent build or runtime.'),
('Knowledge base','P describes BookStack with MariaDB. T describes content ingestion, tags, permissions and search processing. Content migration must include attachments, access rules and verification of what reaches retrieval, not only article text.'),
('Licensed platform and channels','H places AI logic, conversation routing, agents and WhatsApp integration in the Mindsmiths layer. T also describes platform MongoDB and integrations. The complete live database, account and interface inventory remains to be confirmed.'),
('People and service','H identifies content work, ticket handling, human replies, event operations and technical maintenance. These responsibilities remain necessary under any target architecture. Its historical team counts are not a staffing estimate for the incoming team.')], 'Sources: D; P; H pp. 2-6; T pp. 116-120, 141-156, 188-190.'),
('What we have / what we need',[
('Business scope | partial evidence','Have: documented workflows and handover proposal. Need: demonstrations of live journeys, usage by function, explicit exclusions and signed acceptance scenarios. Proposed owner: product owner with business representatives.'),
('Code and rights | unverified','Have: stack descriptions and planned GitHub access. Need: repository history and production revision for transferable components, package access, build instructions, rights and license boundaries. Proposed owners: suppliers and FS technical lead; rights confirmation by the relevant contract owner.'),
('Data and integrations | partial evidence','Have: API descriptions and named stores. Need: samples, schemas, complete exports, reconciliation counts, retention requirements, attachment locations and interface owners. Proposed owners: supplier data lead and FS integration owners.'),
('Hosting and releases | documented gaps','Have: descriptions of manual Dashboard deployment and supplier CRM builds. Need: current inventory, FS environments, deployment and rollback evidence, monitoring and restore results. Proposed owners: FS Infrastructure/DevOps with suppliers.'),
('Operations and governance | unverified','Have: role descriptions, framework and policy documents. Need: named support/content owners, agreed service coverage, current access evidence, applicable security reports and knowledge-transfer records. Proposed owners: service owner, FS Security and supplier leads.')], 'Sources: D; P; F; H pp. 6-8. Status concerns evidence in this package, not a live-system audit.'),
('Usage and quality assessment',[
('Reported figures need a defined basis','Earlier local note B mentions 50,000 messages and 7% usage. These figures have not been verified from data here. Obtain the time period, cohort, active-user numerator, eligible-user denominator, exclusions and calculation before presenting either as a confirmed metric.'),
('Existing export route','T pp. 196-200 documents GET /conversations and per-user history, date filters, pagination, totals, message_id deduplication and auth.view_conversation. Request a sample and complete agreed export using this route if available; confirm the live API matches the documentation.'),
('Required linked datasets','Obtain stable pseudonymous user IDs, message IDs and timestamps, user/cohort records including users with no messages, and available conversation, channel and author fields. Add quality labels, tickets, outcomes, event activity and delivery failures where recorded. Confirm safe handling of free text.'),
('Validation and analysis','Reconcile counts, dates, pagination, duplicates and joins. Separate imported profiles, incomplete onboarding and active users; distinguish proactive messages from student activity where possible. Segment adoption and repeat use by cohort. Review a documented sample for answer correctness and successful task completion.'),
('Outputs and interpretation','Produce a reproducible usage baseline, function-demand summary and quality findings with coverage limits. One message is not proof of value; no ticket is not proof of a correct answer. Low use alone cannot identify its cause. These results inform scope and priorities, rather than justify an assumed rebuild.')], 'Sources: B (unverified figures); T pp. 86-87, 94-95, 133-134, 176-186, 196-220, 223-234.'),
('Principal migration risks',[
('Platform dependencies','CRM operations refer to platform APIs for events, email, human replies and KPIs, including direct platform MongoDB reads for human-reply state. Closure evidence: interface inventory, contract examples and end-to-end tests against the retained or replacement service. Proposed owner: technical lead.'),
('Incomplete or inconsistent data','Conversation exports alone may omit users without messages, attachments or activity held elsewhere. Closure evidence: store inventory, mapped data model, trial import and reconciliation of records, relationships and exclusions. Proposed owner: data migration lead.'),
('Service interruption','Support ownership and the working cutover procedure are not demonstrated. Closure evidence: support agreement, trained operators, release rehearsal, restore test, rollback triggers and verified channel routing. Proposed owner: service owner with DevOps.'),
('Knowledge and answer degradation','Content, tags, permissions, synchronization and retrieval all affect answers. Closure evidence: content-owner sign-off, retrieval checks, representative answer evaluation and escalation tests. Proposed owner: knowledge lead with product and engineering.'),
('Unproven security readiness','Supplier policy PDFs are statements of policy, not evidence of controls on the current Frankie deployment. Closure evidence: FS-agreed review scope, access and secrets review, applicable code/security reports and accepted remediation. Proposed owner: FS Security.')], 'Sources: T pp. 116-120, 154-156, 172, 182-190, 200-205; H pp. 6-8; F; S policy set. Risk priorities require joint confirmation.'),
('Assessment work and acceptance gates',[
('1. Scope and evidence baseline','Confirm the direction, current support owner and decision maker. Record each live function, source, supplier contact and access request. Exit: agreed assessment scope and evidence register; missing items have owners and response dates.'),
('2. Verification','Demonstrate workflows; reproduce usage measures; inspect transferable code and interfaces; trial data export/import; validate deployment and restore capability. Exit: findings supported by demonstrations or artifacts, with unresolved items explicitly recorded.'),
('3. Target and delivery plan','Compare viable options, define the target architecture and retained dependencies, break work into packages and confirm team capacity. Exit: recommended option with effort ranges, dependencies, cost categories and stated confidence. No delivery date is supported yet.'),
('4. Later migration approval','Before production change, require FS staging acceptance, data reconciliation, role/access checks, critical workflow tests, agreed quality/security evidence, channel cutover and rollback rehearsal, support readiness and business sign-off. The appropriate owners must agree thresholds before testing.'),
('FS alignment','F requires FS GitHub, managed environments and CI/CD, plus JIRA, Confluence, Teams and Figma as applicable. Existing compliant tooling can be reused. Its stated supplier responsibilities must be checked against actual agreements; the framework itself does not prove contractual commitment.')], 'Sources: F sections 1-5; H p. 7. Work sequence and gates are proposed; no durations are commitments.'),
('People, estimates and immediate requests',[
('Capabilities required','Cover product decisions, technical architecture, frontend/backend work, integrations and data, AI/retrieval evaluation, DevOps, testing, security review, knowledge editing and service operations. One person may cover multiple responsibilities; headcount is not established by this list.'),
('How to estimate','For each approved work package record scope, dependencies, acceptance tests, effort range and uncertainty. Confirm each person\'s available days after other commitments and existing-service support. Build a dependency-based schedule and include supplier lead times, testing, transition and operating costs.'),
('First evidence request','Request read-only access or controlled copies; message and user samples with metric definitions; active-function demonstrations; transferable repositories and production revisions; interface contracts; and infrastructure, backup and support records. Requests are prepared here, not sent.'),
('Decisions for the assessment meeting','Confirm the migration direction, business sponsor and service owner. Assign evidence owners and response dates. Agree which live functions are mandatory and who supports the current service during assessment and delivery. Return for a migration decision when the evidence gates are met.'),
('Deliverable of the next assessment iteration','A verified current-state inventory, usage and quality baseline, prioritized gap/risk register, agreed target recommendation and explainable resource/cost/schedule ranges. Earlier illustrative staffing and time estimates in local notes must not be reused as commitments.')], 'Sources: F; H pp. 6-8; A; B. Resource approach and next actions are recommendations.'),
('Source register and traceability',[
('H | handover proposal','Frankie_Handover_Presentation_vF.pdf, June 2026, pp. 2-8. Describes the proposed transfer perimeter, licensed platform, roles, transition and risks.'),
('D / P | component status','Frankie Dashboard IT handover status.docx and Frankie platform IT handover status.docx, under 7. Migration into FS IT Ecosystem. Describe component stacks, hosting, build and access status at the time of writing.'),
('F | FS requirements','Framework for Migrating External Projects into FS IT Ecosystem_v1.0.docx, 18 June 2025, in the same folder. Used as the target governance and acceptance framework.'),
('T / S | technical and policy evidence','T: 8. Frankie product and technical documentation/Frankie product and technical dosumentation 20261001.pdf. Page numbers in this assessment refer to PDF pages. S: ten PDFs in Frankie Platform ISO documentation. Policies do not verify current implementation or certification.'),
('A / B | earlier local working notes','A: Frankie-assessment-i-plan.md. B: Frankie-pregled-dokumentacije.md. Both dated 6 October 2026. They contain useful leads and conflicting scope statements, and are not independent system evidence. This assessment used source extracts and targeted technical passages; it is not a fresh page-by-page audit of all source PDFs. The 2023 technical report is historical and is not used to establish current readiness.')], 'Prepared 8 October 2026. External links embedded in source documents were not accessed for this assessment.')
]
slides=[
('Frankie migration assessment','What we have, what we need, and the decisions ahead',[
'Document-based assessment | 8 October 2026',
'For business, IT, operations and supplier stakeholders',
'Current conclusion: migration readiness remains unproven'],0),
('What we can conclude now','The documents provide a baseline; execution readiness needs evidence',[
'We have product, architecture, component and handover descriptions.',
'We still need verified access, data, live workflows and support commitments.',
'Recommendation: complete verification before committing to migration, staffing or dates.'],0),
('Migration scope remains a decision','The working notes and supplier proposal describe different destinations',[
'Selected-component handover: FS takes Dashboard, CRM and BookStack; Mindsmiths stays licensed.',
'Takeover plus replacement: retain useful components and replace the licensed runtime.',
'New platform: build a replacement while the supplier operates the existing service.'],1),
('What the current system includes','The scope extends beyond answering student questions',[
'Student service: onboarding, conversations, events, preferences and knowledge access.',
'Staff service: Dashboard, tickets, human replies, content maintenance and reporting.',
'Technical dependencies: CRM, BookStack, licensed agents, channels and FS integrations.',
'Live functionality and prototype status still require demonstration.'],2),
('What we have and what we need','Each document must lead to a verifiable handover artifact',[
'Stack descriptions -> source rights, production revision and a reproducible build.',
'API and database descriptions -> sample exports, schemas and reconciled data.',
'Hosting descriptions -> current inventory, deployment and recovery evidence.',
'Role and policy descriptions -> named owners, support terms and control evidence.'],3),
('Actual usage comes first','Reported message volume and adoption are not yet verified',[
'The earlier notes mention 50,000 messages and 7% usage; period and calculation remain unconfirmed.',
'Obtain messages plus all eligible users, including people with no messages.',
'Recalculate adoption and repeat use; assess quality with linked reviews and outcomes.',
'Use the results to agree which current functions the target must preserve.'],4),
('Key migration risks','A code transfer does not remove runtime dependencies',[
'Licensed interfaces drive events, human replies, reporting and retrieval.',
'Data can span CRM, platform stores, knowledge content and attachments.',
'Support gaps and lost operational knowledge can interrupt student service.',
'Closure requires tested interfaces, reconciled data and trained service owners.'],5),
('Assessment deliverables','The next decision should rest on observed evidence',[
'Verified inventory of live functions, systems, data and dependencies.',
'Reproducible usage and answer-quality baseline with limitations.',
'Prioritized gaps with owners and concrete closure evidence.',
'Target recommendation and work packages with defensible effort and cost ranges.'],6),
('What is needed from each group','Responsibilities must be assigned before scheduling delivery',[
'Business: confirm scope, priorities and acceptance scenarios.',
'Suppliers: provide evidence, walkthroughs, rights and support commitments.',
'FS IT: define target environments, integration owners and review requirements.',
'Operations and content: own service coverage, knowledge quality and escalation.'],7),
('Decisions for this meeting','Agree how the assessment will reach a migration decision',[
'Confirm the migration direction and accountable sponsor.',
'Assign evidence owners and response dates.',
'Confirm who supports the existing service during transition.',
'Keep production approval pending until testing, data and operational gates pass.'],7)
]
def wrap(t,w,size,font):
    result=[]
    for para in t.split('\n'):
        line=''
        for word in para.split():
            trial=(line+' '+word).strip()
            if fonts[font].text_length(trial,fontsize=size)>w and line:result.append(line);line=word
            else:line=trial
        result.append(line)
    return result
def text(p,t,x,y,w,size=11,font='R',color=NAVY,leading=None):
    leading=leading or size*1.38
    for line in wrap(t,w,size,font):
        p.insert_text((x,y+size),line,fontname=font,fontsize=size,color=color);y+=leading
    return y
def page(doc,w,h):
    p=doc.new_page(width=w,height=h)
    for k,v in {'R':'arial.ttf','B':'arialbd.ttf'}.items():p.insert_font(fontname=k,fontfile='C:/Windows/Fonts/'+v)
    return p
report=fitz.open()
for i,(title,items,source) in enumerate(sections):
    p=page(report,595,842)
    text(p,'FRANKIE / MIGRATION ASSESSMENT',44,30,507,9,'B',TEAL)
    y=text(p,title,44,62,507,25,'B')+19
    for label,body in items:
        y=text(p,label,44,y,507,12,'B',TEAL)+5
        y=text(p,body,44,y,507,10.5)+16
    assert y<755,(i,y)
    text(p,source,44,761,507,8,color=GREY)
    text(p,f'8 October 2026 | Document-based assessment                                   {i+1} / {len(sections)}',44,815,507,8,color=GREY)
report.save(OUT/'Frankie-Migration-Assessment.pdf')
deck=fitz.open()
for i,(title,sub,items,ref) in enumerate(slides):
    p=page(deck,960,540)
    text(p,title,55,40,850,32,'B')
    text(p,sub,55,98,850,17,color=TEAL)
    y=160
    for item in items:
        y=text(p,item,55,y,840,22 if i==0 else 20)+24
    assert y<476,(i,y)
    text(p,f'Assessment section {ref+1}: {sections[ref][0]} | Sources and qualifications in accompanying assessment',55,490,850,9,color=GREY)
    text(p,f'Frankie | 8 October 2026                                                                                         {i+1} / {len(slides)}',55,516,850,9,color=GREY)
deck.save(OUT/'Frankie-Migration-Assessment-Presentation.pdf')
# Render every page for visual review; make contact sheets without changing document content.
for name,doc in [('report',report),('slides',deck)]:
    thumbs=[]
    for i,p in enumerate(doc):
        pix=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pix.save(TMP/f'{name}-{i+1:02}.png')
        thumbs.append(p)
    for start in range(0,len(doc),4):
        sheet=fitz.open();sp=sheet.new_page(width=1200,height=900)
        for j in range(min(4,len(doc)-start)):
            col=j%2;row=j//2
            sp.show_pdf_page(fitz.Rect(col*600,row*450,(col+1)*600,(row+1)*450),doc,start+j)
        sp.get_pixmap().save(TMP/f'{name}-sheet-{start//4+1}.png')
# Editable browser presentation, using the same reviewed content.
body=''.join('<section><h1>'+html.escape(t)+'</h1><h2>'+html.escape(s)+'</h2><ul>'+''.join('<li>'+html.escape(v)+'</li>' for v in items)+'</ul><footer>Assessment section '+str(ref+1)+' | '+str(i+1)+' / '+str(len(slides))+'</footer></section>' for i,(t,s,items,ref) in enumerate(slides))
css='body{margin:0;background:#eef2f4;color:#14293d;font:22px Arial}section{box-sizing:border-box;max-width:1100px;min-height:620px;margin:30px auto;padding:50px 65px;background:white}h1{font-size:40px;margin:0 0 22px}h2{font-size:23px;font-weight:normal;color:#006166}li{margin:24px 0;line-height:1.4}footer{font-size:13px;color:#56616c;margin-top:32px}@media print{section{margin:0;page-break-after:always}}'
(ROOT/'output/assessment/Frankie-Migration-Presentation.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Frankie migration assessment</title><style>'+css+'</style>'+body+'</html>',encoding='utf8')
print('Created assessment: '+str(len(report))+' pages; presentation: '+str(len(deck))+' slides.')
