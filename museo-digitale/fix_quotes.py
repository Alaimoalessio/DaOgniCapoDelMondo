import os
import re
from translate_the_rest import files_replacements

for file_path, sentences in files_replacements.items():
    if not os.path.exists(file_path):
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for sentence in sentences:
        # The bad string I inserted was EXACTLY: f"{{{{ _('{sentence}') }}}}"
        # Where sentence might have contained unescaped quotes!
        bad_string = f"{{{{ _('{sentence}') }}}}"
        
        # We want to replace it with a properly escaped one. 
        # Best approach for jinja strings with mixed quotes is using double quotes for outer, 
        # and escape inner double quotes.
        safe_sentence = sentence.replace('"', '\\"')
        good_string = f'{{{{ _("{safe_sentence}") }}}}'
        
        content = content.replace(bad_string, good_string)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed Jinja templates quotes!")
