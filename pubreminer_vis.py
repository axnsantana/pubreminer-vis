class PubreminerData:

    def __init__(self,filename):
        self.filename = filename
        self.data={}

    def process(self):
        import re
        from itertools import izip
        file = open(self.filename)
        self.text = file.read()
        self.query_info = re.findall('(#\s.*?)\n',self.text,re.DOTALL)
        self.query_info = "\n".join(self.query_info)
        groups = re.findall('(#T.*?)\n(?:\n{2}|$)',self.text,re.DOTALL)
        for g in groups:
            info=re.findall('^#T:(.*)',g)
            if(info):
                info = info[0]
                data = self.data[info]=[]
                columns = re.findall('#H:(.*)',g)
                if(columns):
                    columns = columns[0].split('\t')
                    data_lines = re.findall('#H:.*?\n(.*)$',g,re.DOTALL)
                    data_lines = data_lines[0].split('\n')
                    for d in data_lines:
                        values = d.split('\t')
                        entry = {}
                        data.append({k:v for k, v in izip(columns,values)})
                else:
                    data_lines = re.findall('#T:.*?\n(.*)$',g,re.DOTALL)
                    if(data_lines):
                        self.data[info]=data_lines[0].split()

class PubreminerVis:
    def __init__(self):
        pass
