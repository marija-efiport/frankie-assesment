import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const data = JSON.parse(await fs.readFile('analysis.json','utf8'));
const intents = JSON.parse(await fs.readFile('user-intents.json','utf8'));
const out=path.resolve('../../outputs/frankie-message-analysis');
const wb=Workbook.create();
const names=['Overview','User message intent','User topics','Common questions','Common messages','Frankie templates','Event campaigns'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const navy='#233B59', blue='#3568A8', orange='#C77438', grey='#607086';
function write(s,row,cols,rows){if(rows.length)s.getRangeByIndexes(row-1,0,rows.length,cols).values=rows;}
function base(s,title,widths,lastRow=50){
 s.showGridLines=false;
 const range=s.getRangeByIndexes(0,0,lastRow,widths.length);
 range.format.font={name:'Arial',size:10,color:'#243348'};
 range.format.rowHeight=21; range.format.verticalAlignment='center';
 widths.forEach((w,i)=>s.getRangeByIndexes(0,i,lastRow,1).format.columnWidth=w);
 s.getRange('A2').values=[[title]]; s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
 s.getRangeByIndexes(2,0,1,widths.length).format.borders={bottom:{style:'thin',color:'#C9D2DE'}};
 s.tabColor=navy;
}
function table(s,row,headers,rows,name){
 write(s,row,headers.length,[headers,...rows]);
 const r=s.getRangeByIndexes(row-1,0,rows.length+1,headers.length);
 s.tables.add(r,true,name);
 s.getRangeByIndexes(row-1,0,1,headers.length).format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:28,horizontalAlignment:'center',verticalAlignment:'center'};
 if(rows.length)s.getRangeByIndexes(row,1,rows.length,Math.min(3,headers.length-1)).setNumberFormat('#,##0');
 s.freezePanes.freezeRows(row);
}
function chart(s,type,range,title,start,end){
 const c=s.charts.add(type,s.getRange(range));c.title=title;c.hasLegend=type==='line';
 c.titleTextStyle.typeface='Arial';
 c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial'}};
 c.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial'}};
 c.setPosition(start,end);
 c.series.items.forEach((ser,i)=>{ser.fill=[blue,orange,'#589588',grey][i%4];if(type==='line')ser.line={fill:[blue,orange,'#589588',grey][i%4],style:'solid',width:2};});
 return c;
}
const s=sheets.Overview;
base(s,'Frankie message analysis',[43,15,15,15,13,3,14,14,14,14,14,14],65);
s.getRange('A3').values=[[`${data.date_from} to ${data.date_to} | Export completed for all ${data.conversations.toLocaleString()} conversations`]];
const dir=Object.fromEntries(data.direction_rows.map(r=>[r.direction,r]));
table(s,5,['Message direction','Records','Unique users','Share of records'],[
 ['Users → system',dir.inbound.count,dir.inbound.users,null],
 ['Frankie outbound chat',dir.outbound.count,dir.outbound.users,null],
 ['Frankie templates',dir.template.count,dir.template.users,null],
 ['UCS (sender unspecified)',dir.ucs.count,dir.ucs.users,null],
 ['Total',null,data.conversations,null],
],'Directions');
s.freezePanes.unfreeze();
s.getRange('B10').formulas=[['=SUM(B6:B9)']];
s.getRange('D6:D10').formulas=Array.from({length:5},(_,i)=>[`=B${i+6}/$B$10`]);s.getRange('D6:D10').setNumberFormat('0.0%');
write(s,12,2,[['Users who sent messages',data.active_users],['Conversations without inbound',data.received_only],['Question-like inbound records',data.question_like_messages],['Repeated-ID occurrences retained',data.repeated_ids]]);
s.getRange('B12:B15').setNumberFormat('#,##0');
write(s,17,1,[['Records are message occurrences, not unique questions.'],['UCS is separate because its sender role is undocumented.'],['Templates can be proactive or triggered by a user action.']]);
chart(s,'bar','A5:B9','Message records by direction','G5','M20');
s.getRange('A21').values=[['Monthly activity (UTC)']];s.getRange('A21').format.font.bold=true;
table(s,23,['Month','User messages','Outbound chat','Templates','UCS'],data.months.map(r=>[r.month,r.inbound,r.outbound,r.template,r.ucs]),'MonthlyActivity');s.freezePanes.unfreeze();
chart(s,'line',`A23:D${23+data.months.length}`,'Monthly message records','G23','M43');
s.getRange('A44').values=[['April 2025 and October 2026 are partial months. October ends on 13 October.']];
write(s,46,1,[['How to read this analysis'],['Source: '+data.source+'/messages.jsonl and report.json.'],['All 427,081 records scanned. No repeated (conversation, message ID, timestamp) keys.'],['User topics use ordered English/German keyword rules; labels are estimates, not manual coding.'],['Context-dependent replies stay unclassified. Multi-topic messages receive the first matching category.'],['Question rankings normalize case, apostrophes, whitespace and terminal punctuation; synonyms are not merged.'],['Question-like means question punctuation or a question prefix, excluding greetings, short replies and non-text.'],['Unique-user counts overlap across categories and must not be added. No student/test/staff filter was applied.'],['Counts reflect exported records, not delivery/read receipts or event attendance. The export is not a fixed-time snapshot.'],[`The exporter recorded ${data.count_discrepancies} list/detail count differences. ${data.repeated_ids} repeated-ID occurrences were retained.`],
 ['Message index: all records with source line, anonymous conversation label, category and a 1,000-character excerpt.'],['Source anonymization was enabled. Excerpt links and email addresses are removed; original export remains unchanged.']]);
