dic = []
with open('encs.txt', encoding='utf-8') as file:
    f = file.read()
    for term in f.split('\n'):

        dic.append(term.split('|'))


def get_czech_word(cs_word: str, not_found=True):
    res = []
    for x in dic:
        if x[1] == cs_word.lower().strip():
            res.append(x[0])
    if not res:
        if not_found:
            print(f'Zadané slovo "{cs_word}" jsem ve svém slovníku nenašel')
            return
        return cs_word
    else:
        if not_found:
            print(f'{cs_word.lower().strip()} - {", ".join(res)}')
            return
        return res[0]

get_czech_word('půjdu')

def get_czech_sentence(sentence: str):
    tsent = []
    for word in sentence.split():
        tword = get_czech_word(word, not_found=False)
        tsent.append(tword)
    print(" ".join(tsent))

get_czech_sentence('Zítra půjdu domů')
