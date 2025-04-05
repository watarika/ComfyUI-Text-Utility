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

バッチカウントを使ってバッチ実行した場合、実行するたびにstart行からインクリメントしながら1行ずつ取り出します。  
Webui の Prompts from file or textbox のような使い方ができます。

- start: 開始する行
- text: 抽出する元となるテキスト（複数行）