s.getRange('A46').format.font.bold=true;

const t=sheets['User topics'];base(t,'What users sent — estimated primary topics',[43,14,14,14,105],data.topics.length+25);
t.getRange('A3').values=[['One category per inbound record. Read “Other” as unclassified, not as a single topic.']];
table(t,5,['Estimated topic','Messages','Unique users','% of inbound','Common examples (excerpts)'],data.topics.map(r=>[r.topic,r.messages,r.users,null,r.examples.join(' / ').slice(0,400)]),'UserTopics');
t.getRange(`D6:D${5+data.topics.length}`).formulas=data.topics.map((_,i)=>[`=B${i+6}/'Overview'!$B$6`]);t.getRange(`D6:D${5+data.topics.length}`).setNumberFormat('0.0%');
t.getRange(`A6:E${5+data.topics.length}`).format.rowHeight=52;t.getRange(`A6:A${5+data.topics.length}`).format.wrapText=true;t.getRange(`E6:E${5+data.topics.length}`).format.wrapText=true;
const typeRow=data.topics.length+9;t.getRange(`A${typeRow}`).values=[['Inbound content formats (API field)']];
table(t,typeRow+2,['Content format','Records'],data.incoming_types.map(r=>[r.type,r.count]),'InboundFormats');t.freezePanes.freezeRows(5);

const q=sheets['Common questions'];base(q,'Most repeated question-like user messages',[105,14,14,44],data.top_questions.length+7);
q.getRange('A3').values=[['Normalized text, not semantic intent clusters. Counts and unique users include only question-like occurrences.']];
table(q,5,['Normalized user question','Occurrences','Unique users','Estimated topic'],data.top_questions.map(r=>[r.text,r.count,r.users,r.topic]),'CommonQuestions');
q.getRange(`A6:D${5+data.top_questions.length}`).format.rowHeight=40;q.getRange(`A6:A${5+data.top_questions.length}`).format.wrapText=true;q.getRange(`D6:D${5+data.top_questions.length}`).format.wrapText=true;

const m=sheets['Common messages'];base(m,'Most repeated user and outbound messages',[105,14,14,44],170);
m.getRange('A3').values=[['User text is normalized; outbound text is whitespace-normalized. Empty normalized text includes media, blank and punctuation-only input.']];
table(m,5,['Normalized user text','Occurrences','Unique users','Estimated topic'],data.top_messages.map(r=>[r.text,r.count,r.users,r.topic]),'CommonMessages');
m.getRange('A6:D105').format.rowHeight=36;m.getRange('A6:A105').format.wrapText=true;m.getRange('D6:D105').format.wrapText=true;
m.getRange('A109').values=[['Most repeated non-template outbound text']];m.getRange('A109').format.font.bold=true;
table(m,111,['Outbound excerpt (max 400 characters)','Occurrences','Unique users'],data.outbound_common.map(r=>[r.text.slice(0,400),r.count,r.users]),'CommonOutbound');
m.getRange('A112:A161').format.wrapText=true;m.getRange('A112:C161').format.rowHeight=65;m.freezePanes.freezeRows(5);

