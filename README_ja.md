# ComfyUI-Text-Utility

[<a href="README.md">English</a>][日本語]

テキストを扱うカスタムノードです。

## Load Text File

指定したファイルを読み込みます。

![image](https://github.com/user-attachments/assets/4add098e-c33f-4657-9d15-e7f0955138d9)

## Save Text File

指定したファイルにテキストを保存します。

![image](https://github.com/user-attachments/assets/c0a838ef-8b87-4ecb-a0f9-be2a8dcbc99b)

ディレクトリが存在しない場合は作成します。

overwriteをTrueにすると上書き保存します。
overwriteをFalseにするとファイルが存在した場合は何も行いません。

## Remove Comments

コメントを削除します。行コメントとブロックコメントに対応しています。

![image](https://github.com/user-attachments/assets/c93ce4e9-3c29-48d7-985c-b4517952b0d4)

- line_comment : 行コメントを開始する文字列（デフォルト：//）
- block_comment_start : ブロックコメントを開始する文字列（デフォルト：/*）
- block_comment_end : ブロックコメントを終了する文字列（デフォルト：*/）
- remove_linefeed : 改行を削除するかどうか（デフォルト：No）
  - No : 削除しない
  - All : すべて削除する
  - Blank Lines Only : 空行のみ削除する

## Strings from textbox

テキストボックスに入力した複数行のテキストから1行を取り出します。

![image](https://github.com/user-attachments/assets/a576e017-73aa-4eae-a9c7-af888b90b35c)

バッチカウントを使ってバッチ実行した場合、実行するたびにstart行からインクリメントしながら1行ずつ取り出します。  
Webui の Prompts from file or textbox のような使い方ができます。

ワイルドカードを使用する場合は「Prompts from textbox」を使ってください。

- text: 抽出する元となるテキスト（複数行）
- start: 開始する行
- mode: startを処理するたびに更新するかどうか（デフォルト：Continued）
  - Fixed : 更新しない
  - Continued : 更新する

## Prompts from textbox

ワイルドカードに対応した "Strings from textbox" です。

![image](https://github.com/user-attachments/assets/8b34b576-c27e-4c68-9ec7-81caa52ae611)

内部的に [ComfyUI-Impact-Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack) のワイルドカード処理を呼び出します。そのため、ComfyUI-Impact-Pack をインストールしておく必要があります。

ワイルドカードについては [ImpactWildcard](https://github.com/ltdrdata/ComfyUI-extension-tutorials/blob/Main/ComfyUI-Impact-Pack/tutorial/ImpactWildcard.md) を参照してください。

- wildcard_text: 抽出する元となるワイルドカードテキスト（複数行）
- seed: ワイルドカード処理に使用するSeed
- start: 開始する行
- mode: startを処理するたびに更新するかどうか（デフォルト：Fixed）
  - Fixed : 更新しない
  - Continued : 更新する

## Replace Variables

入力テキスト内の変数を定義・置換します。

- 変数定義構文：`$name="値"`（値はダブルクォートで囲む必要があります）
- 複数の変数定義が可能です。
- 変数使用構文：`$name`
- 入力例：`$animal="cat" $color="black" The $color $animal sleeps on the sofa.`
- 出力例：`The black cat sleeps on the sofa.`

## 変更履歴

- v1.3.0 (2025-04-22)
  - Replace Variables ノードを追加
- v1.2.0 (2025-04-06)
  - Prompts from textbox ノードを追加
- v1.1.0 (2025-04-05)
  - Strings from textbox ノードを追加
