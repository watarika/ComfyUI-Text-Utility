# Conditional Tag Processor

[<a href="ConditionalTagProcessor.md">English</a>][日本語]

このカスタムノードは実験的なノードです。書式、動作は変更される可能性があります。

**Conditional Tag Processor** は、プロンプト中のタグに対して、角括弧命令
`<ADD:...:...>` / `<REMOVE:...:...>` を適用する **ComfyUI カスタムノード**です。
検索条件・重複判定は、通常語・カッコ内アイテム・`[CUT:1girl:solo]` 形式をすべて考慮します。

* **ノード名**: `Conditional Tag Processor`
* **カテゴリ**: `text`
* **入力**: `text` (STRING / multiline)
* **出力**: `processed` (STRING)

---

## できること（概要）

* `text` に含まれる **角括弧命令**（大文字の `ADD` / `REMOVE`）を検出し、**左から順に**適用します。
* 命令適用後、命令文字列自体はテキストから削除されます。
* **単語**は以下の規則で抽出・照合します（スペースを含む単語も可）:

  * 通常アイテム：そのまま（例: `blue eyes` → 単語は `blue eyes`）
  * **カッコ**：

    * `(name:value)` → 単語は `name`
    * `(1girl, solo, smile, white shirt:1.5)` → 単語は `1girl`, `solo`, `smile`, `white shirt`

      * `REMOVE` でサブ語削除、**全消し**になったら **カッコごと**（および `:1.5` などのサフィックスも）削除
    * `([CUT:white shirt:white])`, `([CUT:white shirt:white]:1.2)` → 単語は `white shirt`
  * **CUT**：`[CUT:white shirt:white]` → 単語は中央の **`white shirt`**

    * `REMOVE` で `white shirt` を指定すると **CUT アイテム全体** を削除
* **ADD の重複回避**：

  * `add_target` は**カンマ区切り**で複数要素を指定可能
  * 各要素の**単語**（カッコは名前部、CUT は中央 `white shirt`）がすでに存在する場合、その要素は**追加しない**
  * 挿入する文字列は **add_target に書かれた表記そのまま**（例: `(white shirt:1.5)` や `[CUT:red shirt:red]`）
* **挿入位置**：

  * `search` が一致した **アイテムの直後** に、`add_target` の要素を**指定順**で挿入
    （`search=''` のときは**末尾**に挿入）
  * `search` が `A|B` の場合は**最初に見つかった**方、`A&B` の場合は**両方が存在**したときの**後ろ側**（より後方にある語）に挿入
* **評価順序**：`&` と `|` は**同優先・左結合**。`()` でグルーピング可能。
* 文字種は**大文字の `ADD` / `REMOVE` のみ**認識（小文字は無視）。
* 照合は**完全一致・大文字小文字区別あり**（入力そのままを比較）。

---

## 命令フォーマット

### ADD

```
<ADD: search : add_target>
```

* `search` … 省略可。省略時は `add_target` を**末尾**に挿入。
* `add_target` … **カンマ区切り**で複数指定可。
  各要素は **通常語** / **(name:value)** / **[CUT:xxx:yyy]** を指定でき、**表記のまま**追加されます。
  追加前に**重複判定**（既存の語）を行い、存在する要素はスキップ。

### REMOVE

```
<REMOVE: search : remove_target>
```

* `search` … 省略可。省略時は **無条件**に `remove_target` を削除。
* `remove_target` … **カンマ区切り**の**語**を列挙。存在しない語は無視。
  `white shirt` のようなスペース含み語も可。
  `white shirt` を指定すると、`[CUT:white shirt:white]` / `([CUT:white shirt:white])` / `([CUT:white shirt:white]:x)` は**アイテムごと削除**。
  カッコ内複数語 `(1girl, solo, ... :value)` は **サブ語単位**で削除。**全消し**ならカッコ自体も削除（`:value` も同時に消滅）。

---

## 検索式（`search`）の書き方

* 記号：`&`（AND）, `|`（OR）, `()`（グループ）
* **左結合・同優先**

  * 例：`foo|bar&baz` は `((foo|bar)&baz)` と同じ評価順
