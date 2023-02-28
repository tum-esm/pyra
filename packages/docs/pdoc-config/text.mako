## Define mini-templates for each portion of the doco.

<%!
def indent(s, spaces=4):
    new = s.replace('\n', '\n' + ' ' * spaces)
    return ' ' * spaces + new.strip()

def render_py_function_def(func) -> str:
    params = func.params(annotate=True)
    params_str = ""
    if len(params) > 0:
        params_str = "\n"
        for p in func.params(annotate=True):
            params_str += "\t" + str(p).replace("\xa0", " ") + ",\n"

    return f"{func.funcdef()} {func.name}({params_str}) -> {func.return_annotation()}"
%>

<%def name="deflist(s)">:${indent(s)[1:]}</%def>

<%def name="h3(s)">### ${s}
</%def>

<%def name="function(func, h_level)" buffered="True">
${'##' if h_level == 'h2' else '###'} `${func.name}`

```py
${render_py_function_def(func)}
```

${func.docstring}

<br/>
</%def>

<%def name="variable(var)" buffered="True">
<%
annot = show_type_annotations and var.type_annotation() or ''
if annot:
    annot = ': ' + annot
%>
`${var.name}${annot}`
${var.docstring | deflist}
</%def>

<%def name="class_(cls)" buffered="True">
`${cls.name}(${", ".join(cls.params(annotate=show_type_annotations))})`
${cls.docstring | deflist}
<%
  class_vars = cls.class_variables(show_inherited_members, sort=sort_identifiers)
  static_methods = cls.functions(show_inherited_members, sort=sort_identifiers)
  inst_vars = cls.instance_variables(show_inherited_members, sort=sort_identifiers)
  methods = cls.methods(show_inherited_members, sort=sort_identifiers)
  mro = cls.mro()
  subclasses = cls.subclasses()
%>
% if mro:
${h3('Ancestors (in MRO)')}
% for c in mro:
* ${c.refname}
% endfor

% endif
% if subclasses:
${h3('Descendants')}
% for c in subclasses:
* ${c.refname}
% endfor

## =======================
## CLASS VARIABLES/METHODS

% endif
    % if class_vars:

${h3('Class variables')}
% for v in class_vars:
${variable(v) | indent}

    % endfor
% endif

## -----------------------

% if static_methods:

${h3('Static methods')}

    % for f in static_methods:

${function(f, "h3")}

    % endfor
% endif

## -----------------------

% if inst_vars:

${h3('Instance variables')}

% for v in inst_vars:

${variable(v) | indent}

    % endfor
% endif

## -----------------------

% if methods:

${h3('Methods')}

    % for m in methods:

${function(m, "h3")}

    % endfor
% endif

</%def>

## Start the output logic for an entire module.

<%
  variables = module.variables(sort=sort_identifiers)
  classes = module.classes(sort=sort_identifiers)
  functions = module.functions(sort=sort_identifiers)
  submodules = module.submodules()
  heading = 'Namespace' if module.is_namespace else 'Module'
%>

${heading} ${module.name}
=${'=' * (len(module.name) + len(heading))}
${module.docstring}


% if submodules:
Sub-modules
-----------
    % for m in submodules:
* ${m.name}
    % endfor
% endif

% if variables:
Variables
---------
    % for v in variables:
${variable(v)}

    % endfor
% endif

% if functions:
Functions
---------
    % for f in functions:
${function(f, "h2")}

    % endfor
% endif

% if classes:
Classes
-------
    % for c in classes:
${class_(c)}

    % endfor
% endif