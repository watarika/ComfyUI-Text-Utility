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


NODE_CLASS_MAPPINGS = {
    "LoadTextFile": LoadTextFileNode,
    "SaveTextFile": SaveTextFileNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadTextFile": "Load Text File",
    "SaveTextFile": "Save Text File",
}
