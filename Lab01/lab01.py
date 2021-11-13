import lucene
import os
from java.nio.file import Paths, Path
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.analysis.core import StopAnalyzer
from org.apache.lucene.search import IndexSearcher, TopDocs, ScoreDoc
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.store import FSDirectory

lucene.initVM()
directory = FSDirectory.open(Paths.get('./lucene/index'))
# directory = RAMDirectory()

analyzer = StopAnalyzer()
cf = IndexWriterConfig(analyzer)
cf.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

writer = IndexWriter(directory, cf)

# Read file Cranfield
CRANFIELD_DIR = './Cranfield'
for file in os.listdir(CRANFIELD_DIR):
    filepath = os.path.join(CRANFIELD_DIR, file)
    f = open(filepath)
    text = f.read()
    doc = Document()
    basename = os.path.basename(filepath)
    name = os.path.splitext(basename)[0]
    index = StringField('index', str(name), Field.Store.YES)
    content = TextField('content', text, Field.Store.YES)
    doc.add(index)
    doc.add(content)
    writer.addDocument(doc)

writer.close()

reader = DirectoryReader.open(directory)
searcher = IndexSearcher(reader)
parser = QueryParser('content', analyzer)

# Read file query.txt
QUERY_DIR = './TEST/query.txt'
with open(QUERY_DIR, "r") as f:
    datalist = f.readlines()
num_query = []
content_query = []
for s in datalist:
    line = s.strip()
    ct = line.split('\t')
    num_query.append(ct[0])
    content_query.append(ct[1])


# Print related documents
for i in range(len(content_query)):
    keyword = content_query[i]
    num = num_query[i]
    print('======================')
    print('Querying <', keyword, '> ... ', sep='')
    query = parser.parse(keyword)
    doclist = searcher.search(query, 5)
    docs = doclist.scoreDocs

    for item in docs:
        doc = searcher.doc(item.doc)
        print(num, doc.get('index'), item.score)
    print()
