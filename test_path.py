def _to_wsl_path(win_path: str) -> str:
    if not win_path or not isinstance(win_path, str):
        return win_path
    if win_path[1:3] == ":\\":
        return f"/mnt/{win_path[0].lower()}/{win_path[3:].replace('\\\\', '/')}"
    return win_path.replace('\\\\', '/')

print(_to_wsl_path(r'C:\Users\akars\OneDrive\Desktop\Firmware Analysis workflow simulator\backend\data\projects\49_extraction\FST 2.3.13.0.msi_extracted\5000'))
