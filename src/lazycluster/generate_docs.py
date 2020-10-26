"""
Parses source code to generate API docs in markdown.
"""

import inspect
import os
import re
import sys
from inspect import getdoc, getsourcefile, getsourcelines, getmembers
from importlib import reload

if sys.version[0] == "2":
    reload(sys)
    sys.setdefaultencoding("utf8")

_RE_BLOCKSTART_LIST = re.compile(
    r"(Args:|Arg:|Arguments:|Parameters:|Kwargs:|Attributes:|Returns:|Yields:|Kwargs:|Raises:).{0,2}$",
    re.IGNORECASE,
)

_RE_BLOCKSTART_TEXT = re.compile(
    r"(Notes:|Note:|Examples:|Example:|Todo:).{0,2}$", re.IGNORECASE
)

_RE_TYPED_ARGSTART = re.compile(r"([\w\[\]_]{1,}?)\s*?\((.*?)\):(.{2,})", re.IGNORECASE)
_RE_ARGSTART = re.compile(r"(.{1,}?):(.{2,})", re.IGNORECASE)

#
# String templates
#

FUNC_TEMPLATE = """-------------------
<a href="{path}"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

{section} <kbd>{func_type}</kbd> `{header}`

```python
{funcdef}
```
{doc}
"""


CLASS_TEMPLATE = """-------------------
<a href="{path}"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

{section} <kbd>class</kbd> `{header}`
{doc}
{variables}
{init}
{handlers}
{methods}
"""

MODULE_TEMPLATE = """
<a href="{path}"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

{section} <kbd>module</kbd> `{header}`
{doc}
{global_vars}
{functions}
{classes}
"""


def get_function_signature(
    function,
    owner_class=None,
    show_module=False,
    ignore_self=False,
    wrap_arguments=False,
    remove_package=False,
):
    isclass = inspect.isclass(function)

    # Get base name.
    name_parts = []
    if show_module:
        name_parts.append(function.__module__)
    if owner_class:
        name_parts.append(owner_class.__name__)
    if hasattr(function, "__name__"):
        name_parts.append(function.__name__)
    else:
        name_parts.append(type(function).__name__)
        name_parts.append("__call__")
        function = function.__call__
    name = ".".join(name_parts)

    if isclass:
        function = getattr(function, "__init__", None)

    arguments = []
    return_type = ""
    if hasattr(inspect, "signature"):
        parameters = inspect.signature(function).parameters
        if inspect.signature(function).return_annotation != inspect._empty:
            return_type = str(inspect.signature(function).return_annotation)
            if return_type.startswith("<class"):
                # Base class -> get real name
                try:
                    return_type = inspect.signature(function).return_annotation.__name__
                except Exception:
                    pass
            return_type = return_type.lstrip("typing.")

        for parameter in parameters:
            argument = str(parameters[parameter])
            if ignore_self and argument == "self":
                # Ignore self
                continue
            # Reintroduce Optionals
            argument = re.sub(r"Union\[(.*?), NoneType\]", r"Optional[\1]", argument)
            arguments.append(argument)
    else:
        print("Seems like function " + name + " does not have any signature")

    signature = name + "("
    if wrap_arguments:
        for i, arg in enumerate(arguments):
            signature += "\n    " + arg

            if i is not len(arguments) - 1:
                signature += ","
            else:
                signature += "\n"
    else:
        signature += ", ".join(arguments)

    signature += ")" + ((" → " + return_type) if return_type else "")

    if remove_package:
        # Remove all package path from signature
        signature = re.sub(r"([a-zA-Z0-9_]*?\.)", "", signature)
    return signature


def make_iter(obj):
    """ Makes an iterable
    """
    return obj if hasattr(obj, "__iter__") else [obj]


def order_by_line_nos(objs, line_nos):
    """Orders the set of `objs` by `line_nos`
    """
    ordering = sorted(range(len(line_nos)), key=line_nos.__getitem__)
    return [objs[i] for i in ordering]


def to_md_file(string, filename, out_path="."):
    """Import a module path and create an api doc from it
    Args:
        string (str): string with line breaks to write to file.
        filename (str): filename without the .md
        out_path (str): The output directory
    """
    md_file = "%s.md" % filename
    with open(os.path.join(out_path, md_file), "w") as f:
        f.write(string)
    print("wrote {}.".format(md_file))


def modules2mdfiles():
    # TODO
    pass


def code_snippet(snippet):
    result = "```python\n"
    result += snippet + "\n"
    result += "```\n"
    return result


def _get_class_that_defined_method(meth):
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(
            inspect.getmodule(meth),
            meth.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0],
        )
        if isinstance(cls, type):
            return cls
    return getattr(meth, "__objclass__", None)  # handle special descriptor objects


