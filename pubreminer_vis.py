class PubreminerData:

    def __init__(self, filename):
        self.filename = filename
        self.data = {}

    def process(self):
        import re
        from itertools import izip
        file = open(self.filename)
        self.text = file.read()
        self.query_info = re.findall('(#\s.*?)\n', self.text, re.DOTALL)
        self.query_info = "\n".join(self.query_info)
        groups = re.findall('(#T.*?)\n(?:\n{2}|$)', self.text, re.DOTALL)
        for g in groups:
            info = re.findall('^#T:(.*)', g)
            if(info):
                info = info[0]
                data = self.data[info] = []
                columns = re.findall('#H:(.*)', g)
                if(columns):
                    columns = columns[0].split('\t')
                    data_lines = re.findall('#H:.*?\n(.*)$', g, re.DOTALL)
                    data_lines = data_lines[0].split('\n')
                    for d in data_lines:
                        values = d.split('\t')
                        data.append({k: v for k, v in izip(columns, values)})
                else:
                    data_lines = re.findall('#T:.*?\n(.*)$', g, re.DOTALL)
                    if(data_lines):
                        self.data[info] = data_lines[0].split()

    def save_json(self, filename):
        import json
        with open(filename, 'w') as outfile:
            json.dump(self.data, outfile)

    def download_pmid_metadata(self, pmid, filename=None, directory='.',
                               email='example@example.com', tool=''):
        import requests as rq
        from lxml import etree

        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        payload = {'db': 'pubmed', 'id': pmid,
                   'rettype': 'null', 'retmod': 'xml',
                   'email': email, 'tool': tool}
        metadata = rq.get(url, params=payload)

        try:
            xml_string = etree.fromstring(metadata.text)
            if(filename is None):
                filename = "%s.xml" % (pmid)
            filename = "%s/%s" % (directory, filename)
            with open(filename, 'w') as file:
                file.write(etree.tostring(xml_string, pretty_print=True))
        except Exception, e:
            print repr(e)
        return

    def download_all_pmid_metadata(self, directory='.', delay=1,
                                   email='example@example.com', tool=''):
        import os
        import time

        if not os.path.exists(directory):
            os.makedirs(directory)
        total = len(self.data['pmid'])
        c = 1
        for pmid in self.data['pmid']:
            print "Downloading: %d of %d : %s" % (c, total, pmid)
            self.download_pmid_metadata(pmid, directory=directory,
                                        email=email, tool=tool)
            c = c + 1
            time.sleep(delay)

        return

    def is_major_topics(self, xmlfile, tag, UI, major='Y'):
        from lxml import etree

        doc = etree.parse(xmlfile)
        mesh_hearders = doc.findall('.//MeshHeading')
        for header in mesh_hearders:
            for ch in header.getchildren():
                is_major = (ch.attrib['MajorTopicYN'] == 'Y') or (not major)
                if(ch.tag == tag and ch.attrib['UI'] == UI and is_major):
                    print xmlfile, ch.tag
                    print ch.attrib['UI'], ch.attrib['MajorTopicYN']
                    return True
        return False

    def has_qualifier(self, xmlfile, descriptor, qualifier,
                      descriptorMajor=False, qualifierMajor=False,
                      anyMajor=False):
        from lxml import etree

        doc = etree.parse(xmlfile)
        mesh_hearders = doc.findall('.//MeshHeading')
        descriptor_filter = "DescriptorName[@UI='%s']" % descriptor
        qualifier_filter = "QualifierName[@UI='%s']" % qualifier
        for header in mesh_hearders:
            desc_tag = header.find(descriptor_filter)
            qual_tag = header.find(qualifier_filter)
            if(desc_tag is not None and qual_tag is not None):
                anyMajor = ((desc_tag.attrib['MajorTopicYN'] == 'Y') or
                            (qual_tag.attrib['MajorTopicYN'] == 'Y') or
                            not anyMajor)
                if(not anyMajor):
                    return False
                if(descriptorMajor and desc_tag.attrib['MajorTopicYN'] == 'N'):
                    return False
                if(qualifierMajor and qual_tag.attrib['MajorTopicYN'] == 'N'):
                    return False
                print desc_tag.text, desc_tag.attrib['MajorTopicYN']
                print qual_tag.text, qual_tag.attrib['MajorTopicYN']
                return True
        return False


class PubreminerVis:
    def __init__(self):
        pass
