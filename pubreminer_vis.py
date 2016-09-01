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


class PubreminerVis:
    def __init__(self):
        pass
