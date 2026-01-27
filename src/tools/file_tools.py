from pathlib import Path
from src.tools.sandbox_tools import ensure_safe_path

def read_file(path: Path) -> str:
    """
    Read a file safely. Path MUST be inside sandbox/. and u gotta loop through the folders files 
    and each time extract the path and give it to the folder , ill give u the function that does this below :)
    """
    safe_path = ensure_safe_path(path)

    with open(safe_path, "r", encoding="utf-8") as f:
        return f.read()



def write_file(path: Path, content: str) -> None:
    """
    Write content to a file safely inside sandbox.
    Creates parent directories if they do not exist.
    """
    safe_path = ensure_safe_path(path) 
    # """
    # ensures the path u passed is inside the sandbox
    # safe_path.parent.mkdir(parents=True, exist_ok=True) if u pass a path but the parents dont exist, 
    # it creates them 
    # """

    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(content)



def list_python_files(folder_path: Path) -> list[Path]:
    """
    Return a list of all Python files (.py) in the given folder.
    """
    safe_folder = ensure_safe_path(folder_path)
    return [f for f in safe_folder.glob("*.py") if f.is_file()]  
    # """ so u can loop through the files in the passed folder
    # ill give an example , u the robot passes the folder within the argument u would do 
    # target_dir_str = args.target_dir   # str
    #  target_dir = Path(target_dir_str)  # convert it to path type , call the function files=list_python_files(target_dir)
    #  files here is a list of paths , then u would do for files_path in files : content=read_files(files_path) and work on the files 
    
    # """