const v=sheets['Frankie templates'];base(v,'Frankie templates — invitations, reminders and notifications',[44,15,15,15,105],data.templates.length+36);
v.getRange('A3').values=[['Category mapping uses template names and reviewed examples. Template records are not all necessarily unsolicited.']];
table(v,5,['Template category','Records','Unique users','% of templates'],data.template_groups.map(r=>[r.category,r.count,r.users,null]),'TemplateGroups');
v.getRange(`D6:D${5+data.template_groups.length}`).formulas=data.template_groups.map((_,i)=>[`=B${i+6}/'Overview'!$B$8`]);v.getRange(`D6:D${5+data.template_groups.length}`).setNumberFormat('0.0%');
v.getRange(`A6:D${5+data.template_groups.length}`).format.rowHeight=29;
const tr=27;
table(v,tr,['Template name','Records','Unique users','Category','Example excerpt (max 450 characters)'],data.templates.map(r=>[r.name,r.count,r.users,r.category,r.example.slice(0,450)]),'TemplateDetail');
v.getRange(`A${tr+1}:E${tr+data.templates.length}`).format.rowHeight=78;
v.getRange(`A${tr+1}:A${tr+data.templates.length}`).format.wrapText=true;
v.getRange(`D${tr+1}:E${tr+data.templates.length}`).format.wrapText=true;
v.getRange(`D${tr+1}:D${tr+data.templates.length}`).setNumberFormat('@');v.freezePanes.freezeRows(5);

const e=sheets['Event campaigns'];base(e,'Most frequently sent event invitations',[110,16,16,16],data.events.length+8);
e.getRange('A3').values=[['Only the eight generic invite-template variants with an event-title placeholder. Counts are sends, not registrations.']];
table(e,5,['Event title','Invitations sent','Unique recipients','Sends / recipient'],data.events.map(r=>[r.event,r.count,r.users,null]),'EventCampaigns');
e.getRange(`D6:D${5+data.events.length}`).formulas=data.events.map((_,i)=>[`=B${i+6}/C${i+6}`]);e.getRange(`D6:D${5+data.events.length}`).setNumberFormat('0.00');
e.getRange(`A6:D${5+data.events.length}`).format.rowHeight=40;e.getRange(`A6:A${5+data.events.length}`).format.wrapText=true;

const intentSheet=sheets['User message intent'];
base(intentSheet,'User messages — questions, short replies and unsubscribe',[49,14,14,14,95],60);
intentSheet.getRange('A3').values=[['All 93,987 inbound records. One category per message; intent detection is an estimate.']];
table(intentSheet,5,['Message category','Messages','Unique users','% of inbound','Examples'],intents.rows.map(r=>[r.category,r.messages,r.users,null,r.examples.join(' / ').slice(0,320)]),'UserIntent');
intentSheet.getRange(`D6:D${5+intents.rows.length}`).formulas=intents.rows.map((_,i)=>[`=B${i+6}/'Overview'!$B$6`]);
intentSheet.getRange(`D6:D${5+intents.rows.length}`).setNumberFormat('0.0%');
intentSheet.getRange(`A6:E${5+intents.rows.length}`).format.rowHeight=43;
intentSheet.getRange(`A6:A${5+intents.rows.length}`).format.wrapText=true;
intentSheet.getRange(`E6:E${5+intents.rows.length}`).format.wrapText=true;
write(intentSheet,21,1,[['Counts are message occurrences, not unique questions. Users overlap across categories.'],['Lunch includes brief requests such as “menu today”. Other questions include explicit requests and contextual questions.'],['The 89 explicit stop-notification requests were reviewed; event/exam cancellations were excluded.'],['An additional 29 standalone STOP messages have unclear scope. These counts do not prove successful unsubscription.'],['35 explicit requests mention lunch/menu notifications (27 users); 54 refer to other or unspecified notifications (42 users).'],['Short replies match standalone phrases and variants, not every message containing the word yes or no.']]);
intentSheet.getRange('A28').values=[['Other questions and explicit requests — estimated topics']];
table(intentSheet,30,['Estimated topic','Messages','Unique users'],intents.other_questions.map(r=>[r.topic,r.messages,r.users]),'OtherQuestionTopics');
intentSheet.getRange('A31:A47').format.wrapText=true;intentSheet.getRange('A31:C47').format.rowHeight=30;intentSheet.freezePanes.freezeRows(5);
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Overview!A5:D15',include:'values,formulas',tableMaxRows:11,tableMaxCols:4,maxChars:2200})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:15},summary:'Formula error scan',maxChars:1000})).ndjson);
await fs.mkdir(out,{recursive:true});
for(const [name,range] of [['Overview','A1:M20'],['User message intent','A1:E18'],['User topics','A1:E12'],['Common questions','A1:D12'],['Common messages','A1:D12'],['Frankie templates','A1:E12'],['Event campaigns','A1:D12']]){
 const blob=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
 await fs.writeFile(path.join(out,name==='Overview'?'message-overview.png':`preview-${name.replaceAll(' ','-')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,'Frankie-message-analysis-updated.xlsx'));
for(const [name,range,filename] of [['Overview','A21:M43','monthly'],['Frankie templates','A27:E32','template-detail']]){
 const blob=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
 await fs.writeFile(`preview-${filename}.png`,new Uint8Array(await blob.arrayBuffer()));
}
console.log('Saved workbook with '+names.length+' sheets and two editable charts.');
