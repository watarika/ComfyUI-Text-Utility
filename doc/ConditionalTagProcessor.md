# Conditional Tag Processor

[English][<a href="ConditionalTagProcessor_ja.md">日本語</a>]

This custom node is experimental. Its syntax and behavior may change.

**Conditional Tag Processor** is a **ComfyUI custom node** that applies bracket commands
`<ADD:...:...>` / `<REMOVE:...:...>` to tags within prompts.
Matching and de-duplication take into account plain words, parenthesized items, and the `[CUT:1girl:solo]` form.

* **Node name**: `Conditional Tag Processor`
* **Category**: `text`
* **Input**: `text` (STRING / multiline)
* **Output**: `processed` (STRING)

---

## What it does (overview)

* Detects **angle-bracket directives** (`ADD` / `REMOVE` in uppercase) contained in `text` and applies them **from left to right**.
* After applying, the directive strings themselves are removed from the text.
* **Words** are extracted and matched using the rules below (words may include spaces):

  * Plain item: used as-is (e.g., `blue eyes` -> the word is `blue eyes`)
  * **Parentheses**:

    * `(name:value)` -> the word is `name`
    * `(1girl, solo, smile, white shirt:1.5)` -> the words are `1girl`, `solo`, `smile`, `white shirt`

      * With `REMOVE`, sub-words are deleted; if **all** sub-words are removed, **the entire parentheses** (and any suffix like `:1.5`) are deleted.
    * `([CUT:white shirt:white])`, `([CUT:white shirt:white]:1.2)` -> the word is `white shirt`
  * **CUT**: `[CUT:white shirt:white]` -> the word is the middle **`white shirt`**

    * Specifying `white shirt` to `REMOVE` deletes the **entire CUT item**.
* **De-duplication in ADD**:

  * `add_target` can specify multiple elements via **comma separation**.
  * If a target element’s **word** (the name part for parentheses, the middle `white shirt` for CUT) already exists, that element is **not added**.
  * The inserted string uses the **notation as written in `add_target`** (e.g., `(white shirt:1.5)` or `[CUT:red shirt:red]`).
* **Insertion position**:

  * Elements in `add_target` are inserted **immediately after** the item that matched `search`, in the **specified order**.
    (If `search=''`, they are inserted at the **end**.)
  * For `A|B`, insert after **the first one found**; for `A&B`, insert after the **later one** (the word that appears further to the right).
* **Evaluation order**: `&` and `|` have **the same precedence** and are **left-associative**. Group with `()`.
* Only **uppercase** `ADD` / `REMOVE` are recognized (lowercase is ignored).
* Matching is **exact** and **case-sensitive** (compared as written).

---

## Directive format

### ADD

```
<ADD: search : add_target>
```

* `search` … optional. If omitted, `add_target` is inserted at the **end**.
* `add_target` … **comma-separated**, multiple allowed.
  Each element may be a **plain word**, **(name:value)**, or **[CUT:xxx:yyy]**, and is inserted **as written**.
  Before insertion, a **de-duplication check** (existing words) is performed; existing elements are skipped.

### REMOVE

```
<REMOVE: search : remove_target>
```

* `search` … optional. If omitted, `remove_target` is removed **unconditionally**.
* `remove_target` … a **comma-separated** list of **words**. Non-existent words are ignored.
  Words including spaces (e.g., `white shirt`) are allowed.
  If `white shirt` is specified, `[CUT:white shirt:white]` / `([CUT:white shirt:white])` / `([CUT:white shirt:white]:x)` are **removed as whole items**.
  In parenthesized multi-word items `(1girl, solo, ... :value)`, removal is done **per sub-word**; if **all** are removed, the parentheses themselves are deleted (and `:value` disappears with it).

---

## Writing the `search` expression

* Operators: `&` (AND), `|` (OR), `()` (grouping)
* **Left-associative, same precedence**

  * Example: `foo|bar&baz` is evaluated like `((foo|bar)&baz)`
