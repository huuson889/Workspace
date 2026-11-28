"""Synthetic layout regression; no user document content or expected-page hacks."""
from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement,parse_xml
from docx.oxml.ns import nsdecls,qn
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_BREAK
r=Path(__file__).parent;doc=Document();doc.add_paragraph('Synthetic layout rules')
p=doc.add_paragraph()
ns='xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"'
for i,colour in enumerate(['2266AA','CC5500','228844']):
 x=600000+i*1100000
 s=f'<w:drawing {ns}><wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" behindDoc="0" layoutInCell="1" allowOverlap="1"><wp:simplePos x="0" y="0"/><wp:positionH relativeFrom="page"><wp:posOffset>{x}</wp:posOffset></wp:positionH><wp:positionV relativeFrom="paragraph"><wp:posOffset>0</wp:posOffset></wp:positionV><wp:extent cx="1000000" cy="571500"/><wp:wrapTopAndBottom/><wp:docPr id="{i+1}" name="Test rectangle {i+1}"/><a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"><wps:wsp><wps:cNvSpPr/><wps:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="1000000" cy="571500"/></a:xfrm><a:prstGeom prst="rect"/><a:solidFill><a:srgbClr val="{colour}"/></a:solidFill></wps:spPr><wps:bodyPr/></wps:wsp></a:graphicData></a:graphic></wp:anchor></w:drawing>'
 p.add_run()._r.append(parse_xml(s))
doc.add_paragraph('After three side-by-side rectangles')
t=doc.add_table(rows=2,cols=2);t.cell(0,0).text='Metric';t.cell(0,1).text='Value';t.cell(1,0).text='Synthetic';t.cell(1,1).text='One'
pos=OxmlElement('w:tblpPr')
for key,value in [('vertAnchor','text'),('tblpX','0'),('tblpY','800'),('leftFromText','0'),('rightFromText','0')]:pos.set(qn('w:'+key),value)
t._tbl.tblPr.append(pos)
doc.add_paragraph('Floating table anchor heading')
section=doc.add_section(WD_SECTION_START.CONTINUOUS);cols=section._sectPr.find(qn('w:cols'));cols.set(qn('w:num'),'2');cols.set(qn('w:equalWidth'),'0')
for w,space in [('2880','240'),('5520','0')]:
 c=OxmlElement('w:col');c.set(qn('w:w'),w);c.set(qn('w:space'),space);cols.append(c)
doc.add_paragraph('Left explicit column')
p=doc.add_paragraph();p.add_run().add_break(WD_BREAK.COLUMN);p.add_run('Right explicit column')
doc.save(r/'layout-rules.docx');print(r/'layout-rules.docx')
