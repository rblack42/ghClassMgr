# -*- coding: utf-8 -*-
"""
    Pylit Include Directive
    ~~~~~~~~~~~~~~~~~~~~~~~

    Adapted from SPhinx code.py LiteralInclude directive
    by Roie R. Black

    :copyright: Copyright 2016 by Roie R. Black (modifications only)
    :original copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import sys
import codecs
from difflib import unified_diff

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList

from six import string_types

from sphinx import addnodes
from sphinx.util import parselinenos
from sphinx.util.nodes import set_source_info

from sh import git

def dedent_lines(lines, dedent):
    if not dedent:
        return lines

    new_lines = []
    for line in lines:
        new_line = line[dedent:]
        if line.endswith('\n') and not new_line:
            new_line = '\n'  # keep CRLF
        new_lines.append(new_line)

    return new_lines


def container_wrapper(directive, literal_node, caption):
    container_node = nodes.container('', literal_block=True,
                                     classes=['literal-block-wrapper'])
    parsed = nodes.Element()
    directive.state.nested_parse(ViewList([caption], source=''),
                                 directive.content_offset, parsed)
    caption_node = nodes.caption(parsed[0].rawsource, '',
                                 *parsed[0].children)
    caption_node.source = parsed[0].source
    caption_node.line = parsed[0].line
    container_node += caption_node
    container_node += literal_node
    return container_node

class pylit_node(nodes.General, nodes.Element):
    pass


class PylitInclude(Directive):
    """
    Like ``.. include:: :literal:``, but only warns if the include file is
    not found, and does not raise errors.  Also has several options for
    selecting what to include.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'dedent': int,
        'linenos': directives.flag,
        'lineno-start': int,
        'lineno-match': directives.flag,
        'tab-width': int,
        'language': directives.unchanged_required,
        'encoding': directives.encoding,
        'pyobject': directives.unchanged_required,
        'lines': directives.unchanged_required,
        'start-after': directives.unchanged_required,
        'end-before': directives.unchanged_required,
        'prepend': directives.unchanged_required,
        'append': directives.unchanged_required,
        'emphasize-lines': directives.unchanged_required,
        'caption': directives.unchanged,
        'class': directives.class_option,
        'name': directives.unchanged,
        'diff': directives.unchanged_required,
        'branch': directives.unchanged_required,
    }

    def read_with_encoding(self, filename, document, codec_info, encoding):
        f = None
        try:
            if 'branch' in self.options:
                self.checkout = self.options.get('branch')
                os.chdir(self.code_base)
                print "\nChecking out branch:",self.checkout
                git.checkout(self.checkout)
            f = codecs.StreamReaderWriter(open(filename, 'rb'), codec_info[2],
                                          codec_info[3], 'strict')
            lines = f.readlines()
            git.checkout(self.current_branch)
            os.chdir(self.current_dir)
            lines = dedent_lines(lines, self.options.get('dedent'))
            return lines
        except (IOError, OSError):
            return [document.reporter.warning(
                'Include file %r not found or reading it failed' % filename,
                line=self.lineno)]
        except UnicodeError:
            return [document.reporter.warning(
                'Encoding %r used for reading included file %r seems to '
                'be wrong, try giving an :encoding: option' %
                (encoding, filename))]
        finally:
            if f is not None:
                f.close()

    def run(self):
        document = self.state.document
        if not document.settings.file_insertion_enabled:
            return [document.reporter.warning('File insertion disabled',
                                              line=self.lineno)]
        env = document.settings.env
        #rel_filename, filename = env.relfn2path(self.arguments[0])
        self.code_base = env.config.code_base
        file_name = self.arguments[0]
        if file_name.startswith('/'):
            file_name = file_name[1:]
        filename = os.path.join(self.code_base,file_name)
        rel_filename = os.path.join('../code',file_name)
        print "\nrel:", filename, rel_filename

        # record current branch
        self.current_dir = os.getcwd()
        print "Switching to code dir:", self.code_base
        os.chdir(self.code_base)
        self.current_branch = git('symbolic-ref', '--short', 'HEAD')
        print "current branch", self.current_branch
        self.checkout = self.current_branch
        print "Switching to doc dir:", self.current_dir
        os.chdir(self.current_dir)


        if 'pyobject' in self.options and 'lines' in self.options:
            return [document.reporter.warning(
                'Cannot use both "pyobject" and "lines" options',
                line=self.lineno)]

        if 'lineno-match' in self.options and 'lineno-start' in self.options:
            return [document.reporter.warning(
                'Cannot use both "lineno-match" and "lineno-start"',
                line=self.lineno)]

        if 'lineno-match' in self.options and \
           (set(['append', 'prepend']) & set(self.options.keys())):
            return [document.reporter.warning(
                'Cannot use "lineno-match" and "append" or "prepend"',
                line=self.lineno)]

        encoding = self.options.get('encoding', env.config.source_encoding)
        codec_info = codecs.lookup(encoding)

        lines = self.read_with_encoding(filename, document,
                                        codec_info, encoding)
        if lines and not isinstance(lines[0], string_types):
            return lines

        diffsource = self.options.get('diff')
        if diffsource is not None:
            tmp, fulldiffsource = env.relfn2path(diffsource)

            difflines = self.read_with_encoding(fulldiffsource, document,
                                                codec_info, encoding)
            if not isinstance(difflines[0], string_types):
                return difflines
            diff = unified_diff(
                difflines,
                lines,
                diffsource,
                self.arguments[0])
            lines = list(diff)

        linenostart = self.options.get('lineno-start', 1)
        objectname = self.options.get('pyobject')
        if objectname is not None:
            from sphinx.pycode import ModuleAnalyzer
            analyzer = ModuleAnalyzer.for_file(filename, '')
            tags = analyzer.find_tags()
            if objectname not in tags:
                return [document.reporter.warning(
                    'Object named %r not found in include file %r' %
                    (objectname, filename), line=self.lineno)]
            else:
                lines = lines[tags[objectname][1]-1: tags[objectname][2]-1]
                if 'lineno-match' in self.options:
                    linenostart = tags[objectname][1]

        linespec = self.options.get('lines')
        if linespec:
            try:
                linelist = parselinenos(linespec, len(lines))
            except ValueError as err:
                return [document.reporter.warning(str(err), line=self.lineno)]

            if 'lineno-match' in self.options:
                # make sure the line list is not "disjoint".
                previous = linelist[0]
                for line_number in linelist[1:]:
                    if line_number == previous + 1:
                        previous = line_number
                        continue
                    return [document.reporter.warning(
                        'Cannot use "lineno-match" with a disjoint set of '
                        '"lines"', line=self.lineno)]
                linenostart = linelist[0] + 1
            # just ignore non-existing lines
            lines = [lines[i] for i in linelist if i < len(lines)]
            if not lines:
                return [document.reporter.warning(
                    'Line spec %r: no lines pulled from include file %r' %
                    (linespec, filename), line=self.lineno)]

        linespec = self.options.get('emphasize-lines')
        if linespec:
            try:
                hl_lines = [x+1 for x in parselinenos(linespec, len(lines))]
            except ValueError as err:
                return [document.reporter.warning(str(err), line=self.lineno)]
        else:
            hl_lines = None

        startafter = self.options.get('start-after')
        endbefore = self.options.get('end-before')
        if startafter is not None or endbefore is not None:
            use = not startafter
            res = []
            for line_number, line in enumerate(lines):
                if not use and startafter and startafter in line:
                    if 'lineno-match' in self.options:
                        linenostart += line_number + 1
                    use = True
                elif use and endbefore and endbefore in line:
                    break
                elif use:
                    res.append(line)
            lines = res

        prepend = self.options.get('prepend')
        if prepend:
            lines.insert(0, prepend + '\n')

        append = self.options.get('append')
        if append:
            lines.append(append + '\n')

        text = ''.join(lines)
        if self.options.get('tab-width'):
            text = text.expandtabs(self.options['tab-width'])
        retnode = nodes.literal_block(text, text, source=filename)
        set_source_info(self, retnode)
        if diffsource:  # if diff is set, set udiff
            retnode['language'] = 'udiff'
        if 'language' in self.options:
            retnode['language'] = self.options['language']
        retnode['linenos'] = 'linenos' in self.options or \
                             'lineno-start' in self.options or \
                             'lineno-match' in self.options
        retnode['classes'] += self.options.get('class', [])
        extra_args = retnode['highlight_args'] = {}
        if hl_lines is not None:
            extra_args['hl_lines'] = hl_lines
        extra_args['linenostart'] = linenostart
        env.note_dependency(rel_filename)

        caption = self.options.get('caption')
        if caption is not None:
            if not caption:
                caption = self.arguments[0]
            target = "("+self.checkout+")"+nodes.fully_normalize_name(caption)
            print "Target:",target

            self.options.setdefault('name', target)
            retnode = container_wrapper(self, retnode, caption)

        # retnode will be note_implicit_target that is linked from caption and numref.
        # when options['name'] is provided, it should be primary ID.
        self.add_name(retnode)

        return [retnode]

def html_visit_pylit(self, node):
    code = node['code']
    if node.has_key('language'):
        node_lang = node['language']
    else:
        node_lang = 'python'
    # hilight this code with pygments
    lexer = get_lexer_by_name(node_lang)
    starttag = self.starttag(node, 'div', suffix='',
            CLASS='highlight-%s' % node_lang)
    hlsource = highlight(code,lexer, HtmlFormatter())
    self.body.append(starttag + hlsource + '</div>\n')
    raise nodes.SkipNode

def setup(app):
    app.add_config_value('code_base','.','html')
    app.add_node(pylit_node,
            html = (html_visit_pylit, None)
    )
    app.add_directive('pylitinclude', PylitInclude)
