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

![image](https://github.com/user-attachments/assets/a1d61f3b-f96e-4e9e-a669-f4d722bd473b)

- line_comment : The string used to start a single line comment (default: //)
- block_comment_start : The string used to start a block comment (default: /*)
- block_comment_end : The string used to end a block comment (default: */)
- remove_linefeed : remove linefeed or not (default: No)
  - No : do not remove
  - All : remove all
  - Blank Lines Only : remove blank lines only
- normalize_commas : Normalize commas at word separators and remove extra commas (default: False)

## Strings from textbox

Extracts a single line from multiple lines of text entered in a textbox.

![image](https://github.com/user-attachments/assets/a576e017-73aa-4eae-a9c7-af888b90b35c)

When executed in batch using batch count, it takes out one line at a time, incrementing from the start line each time it is executed.
You can use it like Webui's Prompts from file or textbox.

If you want to use wildcards, use "Prompts from textbox".

- text: Source text (multiple lines) to be extracted
- start: The line to start with
- mode: Whether to update each time start is processed (default: Continued)
  - Fixed : do not update
  - Continued : updated

## Prompts from textbox

"Strings from textbox" with wildcard support.

![image](https://github.com/user-attachments/assets/8b34b576-c27e-4c68-9ec7-81caa52ae611)

Internally calls the wildcard processing of [ComfyUI-Impact-Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack).Therefore, ComfyUI-Impact-Pack must be installed.

For wildcards, see [ImpactWildcard](https://github.com/ltdrdata/ComfyUI-extension-tutorials/blob/Main/ComfyUI-Impact-Pack/tutorial/ImpactWildcard.md).

- wildcard_text: The source wildcard text (multiple lines) to be extracted
- seed: Seed to use for wildcard processing
- start: The line to start with
- mode: Whether to update each time start is processed (default: Fixed)
  - Fixed : do not update
  - Continued : updated

## Replace Variables

Replaces variables in the input text using definitions.

![image](https://github.com/user-attachments/assets/87debebe-baac-46f7-ae8b-de2bc3124f3e)

- Variable definition syntax: `$name="value"` (value must be enclosed in double quotes)
- Multiple variables can be defined.
- Variable usage syntax: `$name`
- Example input: `$animal="cat" $color="black" The $color $animal sleeps on the sofa.`
- Example output: `The black cat sleeps on the sofa.`

## Changelog

- v1.3.1 (2025-04-22)
  - Added normalize_commas option to Remove Comments node
- v1.3.0 (2025-04-22)
  - Add Replace Variables Node
- v1.2.0 (2025-04-06)
  - Add Prompts from textbox Node
- v1.1.0 (2025-04-05)
  - Add Strings from textbox Node
