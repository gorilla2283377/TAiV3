"""МПА варианта 12. Python 3, без сторонних библиотек.
Симулятор читает переходы из L12_PDA.jff. Стек: вершина слева.
Начальный магазин Z. Принятие: весь ввод прочитан и состояние финальное.
"""
from collections import deque
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET

def load(path):
    root = ET.parse(path).getroot()
    states = {s.get('id'): s.get('name') for s in root.findall('.//state')}
    start = next(s.get('id') for s in root.findall('.//state') if s.find('initial') is not None)
    final = {s.get('id') for s in root.findall('.//state') if s.find('final') is not None}
    transitions = [tuple(t.findtext(k) or '' for k in ('from', 'to', 'read', 'pop', 'push')) for t in root.findall('.//transition')]
    return states, start, final, transitions

def run(word, path=None):
    path = path or Path(__file__).with_name('L12_PDA.jff')
    states, start, final, transitions = load(path)
    first = (start, 0, 'Z')
    queue, seen, parent = deque([first]), {first}, {first: None}
    last = first
    while queue:
        current = queue.popleft()
        state, pos, stack = current
        if pos > last[1]: last = current
        if pos == len(word) and state in final:
            trace = []
            while current is not None:
                s, i, st = current
                trace.append((states[s], word[i:], st))
                current = parent[current]
            return True, trace[::-1]
        for source, target, read, pop, push in transitions:
            if source != state or not word.startswith(read, pos) or not stack.startswith(pop):
                continue
            nxt = (target, pos + len(read), push + stack[len(pop):])
            if nxt not in seen:
                seen.add(nxt); parent[nxt] = current; queue.append(nxt)
    trace = []
    while last is not None:
        s, i, st = last
        trace.append((states[s], word[i:], st))
        last = parent[last]
    return False, trace[::-1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('words', nargs='*', help='Цепочки. Пустая цепочка: ""')
    parser.add_argument('--trace', action='store_true')
    args = parser.parse_args()
    for word in (args.words if args.words else ['aaa', 'b', 'aabbb', 'abab', '', 'aab', 'aabb', 'ba']):
        accepted, trace = run(word)
        print(repr(word), 'ACCEPT' if accepted else 'REJECT')
        if args.trace:
            for state, rest, stack in trace:
                print(' ', state, 'input=' + repr(rest), 'stack=' + stack)
            if not accepted:
                print('  Одна из ветвей с максимальным прочитанным префиксом; принимающих ветвей нет.')
