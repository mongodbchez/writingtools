# writingtools

This has two scripts, one for backporting and one for converting legacy YAML step files into step directives.

Prereqs:
- Python 3.9.1 (I'd recommend using pyenv)

Backport script:
john.williams probably has the most context on this. The script can handle multiple backports. It asks for the parent ticket (the ticket being backported from), 
the child ticket(s) (the ticket(s) being backported to), and the versions to backport to. John has a pull request again this

yamlconverter: see initial commmit message for details on how to use
