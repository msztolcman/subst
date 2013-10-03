subst
=====

`subst` is simple utility to replace one string into another in given list of files.

But why?
--------

1. There is `sed` for example?

    Yes, it is. But `sed` use regexps engine called "Basic Regular Expressions", or "Extended
    Regular Expression". PCRE is much more widely used dialect.

2. So I can use Perl!

    Of course you can. But not everyone know how to use Perl. I know, but `subst` is IMHO
    simpler to use.

OK, so how to use it?
---------------------

Simple
------

    echo 'Hello World!' | subst -s 's/Hello/Hi/' -

or:

    subst -p '(192\.168)\.1\.(10)' -r '\1.0.\2' /etc/hosts

More
----

Everything is in help :) Just execute:

    python subst --help

Look at result:

    % python subst --help
    usage: subst [-h] [-p PATTERN] [-r REPLACE] [--eval-replace] [-t STRING]
                    [-s "s/PAT/REP/gixsm"] [-c COUNT] [-l] [-i]
                    [--pattern-dot-all] [--pattern-verbose] [--pattern-multiline]
                    [-b] [-e EXT] [--stdin] [--stdout] [--verbose] [--debug] [-v]
                    [files [files ...]]

    Replace PATTERN with REPLACE in many files.

    positional arguments:
    files                 file to parse.

    optional arguments:
    -h, --help            show this help message and exit
    -p PATTERN, --pattern PATTERN
                          pattern to replace for. Supersede
                          --pattern_and_replace. Required if --replace is
                          specified.
    -r REPLACE, --replace REPLACE
                          replacement. Supersede --pattern_and_replace. Required
                          if --pattern is specified.
    --eval-replace        if specified, make eval data from --replace(should be
                          valid Python code). Ignored with --pattern_and_replace
                          argument.
    -t STRING, --string STRING
                          if specified, treats --pattern as string, not as
                          regular expression. Ignored with --pattern_and_replace
                          argument.
    -s "s/PAT/REP/gixsm", --pattern_and_replace "s/PAT/REP/gixsm"
                          pattern and replacement in one:
                          s/pattern/replace/g(pattern is always regular
                          expression, /g is optional and stands for --count=0,
                          /i == --ignore-case, /s == --pattern-dot-all, /m ==
                          --pattern-multiline).
    -c COUNT, --count COUNT
                          make COUNT replacements for every file(0 make
                          unlimited changes, default).
    -l, --linear          apply pattern for every line separately. Without this
                          flag whole file is read into memory.
    -i, --ignore-case     ignore case of characters when matching
    --pattern-dot-all     with this flag, dot(.) character in pattern match also
                          new line character (see:
                          http://docs.python.org/2/library/re.html#re.DOTALL).
    --pattern-verbose     with this flag pattern can be passed as verbose(see:
                          http://docs.python.org/2/library/re.html#re.VERBOSE).
    --pattern-multiline   with this flag pattern can be passed as multiline(see:
                          http://docs.python.org/2/library/re.html#re.MULTILINE).
    -b, --no-backup       disable creating backup of modified files.
    -e EXT, --backup-extension EXT
                          extension for backuped files(ignore if no backup is
                          created), without leading dot. Defaults to: "bak".
    --stdin               read data from STDIN(implies --stdout)
    --stdout              output data to STDOUT instead of change files in-
                          place(implies --no-backup)
    --verbose             show files and how many replacements was done
    --debug               show more infos
    -v, --version         show version and exit

    Miscellaneous notes:
    * regular expressions engine used here is PCRE, dialect from Python
    * is required to pass either --pattern and -replace, or
    --pattern_and_replace argument
    * if pattern passed to --pattern_and_replace has /g modifier, it
    overwrites --count value
    * if neither /g modifier nor --count argument is passed, assume that
    --count is equal 1
    * if only --count is given, this value is used
    * if --eval-replace is given, --replace must be valid Python code, where
    can be used m variable.m holds MatchObject instance (see:
    http://http://docs.python.org/2/library/re.html#match-objects, for
    example:
        --eval-replace --replace 'm.group(1).lower()'
    * regular expressions with non linear search read whole file to yours
    computer memory - if file size is bigger then you have memory in your
    computer, it fails
    * parsing expression passed to --pattern_and_replace argument is very
    simple - if you use / as delimiter, then in your expression can't be
    used this character anymore. If you need to use same character as
    delimiter and in expression, then better use --pattern and --replace
    argument

    Security notes:
    * be carefull with --eval-replace argument. When it's given, value
    passed to --replace is eval-ed, so any not safe code will be executed!

Some examples?
--------------

Simple replace word 'Hello' with 'Hi' in data read from STDIN:

    echo 'Hello World!' | subst -s 's/Hello/Hi/' -

Replace every IP address in form: 192.168.1.X (where X is few digits - single octet)
with 192.168.0.X in `/etc/hosts`:

    subst -p '(192\.168)\.1\.(10)' -r '\1.0.\2' /etc/hosts

License
=======

MIT: http://opensource.org/licenses/MIT

Author
======

Marcin Sztolcman <marcin@urzenia.net>

Links
=====

* HomePage: https://mysz.github.io/subst
* Issues:   https://github.com/mysz/subst/issues