* Examples:

  * `foo`
  * `foo|bar` … OK if either exists; insert immediately after **the first one found**
  * `foo&bar` … OK if both exist; insert after the **later** one
  * `(foo|bar)&baz` … use grouping to change evaluation order

---

## Examples

### 1) Spaces in words / CUT / multi-word parentheses

**Input**

```
blue eyes, 1girl, (solo), smile, (white shirt:1.3) <REMOVE:solo|smile:blue eyes, white shirt>
```

**Output**

```
1girl, (solo), smile
```

### 2) REMOVE by a CUT word (delete the whole CUT)

**Input**

```
a, [CUT:white shirt:white], b <REMOVE::white shirt>
```

**Output**

```
a, b
```

### 3) Parentheses + CUT also work

**Input**

```
a, ([CUT:white shirt:white]:1.2), b <REMOVE::white shirt>
```

**Output**

```
a, b
```

### 4) Partial removal inside multi-word parentheses

**Input**

```
x, (1girl, solo, smile, white shirt:1.5), y <REMOVE::1girl>
```

**Output**

```
x, (solo, smile, white shirt:1.5), y
```

### 5) Remove all sub-words -> parentheses disappear

**Input**

```
x, (1girl, solo, smile, white shirt:1.5), y <REMOVE::1girl, solo, smile, white shirt>
```

**Output**

```
x, y
```

### 6) ADD: skip existing words (de-duplication)

**Input**

```
a, (white shirt:1.0), b <ADD::white shirt, (white shirt:2.0), new item>
```

**Output**

```
a, (white shirt:1.0), b, new item
```

### 7) ADD: insert right after the matched item

**Input**

```
p, (1girl, solo), q <ADD:solo:NEW1, NEW2>
```

**Output**

```
p, (1girl, solo), NEW1, NEW2, q
```

### 8) ADD: `search` satisfied by a CUT -> insert after the CUT

**Input**

```
p, [CUT:white shirt:white], q <ADD:white shirt:[CUT:white shirt:X], [CUT:blue eyes:blue]>
```

**Output (example)**

```
p, [CUT:white shirt:white], [CUT:blue eyes:blue], q
```

* `[CUT:white shirt:X]` is skipped because `white shirt` already exists.
* `[CUT:blue eyes:blue]` is new -> inserted.

---

## Details

* Commas are split **only at the top level**.
  Commas inside `()` / `[]` are not used for splitting.
* **Trimming**: Each item is trimmed on both ends during splitting; internal spaces are preserved.
* **Case sensitivity**: Word matching is **exact** and **case-sensitive**.
* **Invalid `search`**: Syntax errors are treated as “no match” (the directive is skipped).
* **Uppercase only**: `<Add:...>` or `<remove:...>` are not recognized.
* **Application order**: When multiple directives exist, they are applied **in appearance order**, with changes taking effect immediately.

---

## Node I/O

* **INPUT**

  * `text` (STRING, multiline) — string containing the data and inline directives
* **OUTPUT**

  * `processed` (STRING) — the resulting string after directives are applied (directives removed)

---

## Tips & best practices

* Existing-word checks span **plain words / sub-words in parentheses / CUT (center word)**.
  Words that already exist **won’t be added again**.

* When you write a **parenthesized multi-word pack** like `(1girl, solo)` as a single element in `add_target`:

  * De-duplication checks **all sub-words** inside.
  * If inserted, it’s added **as one item** `(1girl, solo)`.

* `REMOVE` is safe to over-specify: non-existent words are ignored, so you can list many targets at once.

---

## Known limitations

* All matches are **exact** (no substring or regex matching).
* Nested parentheses/CUT are out of scope (only top-level parsing).
* No character normalization (e.g., full-/half-width, case folding) is performed.

---

## Troubleshooting

* **Not added as expected**:

  * Check whether the same **word** already exists somewhere (including inside parentheses or CUT).
  * Verify `search` syntax (`&` / `|` and matching parentheses).
  * Ensure `ADD` / `REMOVE` are in **uppercase**.
