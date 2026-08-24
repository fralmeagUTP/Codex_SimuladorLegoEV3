from simulador_ev3.ui.editor_panel import _python_syntax_spans


def _tagged_source(source: str, tag: str) -> list[str]:
    lines = source.splitlines(keepends=True)
    values: list[str] = []
    for current_tag, start, end in _python_syntax_spans(source):
        if current_tag != tag:
            continue
        if start[0] == end[0]:
            values.append(lines[start[0] - 1][start[1] : end[1]])
            continue
        parts = [lines[start[0] - 1][start[1] :]]
        parts.extend(lines[row] for row in range(start[0], end[0] - 1))
        parts.append(lines[end[0] - 1][: end[1]])
        values.append("".join(parts))
    return values


def test_highlighter_colors_comments_and_complete_multiline_docstring() -> None:
    source = '''#!/usr/bin/env pybricks-micropython
"""
Ejemplo 23 - Radar 360 con ultrasonido.

Que aprender:
1. Hacer un barrido circular tomando una muestra cada 5 grados.
"""
print(23)  # comentario en linea
'''

    assert _tagged_source(source, "comment") == [
        "#!/usr/bin/env pybricks-micropython",
        "# comentario en linea",
    ]
    assert _tagged_source(source, "string") == [
        '"""\nEjemplo 23 - Radar 360 con ultrasonido.\n\nQue aprender:\n'
        '1. Hacer un barrido circular tomando una muestra cada 5 grados.\n"""'
    ]
    assert _tagged_source(source, "number") == ["23"]


def test_highlighter_keeps_valid_tokens_when_source_is_incomplete() -> None:
    spans = _python_syntax_spans("print(1)\n\"\"\"documentación sin cerrar")

    assert ("builtin", (1, 0), (1, 5)) in spans
    assert ("number", (1, 6), (1, 7)) in spans
