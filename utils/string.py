from re import sub


def to_snake_case(value):
    if value in (None, ''):
        return ''
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                value.replace('-', ' '))).split()).lower()