* 例：

  * `foo`
  * `foo|bar` … どちらかがあれば OK、**先に見つかった**ほうの直後に追加
  * `foo&bar` … 両方あれば OK、**より後ろ**にあるほうの直後に追加
  * `(foo|bar)&baz` … グルーピングで順序を変更

---

## 例

### 1) スペースを含む語 / CUT / カッコ内複数語

**入力**

```
blue eyes, 1girl, (solo), smile, (white shirt:1.3) <REMOVE:solo|smile:blue eyes, white shirt>
```

**出力**

```
1girl, (solo), smile
```

### 2) CUT の語で REMOVE（CUT ごと削除）

**入力**

```
a, [CUT:white shirt:white], b <REMOVE::white shirt>
```

**出力**

```
a, b
```

### 3) カッコ＋CUT でも OK

**入力**

```
a, ([CUT:white shirt:white]:1.2), b <REMOVE::white shirt>
```

**出力**

```
a, b
```

### 4) カッコ内複数語の部分削除

**入力**

```
x, (1girl, solo, smile, white shirt:1.5), y <REMOVE::1girl>
```

**出力**

```
x, (solo, smile, white shirt:1.5), y
```

### 5) カッコ内複数語を全削除 → カッコごと消える

**入力**

```
x, (1girl, solo, smile, white shirt:1.5), y <REMOVE::1girl, solo, smile, white shirt>
```

**出力**

```
x, y
```

### 6) ADD：既存語は追加しない（重複回避）

**入力**

```
a, (white shirt:1.0), b <ADD::white shirt, (white shirt:2.0), new item>
```

**出力**

```
a, (white shirt:1.0), b, new item
```

### 7) ADD：挿入位置はマッチしたアイテム直後

**入力**

```
p, (1girl, solo), q <ADD:solo:NEW1, NEW2>
```

**出力**

```
p, (1girl, solo), NEW1, NEW2, q
```

### 8) ADD：CUT が search にマッチ → CUT の直後に挿入

**入力**

```
p, [CUT:white shirt:white], q <ADD:white shirt:[CUT:white shirt:X], [CUT:blue eyes:blue]>
```

**出力（例）**

```
p, [CUT:white shirt:white], [CUT:blue eyes:blue], q
```

* `[CUT:white shirt:X]` は `white shirt` が既に存在 → 追加スキップ
* `[CUT:blue eyes:blue]` は新規 → 追加

---

## 仕様の細目

* **トップレベルのみ**カンマ分割
  `()` / `[]` 内のカンマは分割に使われません。
* **トリム**
  分割時の各要素は前後スペースをトリム。内部スペースは保持。
* **大小区別**
  単語一致は**完全一致・大文字小文字区別あり**。
* **不正な `search` 式**
  構文エラーの `search` は「不一致」として処理（命令スキップ）。
* **命令は大文字限定**
  `<Add:...>` や `<remove:...>` は認識しません。
* **適用順**
  複数命令がある場合、**出現順**に即時反映しながら進みます。

---

## ノード I/O

* **INPUT**

  * `text` (STRING, multiline) … データ本体＋角括弧命令を含む文字列
* **OUTPUT**

  * `processed` (STRING) … 命令適用後の文字列（命令は削除済み）

---

## ヒント & ベストプラクティス

* 既存語の判定は **通常語 / カッコ内サブ語 / CUT（中央語）** を横断して行われます。
  「すでにどこかにある語」は **重複追加されません**。
* `add_target` に `(1girl, solo)` のような**複数語のカッコ**を1要素で書いた場合：

  * 重複判定は **中の全サブ語**が対象
  * 追加する場合は **「(1girl, solo)」という1アイテム**として挿入されます
* `REMOVE` は安全側：存在しない語は無視されるため、複数語をまとめて指定して問題ありません。

---

## 既知の制限

* いずれの一致も**完全一致**です（部分一致・正規表現は未対応）。
* カッコや CUT の**入れ子**は想定外です（トップレベルのみ解析）。
* 文字正規化（全角半角・大文字小文字の変換など）は行いません。

---

## トラブルシュート

* **期待どおり追加されない**：

  * 既に同じ**単語**がどこかに存在していないか（カッコ内・CUT 含む）確認してください。
  * `search` の構文が正しいか（`&` / `|` と括弧の対応）確認してください。
  * `ADD` / `REMOVE` が**大文字**になっているか確認してください。

