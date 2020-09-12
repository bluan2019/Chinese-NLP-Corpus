import sys, os, json, re
from collections import Counter, defaultdict
def get_ents(label_seq):
    bad_idx = [i for i, l in enumerate(label_seq) if not l.strip()]
    label_seq = list(label_seq)
    for i in bad_idx:
        label_seq[i] = 'O'
    status_str = ''.join([label[0] for label in label_seq]) 
    ents = [ent.span() for ent in re.finditer(r'BI*E?|S', status_str)]
    ents = [{ 
                'span':(s,e), 
                'type':label_seq[s].split('-')[1]
            } for s, e in ents]
    return ents

def cut_sent(text:str, delimiter=r"([。；;\s+])"):
    sentences = re.split(delimiter, text)
    sentences.append("")
    sentences = ["".join(i) for i in zip(sentences[0::2],sentences[1::2])]
    sentences = [sent for sent in sentences if sent.strip()]
    larger_than_512 = len([(l, c) for l, c in Counter([len(sent) for sent in sentences]).items() if l > 512])
    print(f'{larger_than_512} sent larger than 512')
    return sentences

def split(tokens, labels, delimiter='([。])'):
    text = ''.join(tokens)
    assert len(text) == len(tokens)
    text_list = cut_sent(text, delimiter)
    idx, token_list, label_list = 0, [], []
    for text in text_list:
        token_list.append(tokens[idx:idx+len(text)])
        label_list.append(labels[idx:idx+len(text)])
        idx += len(text)
    return token_list, label_list

if __name__ == '__main__':
    path = sys.argv[1]
    data = [line.split('\t') for line in open(path).read().split('\n') if line.strip() and len(line.split('\t'))==2]
    tokens, labels = zip(*data)
    token_list, label_list = split(tokens, labels)
    dataset = []
    all_types = set()
    for token, label in zip(token_list, label_list):
        ents = get_ents(label)
        data = defaultdict(list)
        data['tokens'] = token
        data['crf'] =  label
        for e in ents:
            all_types.add(e['type'])
            data[e['type']].append(e['span'])
        dataset.append(data)
    for data in dataset:
        for k in all_types:
            if k not in data:
                data[k] = []
            
    path = f'{path}.result.json'
    outf = open(path, 'w')
    for data in dataset:
        print(json.dumps(data, ensure_ascii=False), file=outf)
