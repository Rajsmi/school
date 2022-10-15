def odcesti(text: str) -> str:
    word = ''

    for lett in text:
        cz_letters = 'ěščřžýáíéúůťďň'
        en_letters = 'escrzyaieuutdn'

        if lett.isupper():
            cz_letters, en_letters = cz_letters.upper(), en_letters.upper()

        if lett in cz_letters:
            word += en_letters[cz_letters.index(lett)]
            continue
        word += lett
    return word


print(odcesti(input('text: ')))
