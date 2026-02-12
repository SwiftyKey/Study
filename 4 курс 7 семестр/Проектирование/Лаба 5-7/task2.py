import re
import math
import json
from dataclasses import dataclass
from typing import List


@dataclass
class Vertex:
    x: float
    y: float


@dataclass
class Figure:
    kind: str
    vertices: List[Vertex]


@dataclass
class ParseResult:
    figures: List[Figure]


# Лексер
TOKEN_SPEC = [
    ("KW",      r"\b(квадрат|ромб)\b"),
    ("LBRACE",  r"\{"),
    ("RBRACE",  r"\}"),
    ("LPAR",    r"\("),
    ("RPAR",    r"\)"),
    ("COMMA",   r","),
    ("SEMICOL", r";"),
    ("NUMBER",  r"[+-]?\d+(?:\.\d+)?"),
    ("WS",      r"[ \t\r\n]+"),
    ("MISC",    r"."),
]
TOK_REGEX = re.compile(
    "|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC), re.IGNORECASE)


class Token:
    def __init__(self, typ, val, pos):
        self.type = typ
        self.val = val
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type},{self.val},{self.pos})"


def lex(text):
    tokens = []
    for m in TOK_REGEX.finditer(text):
        kind = m.lastgroup
        val = m.group()
        start = m.start()
        if kind == "WS":
            pass
        elif kind == "MISC":
            raise SyntaxError(f"Неизместный символ {val!r} на позиции {start}")
        else:
            tokens.append(Token(kind, val, start))
    tokens.append(Token("EOF", "", len(text)))
    return tokens

# Парсер
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def cur(self): return self.tokens[self.i]

    def eat(self, typ):
        t = self.cur()
        if t.type == typ:
            self.i += 1
            return t
        raise SyntaxError(
            f"Ожидалось {typ} на позиции {t.pos}, нашлось {t.type}({t.val})")

    def accept(self, typ):
        if self.cur().type == typ:
            return self.eat(typ)
        return None

    def parse(self):
        figs = []
        while self.cur().type != "EOF":
            if self.cur().type == "SEMICOL":
                self.eat("SEMICOL")
                continue
            fig = self.parse_figure()
            figs.append(fig)
            if self.accept("SEMICOL"):
                pass
            else:
                if self.cur().type == "EOF":
                    break
        return ParseResult(figs)

    def parse_figure(self):
        t = self.cur()
        if t.type != "KW":
            raise SyntaxError(
                f"Ожидаемое ключевое слово в позиции {t.pos}, найдено {t.val!r}")
        kind = self.eat("KW").val.lower()
        if self.accept("LBRACE"):
            verts = []
            while True:
                if self.accept("RBRACE"):
                    break
                v = self.parse_vertex()
                verts.append(v)
                self.accept("COMMA")
                if self.cur().type == "EOF":
                    raise SyntaxError("Незавершенная '{' - пропущена '}'")
            if len(verts) < 4:
                raise SyntaxError(
                    f"{kind}: ожидалось 4 вершины, получено {len(verts)}")
            return Figure(kind, verts)
        else:
            raise SyntaxError(f"Ожидалось '{{' после {kind}")

    def parse_vertex(self):
        if self.accept("LPAR"):
            n1 = self.eat("NUMBER")
            self.accept("COMMA")
            n2 = self.eat("NUMBER")
            self.eat("RPAR")
            return Vertex(float(n1.val), float(n2.val))
        else:
            n1 = self.eat("NUMBER")
            self.accept("COMMA")
            n2 = self.eat("NUMBER")
            return Vertex(float(n1.val), float(n2.val))

# Простые геометрические проверки
def is_square(verts, tol=1e-6):
    if len(verts) != 4:
        return False

    pts = [(v.x, v.y) for v in verts]
    d = lambda a, b: math.hypot(a[0]-b[0], a[1]-b[1])
    sides = [d(pts[i], pts[(i+1) % 4]) for i in range(4)]
    diag = (d(pts[0], pts[2]), d(pts[1], pts[3]))

    return max(sides)-min(sides) < tol and abs(diag[0]-diag[1]) < tol


def is_rhombus(verts, tol=1e-6):
    if len(verts) != 4:
        return False

    pts = [(v.x, v.y) for v in verts]
    d = lambda a, b: math.hypot(a[0]-b[0], a[1]-b[1])
    sides = [d(pts[i], pts[(i+1) % 4]) for i in range(4)]
    return max(sides)-min(sides) < tol


# Тесты
tests = []
tests.append(
    ("Один квадрат", "квадрат { (0,0) (1,0) (1,1) (0,1) }", True))
tests.append(("Один ромб", "ромб { 0,0 1,1 2,0 1,-1 }", True))
tests.append(("Две фигуры",
             "квадрат { (0,0) (1,0) (1,1) (0,1) }; ромб { (0,0) (2,1) (4,0) (2,-1) }", True))
many = "; ".join(
    f"квадрат {{ ({i},{i+1}) ({i+1},{i+1}) ({i+1},{i+2}) ({i},{i+2}) }}" for i in range(0, 50))
tests.append(("Несколько фигур", many, True))
tests.append(("Пропущенная фигурная скобка", "квадрат { (0,0) (1,0) (1,1) (0,1) ", False))
tests.append(("Мало врешин", "ромб { (0,0) (1,0) (1,1) }", False))
tests.append(("Неверный токен", "квадрат { (0,0) (1,0) foo (0,1) }", False))
tests.append(("Нечисловые данные", "квадрат { (a,b) (1,0) (1,1) (0,1) }", False))
'''
results = []
for name, src, should in tests:
    try:
        toks = lex(src)
        p = Parser(toks)
        ast = p.parse()
        ok = True
    except Exception as e:
        ast = str(e)
        ok = False
    results.append((name, ok, ast, should))

# Обобщение и сохранение
report = {"total": len(results), "passed": sum(
    1 for r in results if r[1] == r[3]), "details": []}
for name, ok, ast, should in results:
    report["details"].append(
        {"test": name, "expected": should, "ok": ok, "ast_or_error": str(ast)})

with open("parser_test_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

# Вывод результатов
print("Результаты тестов:")
for name, ok, ast, should in results:
    status = "PASS" if ok == should else "FAIL"
    print(f"{name}: {status} (ожидалось {should}, получено {ok})")
print("\nОтчет сохранен в parser_test_report.json")
'''
