# ComfyUI-Text-Utility

[English][<a href="README_ja.md">日本語</a>]

Custom node to handle text.

## Load Text File

Loads a specified file.

![image](https://github.com/user-attachments/assets/4add098e-c33f-4657-9d15-e7f0955138d9)

## Save Text File

Saves the text to the specified file.

![image](https://github.com/user-attachments/assets/c0a838ef-8b87-4ecb-a0f9-be2a8dcbc99b)

If the directory does not exist, it is created.

If overwrite is set to True, overwrites the file.
If overwrite is False, no action is taken if the file exists.

## Remove Comments

Delete comment.Line comments and block comments are supported.

![image](https://github.com/user-attachments/assets/c93ce4e9-3c29-48d7-985c-b4517952b0d4)

- line_comment : The string used to start a single line comment (default: //)
- block_comment_start : The string used to start a block comment (default: /*)
- block_comment_end : The string used to end a block comment (default: */)
- remove_linefeed : remove linefeed or not (default: No)
  - No : do not remove
  - All : remove all
  - Blank Lines Only : remove blank lines only
