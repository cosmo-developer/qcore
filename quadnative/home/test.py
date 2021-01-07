import re


def segments(file):
    text = open(file).read().replace('days', '*1').replace('minutes', '/(24*60)').replace('seconds',
                                                                                          '/(24*60*60)').replace(
        'hours', '/24')
    rules = [
        ('QUAD', r'D#(?:(?!#D)(.|\n))*?#D')
        , ('SM', r'(.|\n|)')
    ]
    tokens_join = '|'.join('(?P<%s>%s)' % x for x in rules)
    lin_start = 1
    col = 1
    text = text.replace('{{', '<q.Eval(').replace('}}', ');.q>')
    text = text.replace('<q.', 'D#').replace('.q>', '#D')
    segment = []
    t = ""
    for m in re.finditer(tokens_join, text):
        token_type = m.lastgroup
        token_lexeme = m.group(token_type)
        if token_type == 'QUAD':
            for i in t:
                if i == '\n':
                    col = 1
                    lin_start += 1
                else:
                    col += 1
            segment.append(('TEXT', t, 0, 0))
            t = ""
            segment.append(('TOPARSE', token_lexeme.replace('#D', '').replace('D#', ''), lin_start, col))
            for i in token_lexeme:
                if i == '\n':
                    lin_start += 1
        else:
            t += token_lexeme
    segment.append(('TEXT', t, 0, 0))
    return segment


if __name__ == '__main__':
    for i in segments('test.q'):
        print(i)
