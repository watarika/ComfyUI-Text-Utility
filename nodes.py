import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../ComfyUI-Impact-Pack/modules')))
import impact
import impact.wildcards
import re

class LoadTextFileNode:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING", {"multiline": False, "default": ""}),
                "file_name": ("STRING", {"multiline": False, "default": ""}),
            }
        }
        
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("string", ) 
    OUTPUT_IS_LIST = (False, )
    FUNCTION = 'load_text'
    CATEGORY = "text"

    def load_text(self, file_path, file_name):

        fullpath = os.path.join(file_path, file_name)           
        print(f"Load Text File: {fullpath}")

        with open(fullpath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return(content, )


class SaveTextFileNode:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "file_path": ("STRING", {"multiline": False, "default": ""}),
                "file_name": ("STRING", {"multiline": False, "default": ""}),
                "overwrite": ("BOOLEAN", {"default": True}),
            }
        }
        
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("filepath", ) 
    OUTPUT_NODE= True
    FUNCTION = 'save_text'
    CATEGORY = "text"

    def save_text(self, text, file_path, file_name, overwrite):
    
        fullpath = os.path.join(file_path, file_name)

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        if os.path.exists(fullpath) and not overwrite:
            msg = f"File already exists: {fullpath}"
            print(msg)
            return (msg, )
 
        with open(fullpath, 'w', encoding='utf-8') as file:
            file.write(text)

        print(f"Save Text File: {fullpath}")
        
        return (fullpath, )  


class RemoveCommentsNode:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True, "multiline": True, "default": ""}),
                "line_comment": ("STRING", {"multiline": False, "default": "//"}),
                "block_comment_start": ("STRING", {"multiline": False, "default": "/*"}),
                "block_comment_end": ("STRING", {"multiline": False, "default": "*/"}),
                "remove_linefeed": ([
                    "No",
                    "All",
                    "Blank Lines Only",
                ],),
                "normalize_commas": ("BOOLEAN", {"default": False}),
            }
        }
        
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("string", ) 
    OUTPUT_IS_LIST = (False, )
    FUNCTION = 'remove_comments'
    CATEGORY = "text"

    def remove_comments(self, text, line_comment, block_comment_start, block_comment_end, remove_linefeed, normalize_commas):

        # block_comment_startとblock_comment_endの間の文字を削除（複数行コメント）
        while block_comment_start in text:
            start = text.find(block_comment_start)
            end = text.find(block_comment_end)
            text = text[:start] + text[end + len(block_comment_end):]

        # line_comment以降の文字を削除（単一行コメント）
        while line_comment in text:
            start = text.find(line_comment)
            end = text.find("\n", start)
            if end == -1:
                end = len(text)
            text = text[:start] + text[end:]

        # 空行を削除
        if remove_linefeed == "Blank Lines Only":
            text = "\n".join([line for line in text.split("\n") if line.strip()])

        # 改行を削除
        elif remove_linefeed == "All":
            text = text.replace("\n", "")

        # カンマ区切り正規化
        if normalize_commas:
            text = self._normalize_commas(text)
        return(text, )

    @staticmethod
    def _normalize_commas(text):
        # 1. 連続カンマ（カンマ＋空白含む）が2回以上続く部分を「, 」に置換
        text = re.sub(r'(,\s*){2,}', ', ', text)
        # 2. カンマ前スペース除去・カンマ後スペース1つ
        text = re.sub(r'\s*,\s*', ', ', text)
        # 3. 末尾カンマ・末尾スペース除去
        text = re.sub(r'(, )+$', '', text)
        text = text.strip()
        return text


class StringsFromTextboxNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "start": ("INT", {"default": 1, "min": 0, "step": 1}),
                "mode": (["Fixed", "Continued",], {"default": "Fixed", "tooltip": "If Fixed, start is left unchanged; if Continued, start is updated to the number at which the process has progressed."}),
                "counter": ("INT", {"default": 0, "min": 0, "step": 1}),
            },
        }
        
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("prompt", "counter", )
    OUTPUT_IS_LIST = (False, False, )
    FUNCTION = 'doit'
    CATEGORY = "text"

    @staticmethod
    def extract_line(text, start, mode, counter):
        if mode == "Fixed":
            # Fixed mode: start remains unchanged
            target_line = start + counter - 1
        else:
            # Continued mode: start is updated to the number at which the process has progressed
            target_line = start - 1

        lines = text.split('\n')
        if target_line <= len(lines):
            return lines[target_line - 1]

        return ""

    def doit(self, text, start, mode, counter):
        result = StringsFromTextboxNode.extract_line(text, start, mode, counter)
        return (result, str(counter), )


class PromptsFromTextboxNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "wildcard_text": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "Determines the random seed to be used for wildcard processing."}),
                "start": ("INT", {"default": 1, "min": 0, "step": 1}),
                "mode": (["Fixed", "Continued",], {"default": "Fixed", "tooltip": "If Fixed, start is left unchanged; if Continued, start is updated to the number at which the process has progressed."}),
                "counter": ("INT", {"default": 0, "min": 0, "step": 1}),
            },
        }

    CATEGORY = "text"

    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("prompt", "counter", )
    OUTPUT_IS_LIST = (False, False, )
    FUNCTION = "doit"

    def doit(self, wildcard_text, seed, start, mode, counter):
        target_string = StringsFromTextboxNode.extract_line(wildcard_text, start, mode, counter)
        result = impact.wildcards.process(target_string, seed)
        return (result, str(counter), )


class ReplaceVariablesNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("replaced_text",)
    OUTPUT_IS_LIST = (False,)
    FUNCTION = "replace_variables"
    CATEGORY = "text"

    @staticmethod
    def replace_variables(text):
        # 変数定義の抽出: $name="value"
        var_pattern = re.compile(r'\$([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')
        var_defs = dict(var_pattern.findall(text))

        # 変数定義部分を削除
        text_wo_defs = var_pattern.sub("", text)

        # 変数参照の置換: $name
        def replace_var(match):
            var_name = match.group(1)
            return var_defs.get(var_name, match.group(0))

        ref_pattern = re.compile(r"\$([a-zA-Z_][a-zA-Z0-9_]*)")
        replaced_text = ref_pattern.sub(replace_var, text_wo_defs)

        # 先頭・末尾の不要な空白・改行を除去
        return (replaced_text.strip(),)


NODE_CLASS_MAPPINGS = {
    "LoadTextFile": LoadTextFileNode,
    "SaveTextFile": SaveTextFileNode,
    "RemoveComments": RemoveCommentsNode,
    "StringsFromTextbox": StringsFromTextboxNode,
    "PromptsFromTextbox": PromptsFromTextboxNode,
    "ReplaceVariables": ReplaceVariablesNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadTextFile": "Load Text File",
    "SaveTextFile": "Save Text File",
    "RemoveComments": "Remove Comments",
    "StringsFromTextbox": "Strings from textbox",
    "PromptsFromTextbox": "Prompts from textbox",
    "ReplaceVariables": "Replace Variables",
}
