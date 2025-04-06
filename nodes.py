import os
import impact
import impact.wildcards

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
            }
        }
        
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("string", ) 
    OUTPUT_IS_LIST = (False, )
    FUNCTION = 'remove_comments'
    CATEGORY = "text"

    def remove_comments(self, text, line_comment, block_comment_start, block_comment_end, remove_linefeed):

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

        return(text, )


class StringsFromTextboxNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "start": ("INT", {"default": 1, "min": 0, "step": 1}),
                "mode": (["Fixed", "Continued",], {"default": "Continued", "tooltip": "If Fixed, start is left unchanged; if Continued, start is updated to the number at which the process has progressed."}),
                "counter": ("INT", {"default": 0, "min": 0, "step": 1}),
            },
        }
        
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("string", "counter", )
    OUTPUT_IS_LIST = (False, )
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
        return (result, )


class PromptsFromTextboxNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "wildcard_text": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "Determines the random seed to be used for wildcard processing."}),
                "start": ("INT", {"default": 1, "min": 0, "step": 1}),
                "mode": (["Fixed", "Continued",], {"default": "Continued", "tooltip": "If Fixed, start is left unchanged; if Continued, start is updated to the number at which the process has progressed."}),
                "counter": ("INT", {"default": 0, "min": 0, "step": 1}),
            },
        }

    CATEGORY = "text"

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("prompt", )
    FUNCTION = "doit"

    def doit(self, wildcard_text, seed, start, mode, counter):
        target_string = StringsFromTextboxNode.extract_line(wildcard_text, start, mode, counter)
        result = impact.wildcards.process(target_string, seed)
        return (result, )

NODE_CLASS_MAPPINGS = {
    "LoadTextFile": LoadTextFileNode,
    "SaveTextFile": SaveTextFileNode,
    "RemoveComments": RemoveCommentsNode,
    "StringsFromTextbox": StringsFromTextboxNode,
    "PromptsFromTextbox": PromptsFromTextboxNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadTextFile": "Load Text File",
    "SaveTextFile": "Save Text File",
    "RemoveComments": "Remove Comments",
    "StringsFromTextbox": "Strings from textbox",
    "PromptsFromTextbox": "Prompts from textbox",
}
