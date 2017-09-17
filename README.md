subst
=====

`subst` is simple utility to replace one string into another in given list of files.

If you like this tool, just [say thanks](https://saythanks.io/to/msztolcman).

Current stable version
----------------------

0.4.0

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

    subst --help

Look at result:

    % subst --help
    usage: subst.py [-h] [-p PATTERN] [-r REPLACE] [--eval-replace] [-t]
                    [-s "s/PAT/REP/gixsm"] [-c COUNT] [-l] [-i]
                    [--pattern-dot-all] [--pattern-verbose] [--pattern-multiline]
                    [-u] [--encoding-input ENCODING_INPUT]
                    [--encoding-file ENCODING_FILE]
                    [--encoding-filesystem ENCODING_FILESYSTEM] [-b] [-e EXT]
                    [--stdin] [--stdout] [--verbose] [--debug] [-v]
                    [files [files ...]]
    
    Replace PATTERN with REPLACE in many files.
    
    positional arguments:
    files                 files to parse
    
    optional arguments:
    -h, --help            show this help message and exit
    -p PATTERN, --pattern PATTERN
                            pattern to replace for. Supersede --pattern-and-
                            replace. Required if --replace is specified.
    -r REPLACE, --replace REPLACE
                            replacement. Supersede --pattern-and-replace. Required
                            if --pattern is specified.
    --eval-replace        if specified, make eval data from --replace(should be
                            valid Python code). Ignored with --pattern-and-replace
                            argument.
    -t, --string          if specified, treats --pattern as string, not as
                            regular expression. Ignored with --pattern-and-replace
                            argument.
    -s "s/PAT/REP/gixsm", --pattern-and-replace "s/PAT/REP/gixsm", --pattern-and-replace "s/PAT/REP/gixsm"
                            pattern and replacement in one:
                            s/pattern/replace/g(pattern is always regular
                            expression, /g is optional and stands for --count=0,
                            /i == --ignore-case, /s == --pattern-dot-all, /m ==
                            --pattern-multiline).
    -c COUNT, --count COUNT
                            make COUNT replacements for every file (0 makes
                            unlimited changes, default).
    -l, --linear          apply pattern for every line separately. Without this
                            flag whole file is read into memory.
    -i, --ignore-case     ignore case of characters when matching
    --pattern-dot-all     with this flag, dot(.) character in pattern match also
                            new line character (see:
                            https://docs.python.org/3/library/re.html#re.DOTALL).
    --pattern-verbose     with this flag pattern can be passed as verbose(see:
                            https://docs.python.org/3/library/re.html#re.VERBOSE).
    --pattern-multiline   with this flag pattern can be passed as multiline(see:
                            https://docs.python.org/3/library/re.html#re.MULTILINE
                            ).
    -u, --utf8            Use UTF-8 in --encoding-input, --encoding-file and
                            --encoding-filesystem
    --encoding-input ENCODING_INPUT
                            set encoding for parameters like --pattern etc
                            (default for your system: ascii)
    --encoding-file ENCODING_FILE
                            set encoding for content of processed files (default
                            for your system: ascii)
    --encoding-filesystem ENCODING_FILESYSTEM
                            set encoding for paths and filenames (default for your
                            system: utf-8)
    -b, --no-backup       don't create backup of modified files.
    -e EXT, --backup-extension EXT
                            extension for backup files(ignore if no backup is
                            created), without leading dot. Defaults to: "bak".
    --stdin               read data from STDIN(implies --stdout)
    --stdout              output data to STDOUT instead of change files in-
                            place(implies --no-backup)
    --verbose             show files and how many replacements was done and
                            short summary
    --debug               show more informations
    -v, --version         show program's version number and exit
    
    Miscellaneous notes:
    * regular expressions engine used here is PCRE, dialect from Python
    * is required to pass either --pattern and -replace, or --pattern-and-
    replace argument
    * if pattern passed to --pattern-and-replace has /g modifier, it
    overwrites --count value
    * if neither /g modifier nor --count argument is passed, assume that
    --count is equal 1
    * if only --count is given, this value is used
    * if --eval-replace is given, --replace must be valid Python code, where
    can be used m variable. m holds MatchObject instance (see:
    https://docs.python.org/3/library/re.html#match-objects, for example:
        --eval-replace --replace 'm.group(1).lower()'
    * regular expressions with non linear search read whole file to yours
    computer memory - if file size is bigger then you have memory in your
    computer, it fails
    * parsing expression passed to --pattern-and-replace argument is very
    simple - if you use / as delimiter, then in your expression can't be
    used this character anymore. If you need to use same character as
    delimiter and in expression, then better use --pattern and --replace
    arguments
    * you can test exit code to verify there was made any changes (exit code
    = 0) or not (exit code = 1)
    
    Security notes:
    * be careful with --eval-replace argument. When it's given, value passed
    to --replace is eval-ed, so any unsafe code will be executed!
    
    Author:
    Marcin Sztolcman <marcin@urzenia.net> // http://urzenia.net
    
    HomePage:
    http://msztolcman.github.io/subst/

Some examples?
--------------

Simple replace word 'Hello' with 'Hi' in data read from STDIN:

    echo 'Hello World!' | subst -s 's/Hello/Hi/' -

Replace every IP address in form: 192.168.1.X (where X is few digits - single octet)
with 192.168.0.X in `/etc/hosts`:

    subst -p '(192\.168)\.1\.(10)' -r '\1.0.\2' /etc/hosts

Installation
------------

`subst` should work on any platform where [Python](http://python.org) is available,
it means Linux, Windows, MacOS X etc. There is no dependencies, plain Python power :)

1. Installtion using PIP

Simplest way is to use Python's built-in package system:

    pip install subst

2. Using sources

To install, go to [GitHub releases](https://github.com/msztolcman/subst/releases),
download newest release, unpack and put somewhere in `PATH` (ie. `~/bin`
or `/usr/local/bin`).

If You want to install newest unstable version, then just copy file to your PATH,
for example:

    curl https://raw.github.com/msztolcman/subst/master/subst.py > /usr/local/bin/subst

or:

    wget https://raw.github.com/msztolcman/subst/master/subst.py -O /usr/local/bin/subst

Voila!

Authors
-------

Marcin Sztolcman <marcin@urzenia.net>

Contact
-------

If you like or dislike this software, please do not hesitate to tell me about this me via email (marcin@urzenia.net).

If you find bug or have an idea to enhance this tool, please use GitHub's [issues](https://github.com/msztolcman/subst/issues).

License
-------

The MIT License (MIT)

Copyright (c) 2013 Marcin Sztolcman

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ChangeLog
---------

### coming

* improvements to handling different encodings
* exit code give us info about there was any changes
* improvements to pylintrc, Makefile
* config for tox
* fixes and improvements in built-in help
* fixed but with changing new-line characters from dos to unix (issue #5)
* fixed bug with bad interpretation of -t param (issue #4)
* fixed bug with using subst on Windows (issue #2)
* many refactorings
* marked as compatible with Python 3.5 and 3.6

### v0.4.0

* PEP8 improvements (coding style)
* Makefile added
* improved pylintrc

### v0.3.1

* prepared and uploaded to PYPI
* typos and editorials

### v0.3

* better handling of non-ascii encoding in files, patterns etc
* higher priority for --pattern-* switches then modifiers in --pattern-and-replace
* unified switches syntax (was --pattern_and_replace, but other switches used dashes)
* pep8
* typos and editorials

### v0.2

* second public version
