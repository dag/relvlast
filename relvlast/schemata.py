from flatland       import Form, String, List


class Page(Form):

    title = String
    body  = String


class Word(Form):

    id = String
    type = String
    class_ = String
    affixes = List.of(String).using(optional=True)
    definition = String
    notes = String
