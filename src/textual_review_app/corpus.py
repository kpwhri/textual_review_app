from jsonl_index import JsonlIndex


class Corpus:

    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.idx = JsonlIndex(self.corpus_path, load=True)

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, item):
        return self.idx.get(item)
