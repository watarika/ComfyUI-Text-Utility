import os

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
                "remove_blank_lines": ("BOOLEAN", {"default": True}),
            }
        }
        
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("string", ) 
    OUTPUT_IS_LIST = (False, )
    FUNCTION = 'remove_comments'
    CATEGORY = "text"

    def remove_comments(self, text, line_comment, block_comment_start, block_comment_end, remove_blank_lines):

        # block_comment_startとblock_comment_endの間の文字を削除（複数行コメント）
        """
        Remove comments from a given string.

        Parameters
        ----------
        text : str
            The string from which comments are removed.
        line_comment : str
            The string used to start a single line comment.
        block_comment_start : str
            The string used to start a block comment.
        block_comment_end : str
            The string used to end a block comment.
        remove_blank_lines : bool
            If True, remove all blank lines from the string.

        Returns
        -------
        str
            The string with all comments removed.
        """
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
        if remove_blank_lines:
            text = "\n".join([line for line in text.split("\n") if line.strip()])

        return(text, )


NODE_CLASS_MAPPINGS = {
    "LoadTextFile": LoadTextFileNode,
    "SaveTextFile": SaveTextFileNode,
    "RemoveComments": RemoveCommentsNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadTextFile": "Load Text File",
    "SaveTextFile": "Save Text File",
    "RemoveComments": "Remove Comments",
}
