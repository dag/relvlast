from flatland import Form, String, List


TextInput = String.with_properties(template='forms/text-input.html')
CreoleInput = String.with_properties(template='forms/creole-input.html')
CreoleArea = String.with_properties(template='forms/creole-area.html')


class Page(Form):

    title = TextInput
    body  = CreoleArea


class Word(Form):

    id = TextInput
    type = TextInput
    class_ = TextInput
    affixes = List.of(String).using(optional=True)
    definition = CreoleInput
    notes = CreoleInput
