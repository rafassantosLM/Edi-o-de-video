"""Dá ids estáveis (cap-01, cap-02…) às legendas do index.html, para o Studio conseguir editá-las."""
import re, sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = re.sub(r'<div id="cap-\d+" class="cap clip shadow"', '<div class="cap clip shadow"', s)  # idempotente
n = 0


def rep(m):
    global n
    n += 1
    return f'<div id="cap-{n:02d}" class="cap clip shadow"'


s = re.sub(r'<div class="cap clip shadow"', rep, s)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("legendas:", n)
