import re
from typing import List, Tuple, Optional

class ConditionalTagProcessorNode:
    """
    Conditional Tag Processor

    対応仕様（要点）
    - 命令:
        <ADD:search:add_target>
        <REMOVE:search:remove_target>
      ※ ADD/REMOVE は大文字のみ有効。search は &, | を左結合評価、() でグルーピング可。
    - データ:
        カンマ区切りのアイテム列。空白はトリム、内部の空白は保持。
        通常アイテム: "abc efg"
        括弧アイテム: "(name:value)" または "(foo, bar, baz, white shirt:1.5)"
            - 検索・存在判定は各サブ語（name / foo / bar / baz / white shirt）
            - REMOVEでサブ語を削除。全消しになったら括弧ごと（:suffix も含め）削除
        CUT アイテム:
            "[CUT:foo:bar]" / "([CUT:foo:bar])" / "([CUT:foo:bar]:1.2)"
            - 検索・存在判定の語は中央 foo
            - REMOVEで foo を指定したら CUT アイテム全体を削除

    - ADD の add_target 仕様:
        - add_target はカンマ区切りで複数可
        - 各要素は通常語 / (name:tail) / [CUT:foo:bar] を許容
        - 追加前に「既存の語」を判定（通常 / 括弧サブ語 / CUT 含む）
        - 既存語は追加しない。新規のみ追加
        - 追加する表記は add_target に記載された**見た目そのまま**
        - search が一致したアイテムの直後（search='' の場合は末尾）に、指定順で挿入

    入出力:
        入力: text (STRING)
        出力: processed (STRING)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("processed",)
    FUNCTION = "process"
    CATEGORY = "text"
    OUTPUT_NODE = False

    # ----------------- Core processing -----------------

    @staticmethod
    def _split_top_level(text: str) -> List[str]:
        """トップレベルのカンマで分割（() と [] の内側のカンマは無視）"""
        items, buf = [], []
        par, br = 0, 0
        for ch in text:
            if ch == '(':
                par += 1
            elif ch == ')':
                par = max(0, par - 1)
            elif ch == '[':
                br += 1
            elif ch == ']':
                br = max(0, br - 1)
            if ch == ',' and par == 0 and br == 0:
                seg = ''.join(buf).strip()
                if seg:
                    items.append(seg)
                buf = []
            else:
                buf.append(ch)
        seg = ''.join(buf).strip()
        if seg:
            items.append(seg)
        return items

    @staticmethod
    def _join_items(items: List[str]) -> str:
        return ', '.join(items)

    CUT_BARE = re.compile(r'^\[CUT\s*:\s*(.*?)\s*:\s*(.*?)\]\s*$')
    CUT_INNER = re.compile(r'^\[CUT\s*:\s*(.*?)\s*:\s*(.*?)\]\s*(?::.*)?$')

    @classmethod
    def _item_words(cls, item: str) -> List[str]:
        """
        アイテムから検索・存在判定用の語を抽出
        - 通常: そのまま
        - CUT: foo
        - 括弧:
            - ([CUT:foo:bar]) / ([CUT:foo:bar]:x) → foo
            - (foo, bar, white:1.0) → ["foo","bar","white"]
            - (name:val) → ["name"]
        """
        t = item.strip()
        # 素の CUT
        m = cls.CUT_BARE.match(t)
        if m:
            return [m.group(1).strip()]
        # 括弧
        if t.startswith('(') and t.endswith(')'):
            inner = t[1:-1].strip()
            # 括弧内 CUT（:tail 許容）
            m2 = cls.CUT_INNER.match(inner)
            if m2:
                return [m2.group(1).strip()]
            # 括弧内複数語
            subs = cls._split_top_level(inner)
            if subs:
                words = []
                for seg in subs:
                    seg = seg.strip()
                    if not seg:
                        continue
                    name = seg.split(':', 1)[0].strip()
                    words.append(name)
                if words:
                    return words
            # 単一
            return [inner.split(':', 1)[0].strip()]
        # 通常
        return [t]

    @classmethod
    def _remove_from_parenthetical(cls, t: str, targets: set) -> Optional[str]:
        """
        括弧アイテムから targets を除去。空になれば None（=アイテムごと削除）
        CUT が中身なら語一致で None
        """
        inner = t[1:-1].strip()

        # CUT in () → 語一致なら全削除
        m2 = cls.CUT_INNER.match(inner)
        if m2:
            word = m2.group(1).strip()
            return None if word in targets else t

        # 複数語の可能性
        subs = cls._split_top_level(inner)
        if subs:
            kept = []
            for seg in subs:
                seg_trim = seg.strip()
                if not seg_trim:
                    continue
                word = seg_trim.split(':', 1)[0].strip()
                if word not in targets:
                    kept.append(seg_trim)
            if kept:
                return '(' + ', '.join(kept) + ')'
            else:
                return None

        # 単一
        base = inner.split(':', 1)[0].strip()
        return None if base in targets else t

    # -------- search expression parser (left-assoc &, |; () grouping) --------

    class _Tok:
        def __init__(self, typ, val=None):
            self.typ, self.val = typ, val

    @classmethod
    def _tokenize(cls, expr: str):
        toks, i = [], 0
        while i < len(expr):
            ch = expr[i]
            if ch.isspace():
                i += 1; continue
            if ch in '()&|':
                toks.append(cls._Tok(ch)); i += 1; continue
            j = i
            while j < len(expr) and expr[j] not in '()&|':
                j += 1
            word = expr[i:j].strip()
            if word:
                toks.append(cls._Tok('WORD', word))
            i = j
        return toks

    class _Node: ...
    class _Word(_Node):
        def __init__(self, w): self.w = w
        def eval(self, pos_map):
            pos = pos_map.get(self.w, None)
            return (pos is not None, pos)
    class _And(_Node):
        def __init__(self, l, r): self.l, self.r = l, r
        def eval(self, pos_map):
            lt, lp = self.l.eval(pos_map)
            rt, rp = self.r.eval(pos_map)
            ok = lt and rt
            return (ok, (max(lp, rp) if ok else None))
    class _Or(_Node):
        def __init__(self, l, r): self.l, self.r = l, r
        def eval(self, pos_map):
            lt, lp = self.l.eval(pos_map)
            rt, rp = self.r.eval(pos_map)
            ok = lt or rt
            if not ok: return (False, None)
            if lp is None: return (True, rp)
            if rp is None: return (True, lp)
            return (True, min(lp, rp))

    @classmethod
    def _parse_search(cls, expr: str) -> Optional["_Node"]:
        toks = cls._tokenize(expr)
        i = 0
        def peek():
            return toks[i] if i < len(toks) else None
        def eat(typ=None):
            nonlocal i
            tok = peek()
            if tok is None: return None
            if typ and tok.typ != typ:
                raise ValueError(f"Expected {typ}, got {tok.typ}")
            i += 1
            return tok
        def term():
            tok = peek()
            if tok is None: raise ValueError("Unexpected end")
            if tok.typ == '(':
                eat('(')
                node = expr_rule()
                if peek() is None or peek().typ != ')':
                    raise ValueError("Missing ')'")
                eat(')')
                return node
            if tok.typ == 'WORD':
                return cls._Word(eat('WORD').val)
            raise ValueError(f"Unexpected token {tok.typ}")
        def expr_rule():
            node = term()
            while True:
                tok = peek()
                if tok and tok.typ in ('&','|'):
                    op = eat().typ
                    rhs = term()
                    node = cls._And(node, rhs) if op=='&' else cls._Or(node, rhs)
                else:
                    break
            return node
        if not toks:
            return None
        try:
            return expr_rule()
        except Exception:
            return None

    # ----------------- ComfyUI entry point -----------------

    def process(self, text: str):
        """
        ComfyUI entry point. Returns a single STRING output.
        """
        s = text if isinstance(text, str) else str(text)

        # 抽出: <ADD:...:...> / <REMOVE:...:...>
        cmd_pattern = re.compile(r'<(ADD|REMOVE)\s*:\s*(.*?)\s*:\s*(.*?)>')
        ops: List[Tuple[str, str, str]] = [
            (m.group(1).upper(), m.group(2).strip(), m.group(3).strip())
            for m in cmd_pattern.finditer(s)
        ]
        data_part = cmd_pattern.sub('', s).strip()

        items = self._split_top_level(data_part)

        for kind, search, target in ops:
            # 現在の語→最初の出現 index（括弧サブ語や CUT も含む）
            first_pos = {}
            for idx, it in enumerate(items):
                for w in self._item_words(it):
                    if w not in first_pos:
                        first_pos[w] = idx

            if kind == 'ADD':
                raw_targets = [t for t in self._split_top_level(target) if t.strip()]
                if not raw_targets:
                    continue

                # 挿入位置の決定
                if search.strip() == '':
                    insert_after_index = len(items) - 1
                else:
                    ast = self._parse_search(search)
                    if ast is None:
                        continue
                    ok, pos = ast.eval(first_pos)
                    if not ok:
                        continue
                    insert_after_index = pos if isinstance(pos, int) else (len(items) - 1)

                # 既存語セット（重複回避）
                present_words = set(first_pos.keys())

                # 追加候補を順に判定・蓄積
                to_insert: List[str] = []
                for rt in raw_targets:
                    words_of_rt = set(self._item_words(rt))
                    if any(w in present_words for w in words_of_rt):
                        continue
                    to_insert.append(rt)
                    present_words.update(words_of_rt)

                if not to_insert:
                    continue

                # 直後に順次挿入
                insert_at = insert_after_index + 1
                for val in to_insert:
                    items.insert(insert_at, val)
                    insert_at += 1

            elif kind == 'REMOVE':
                targets = {t.strip() for t in self._split_top_level(target)}
                targets.discard('')
                if not targets:
                    continue

                # 条件評価
                cond_ok = True
                if search.strip() != '':
                    ast = self._parse_search(search)
                    if ast is None:
                        cond_ok = False
                    else:
                        cond_ok, _ = ast.eval(first_pos)
                if not cond_ok:
                    continue

                # 実削除
                new_items: List[str] = []
                for it in items:
                    t = it.strip()
                    # 素の CUT → 語が targets にあれば全削除
                    m = self.CUT_BARE.match(t)
                    if m and m.group(1).strip() in targets:
                        continue

                    # 括弧 → サブ語削除、空なら全削除
                    if t.startswith('(') and t.endswith(')'):
                        replaced = self._remove_from_parenthetical(t, targets)
                        if replaced is not None:
                            new_items.append(replaced)
                        continue

                    # 通常
                    wlist = self._item_words(t)
                    bw = wlist[0] if wlist else ''
                    if bw in targets:
                        continue
                    new_items.append(t)

                items = new_items

        return (self._join_items(items),)


