import re

__all__ = ['parse_search_query']


def parse_search_query(q: str) -> str:
    """Parse a query to raw tsquery format, with some desirable properties.

    Postgres provides a few built-in ways to parse user input to a tsquery:

      - plainto_tsquery: each keyword is connected by an AND (&)
      - phraseto_tsquery: each keyword is connected by a FOLLOWED BY (<->)
      - websearch_to_tsquery: unquoted terms are connected by AND,
                              quoted terms are connected by FOLLOWED BY,
                              the word "or" becomes the OR operator (|),
                              and dashes "-" become the negation operator (!)

    The power of websearch_to_tsquery is very handy, but due to how the "english"
    config parses the lexemes and stems of words, a query like "gold" won't
    match "golden". Because this can be surprising behaviour, it would be nice
    if unquoted terms perform a prefix search (term:*).

    This parser performs much of the same function as websearch_to_tsquery,
    with the one deviation being unquoted terms translated to prefix searches.

    >>> parse_search_query('t')
    't:*'
    >>> parse_search_query('to')
    'to:*'
    >>> parse_search_query('to blathe')
    'to:* & blathe:*'
    >>> parse_search_query('"twue wub"')
    "( 'twue' <-> 'wub' )"
    >>> parse_search_query('-"twue wub"')
    "!( 'twue' <-> 'wub' )"
    >>> parse_search_query('you or me')
    'you:* | me:*'
    """
    is_negated = False
    is_or_join = False
    parts = []

    def add_part(part: str) -> None:
        nonlocal is_negated, is_or_join

        if parts:
            parts.append('|' if is_or_join else '&')
            is_or_join = False

        if is_negated:
            part = '!' + part
            is_negated = False
        parts.append(part)

    def escape_word(word: str) -> str:
        """Remove tsquery operators from a word"""
        return re.sub(r'[()\'"&|]|<->', '', word)

    i = 0
    while i < len(q):
        c = q[i]
        if c == '"':
            i += 1

            if (quoted_len := q[i + 1:].find('"')) != -1:
                quoted = q[i:i + quoted_len + 1]
                i += quoted_len + 1

                words = quoted.split()
                escaped_words = [f"'{escape_word(word)}'" for word in words]
                add_part(f'( {" <-> ".join(escaped_words)} )')

        elif c == ' ':
            i += 1
            continue

        elif c == '-':
            i += 1
            is_negated = True

        else:
            word = q[i:]
            if (word_len := word.find(' ')) != -1:
                word = word[:word_len]
            i += len(word)

            if word.lower() == 'or':
                is_or_join = True
            else:
                add_part(f"{escape_word(word)}:*")

    return ' '.join(parts)