class MarkdownAPIGenerator(object):
    def __init__(self, src_root, github_link, remove_package_path: bool = False):
        """Initializes the markdown api generator.
        Args:
            src_root: The root folder name containing all the sources.
                Ex: src
            github_link: The base github link. Should include branch name.
                All source links are generated with this prefix.
        """
        self.src_root = src_root
        self.github_link = github_link
        self.remove_package_path = remove_package_path

    def get_line_no(self, obj):
        """Gets the source line number of this object. None if `obj` code cannot be found.
        """
        try:
            lineno = getsourcelines(obj)[1]
        except Exception:
            # no code found
            lineno = None
        return lineno

    def get_src_path(self, obj, append_base=True):
        """Creates a src path string with line info for use as markdown link.
        """
        path = getsourcefile(obj)
        if not self.src_root in path:
            # this can happen with e.g.
            # inlinefunc-wrapped functions
            if hasattr(obj, "__module__"):
                path = "%s.%s" % (obj.__module__, obj.__name__)
            else:
                path = obj.__name__
            path = path.replace(".", "/")
        print(path)
        pre, post = path.rsplit(self.src_root + "/", 1)

        lineno = self.get_line_no(obj)
        lineno = "" if lineno is None else "#L{}".format(lineno)

        path = self.src_root + "/" + post + lineno
        if append_base:
            path = os.path.join(self.github_link, path)
        return path

    def doc2md(self, func):
        """Parse docstring (parsed with getdoc) according to Google-style
        formatting and convert to markdown. We support the following
        Google style syntax:
        Args, Kwargs:
            argname (type): text
            freeform text
        Returns, Yields:
            retname (type): text
            freeform text
        Raises:
            exceptiontype: text
            freeform text
        Notes, Examples:
            freeform text
        """
        # The specfication of Inspect#getdoc() was changed since version 3.5,
        # the documentation strings are now inherited if not overridden.
        # For details see: https://docs.python.org/3.6/library/inspect.html#inspect.getdoc
        # doc = getdoc(func) or ""
        doc = "" if func.__doc__ is None else getdoc(func) or ""

        blockindent = 0
        argindent = 1
        out = []
        arg_list = False
        literal_block = False

        for line in doc.split("\n"):
            indent = len(line) - len(line.lstrip())
            line = line.lstrip()
            if line.startswith(">>>"):
                # support for doctest
                line = line.replace(">>>", "```") + "```"

            if _RE_BLOCKSTART_LIST.match(line) or _RE_BLOCKSTART_TEXT.match(line):
                # start of a new block
                blockindent = indent

                if literal_block:
                    # break literal block
                    out.append("```\n")
                    literal_block = False

                out.append("\n**{}**\n".format(line.strip()))

                if _RE_BLOCKSTART_LIST.match(line):
                    arg_list = True
                else:
                    arg_list = False
            elif line.strip().endswith("::"):
                # Literal Block Support: https://docutils.sourceforge.io/docs/user/rst/quickref.html#literal-blocks
                literal_block = True
                out.append(line.replace("::", ":\n```"))
            elif indent > blockindent:
                if arg_list and not literal_block and _RE_TYPED_ARGSTART.match(line):
                    # start of new argument
                    out.append(
                        "\n"
                        + " " * blockindent
                        + " - "
                        + _RE_TYPED_ARGSTART.sub(r"<b>`\1`</b> (\2): \3", line)
                    )
                    argindent = indent
                elif arg_list and not literal_block and _RE_ARGSTART.match(line):
                    # start of an exception-type block
                    out.append(
                        "\n"
                        + " " * blockindent
                        + " - "
                        + _RE_ARGSTART.sub(r"<b>`\1`</b>: \2", line)
                    )
                    argindent = indent
                elif indent > argindent:
                    # attach docs text of argument
                    # * (blockindent + 2)
                    out.append(" " + line)
                else:
                    out.append(line)
            else:
                if line.strip() and literal_block:
                    # indent has changed, if not empty line, break literal block
                    line = "```\n" + line
                    literal_block = False
                out.append(line)

            out.append("\n")

        return "".join(out)

    def func2md(self, func, clsname="", depth=3):
        """Takes a function (or method) and documents it.
        Args:
            clsname (str, optional): class name to prepend to funcname.
            depth (int, optional): number of ### to append to function name
        """
        section = "#" * depth
        funcname = func.__name__
        escfuncname = (
            "%s" % funcname if funcname.startswith("_") else funcname
        )  # "`%s`"
        header = "%s%s" % ("%s." % clsname if clsname else "", escfuncname)

        path = self.get_src_path(func)
        doc = self.doc2md(func)

        funcdef = get_function_signature(
            func, ignore_self=True, remove_package=self.remove_package_path
        )

        # split the function definition if it is too long
        lmax = 80
        if len(funcdef) > lmax:
            funcdef = get_function_signature(
                func,
                ignore_self=True,
                wrap_arguments=True,
                remove_package=self.remove_package_path,
            )

        if inspect.ismethod(func):
            func_type = "classmethod"
        else:
            if _get_class_that_defined_method(func) is None:
                func_type = "function"
            else:
                # function of a class
                func_type = "method"

        # build the signature
        string = FUNC_TEMPLATE.format(
            section=section,
            header=header,
            funcdef=funcdef,
            path=path,
            func_type=func_type,
            doc=doc if doc else "*No documentation found.*",
        )
        return string

    def class2md(self, cls, depth=2):
        """Takes a class and creates markdown text to document its methods and variables.
        """

        section = "#" * depth
        subsection = "#" * (depth + 2)
        clsname = cls.__name__
        modname = cls.__module__
        header = clsname
        path = self.get_src_path(cls)
        doc = self.doc2md(cls)

        try:
            init = self.func2md(cls.__init__, clsname=clsname)
        except (ValueError, TypeError):
            # this happens if __init__ is outside the repo
            init = ""

        variables = []
        for name, obj in getmembers(
            cls, lambda a: not (inspect.isroutine(a) or inspect.ismethod(a))
        ):
            if not name.startswith("_") and type(obj) == property:
                comments = self.doc2md(obj) or inspect.getcomments(obj)
                comments = "\n %s" % comments if comments else ""
                variables.append(
                    "\n%s <kbd>property</kbd> %s.%s%s\n"
                    % (subsection, clsname, name, comments)
                )

        handlers = []
        for name, obj in getmembers(cls, inspect.ismethoddescriptor):
            if not name.startswith("_") and hasattr(
                obj, "__module__"
            ):  # and obj.__module__ == modname:
                handlers.append(
                    "\n%s <kbd>handler</kbd> %s.%s\n" % (subsection, clsname, name)
                )

        methods = []
        # for name, obj in getmembers(cls, inspect.isfunction):
        for name, obj in getmembers(
            cls, lambda a: inspect.ismethod(a) or inspect.isfunction(a)
        ):
            if (
                not name.startswith("_")
                and hasattr(obj, "__module__")
                and name not in handlers
            ):  # and obj.__module__ == modname and :
                methods.append(self.func2md(obj, clsname=clsname, depth=depth + 1))

        string = CLASS_TEMPLATE.format(
            section=section,
            header=header,
            path=path,
            doc=doc if doc else "",
            init=init,
            variables="".join(variables),
            handlers="".join(handlers),
            methods="".join(methods),
        )
        return string

    def module2md(self, module):
        """Takes an imported module object and create a Markdown string containing functions and classes.
        """
        modname = module.__name__
        doc = self.doc2md(module)
        path = self.get_src_path(module, append_base=False)
        path = os.path.join(self.github_link, path)
        found = []

        classes = []
        line_nos = []
        for name, obj in getmembers(module, inspect.isclass):
            # handle classes
            found.append(name)
            if (
                not name.startswith("_")
                and hasattr(obj, "__module__")
                and obj.__module__ == modname
            ):
                classes.append(self.class2md(obj))
                line_nos.append(self.get_line_no(obj) or 0)
        classes = order_by_line_nos(classes, line_nos)

        functions = []
        line_nos = []
        for name, obj in getmembers(module, inspect.isfunction):
            # handle functions
            found.append(name)
            if (
                not name.startswith("_")
                and hasattr(obj, "__module__")
                and obj.__module__ == modname
            ):
                functions.append(self.func2md(obj))
                line_nos.append(self.get_line_no(obj) or 0)
        functions = order_by_line_nos(functions, line_nos)

        variables = []
        line_nos = []
        for name, obj in module.__dict__.items():
            if not name.startswith("_") and name not in found:
                if hasattr(obj, "__module__") and obj.__module__ != modname:
                    continue
                if hasattr(obj, "__name__") and not obj.__name__.startswith(modname):
                    continue
                comments = inspect.getcomments(obj)
                comments = ": %s" % comments if comments else ""
                variables.append("- **%s**%s" % (name, comments))
                line_nos.append(self.get_line_no(obj) or 0)

        variables = order_by_line_nos(variables, line_nos)
        if variables:
            new_list = ["**Global Variables**", "---------------"]
            new_list.extend(variables)
            variables = new_list

        string = MODULE_TEMPLATE.format(
            path=path,
            header=modname,
            section="#",
            doc=doc,
            global_vars="\n".join(variables) if variables else "",
            functions="\n".join(functions) if functions else "",
            classes="".join(classes) if classes else "",
        )
        return string
