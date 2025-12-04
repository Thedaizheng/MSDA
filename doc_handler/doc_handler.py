from doc_handler import reader, formatter, base


class DocHandler:
    def __init__(self):
        self.handle_process = reader.Reader() | formatter.Formatter()

    def handle_doc(self, doc_name):
        sess = base.Session()
        sess.file_name = doc_name

        self.handle_process.exec(sess)

        return sess.title

instance = DocHandler()
