"""Keep large PPTX conversion under the demo's RAM budget.
Only presentation slide/master lists are restricted per batch; slide XML is unchanged.
Cross-batch hyperlinks, sections, custom shows and PDF structure tags aren't preserved.
"""
from pathlib import PurePosixPath
import copy
import posixpath
import zipfile
from lxml import etree as E

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PARSER = E.XMLParser(resolve_entities=False, no_network=True)


def batches(source, output, size=8):
    with zipfile.ZipFile(source) as z:
        presentation = E.fromstring(z.read('ppt/presentation.xml'), PARSER)
        ids = presentation.find('{'+P+'}sldIdLst')
        if ids is None or not len(ids):
            raise ValueError('No slide list')
        count = len(ids)
        if count <= 12:
            yield (source, count)
            return
        relpath = 'ppt/_rels/presentation.xml.rels'
        relations = E.fromstring(z.read(relpath), PARSER)
        links = {r.get('Id'): r for r in relations}
        def target(base, rel):
            t = rel.get('Target')
            return t.lstrip('/') if t.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(base), t))
        def related(part, suffix):
            pp = PurePosixPath(part)
            rp = str(pp.parent / '_rels' / (pp.name + '.rels'))
            if rp not in z.namelist():
                return None
            for rel in E.fromstring(z.read(rp), PARSER):
                if rel.get('Type', '').endswith('/'+suffix) and rel.get('TargetMode') != 'External':
                    return target(part, rel)
            return None
        for start in range(0, count, size):
            root = E.fromstring(z.read('ppt/presentation.xml'), PARSER)
            idlist = root.find('{'+P+'}sldIdLst')
            subset = list(idlist)[start:start+size]
            selected_ids = {i.get('{'+R+'}id') for i in subset}
            for node in list(idlist):
                if node not in subset:
                    idlist.remove(node)
            needed_masters = set()
            for rid in selected_ids:
                slide = target('ppt/presentation.xml', links[rid])
                layout = related(slide, 'slideLayout')
                master = related(layout, 'slideMaster') if layout else None
                if master:
                    needed_masters.add(master)
            rels = E.fromstring(z.read(relpath), PARSER)
            removed = set()
            for rel in list(rels):
                kind = rel.get('Type', '').split('/')[-1]
                if (kind == 'slide' and rel.get('Id') not in selected_ids) or (kind == 'slideMaster' and target('ppt/presentation.xml', rel) not in needed_masters):
                    removed.add(rel.get('Id')); rels.remove(rel)
            masterlist = root.find('{'+P+'}sldMasterIdLst')
            if masterlist is not None:
                for node in list(masterlist):
                    if node.get('{'+R+'}id') in removed:
                        masterlist.remove(node)
            # These lists refer to slides no longer present in this temporary batch.
            for node in root.xpath('./p:custShowLst | ./p:extLst', namespaces={'p':P}):
                root.remove(node)
            overrides = {'ppt/presentation.xml': E.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True),
                         relpath: E.tostring(rels, xml_declaration=True, encoding='UTF-8', standalone=True)}
            path = output / ('batch-%03d.pptx' % (start//size+1))
            with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as out:
                for info in z.infolist():
                    out.writestr(copy.copy(info), overrides[info.filename] if info.filename in overrides else z.read(info))
            yield (path,len(subset))
