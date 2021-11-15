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
directory = FSDirectory.open(Paths.get('./CranField_index'))
# directory = RAMDirectory()

analyzer = StopAnalyzer()
cf = IndexWriterConfig(analyzer)
cf.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

writer = IndexWriter(directory, cf)

# Read file Cranfield
CRANFIELD_DIR = './CranField'
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

def Query(n, quiet = False, hide_feature = False):
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
    precison_list = []
    for i in range(len(num_query)):
        returned_docs = []
        num_real_related_doc_retrieval = 0
        keyword = content_query[i]
        num = num_query[i]
        if not quiet:
            print('='*20)
            print('Querying ' + str(i+1) +' <' + keyword + '>', sep='')
        query = parser.parse(keyword)
        doclist = searcher.search(query, n)
        docs = doclist.scoreDocs
        with open('./TEST/RES/'+str(i+1) + ".txt", "r") as datafile:
            real_related_doc = datafile.read().split()[1::3]
        
        for item in docs:
            doc = searcher.doc(item.doc)
            returned_docs.append(doc.get('index')) # Get returned documents ID

        for idx in returned_docs:
            if idx in real_related_doc:
                num_real_related_doc_retrieval += 1
        
        precison_retrieval = num_real_related_doc_retrieval/n
        precison_list.append(precison_retrieval)

        recall_retrieval = num_real_related_doc_retrieval/ len(real_related_doc)
        if not quiet:
            print("Precision: " + str(precison_retrieval))
            if not hide_feature:
                print("Recall: " + str(recall_retrieval))
                try:
                    print("F1-Score: " + str(2*precison_retrieval*recall_retrieval/(precison_retrieval + recall_retrieval)))
                except: # P, R = 0
                    if precison_retrieval == 0 and recall_retrieval == 0:
                        print("F1-Score: 0")

    MAP = sum(precison_list)/225
    return MAP

print(Query(5))
print('\n\n========== P@5 ==========\n')
print()
Query(5, False, True)


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
