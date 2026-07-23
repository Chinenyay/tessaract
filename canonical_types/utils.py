import pathlib

def get_file_extension(str_path: str):
    path_obj = pathlib.Path(str_path)
    suffix = path_obj.suffix
    return suffix