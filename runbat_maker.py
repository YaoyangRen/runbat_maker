import argparse
import locale
import os
import subprocess
import sys
import time
from types import ModuleType
from typing import List, Optional

REG_APP_BASE = r"Software\RunbatMaker"
REG_MCNPPATH_VALUE = "MCNP6Path"
REG_STARTUP = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_STARTUP_VALUE = "RunbatMaker"
SHELL_DEFINITIONS = {
    "dir_generate": (
        r"Software\Classes\Directory\shell\RunbatMaker_Generate",
        "生成 run.bat",
        "--dir \"%V\" --silent"
    ),
    "dir_run": (
        r"Software\Classes\Directory\shell\RunbatMaker_Run",
        "运行 MCNP6",
        "--dir \"%V\" --silent --run-mcnp"
    ),
    "dir_bg_generate": (
        r"Software\Classes\Directory\Background\shell\RunbatMaker_GenerateHere",
        "在此目录生成 run.bat",
        "--dir \"%V\" --silent"
    ),
    "dir_bg_run": (
        r"Software\Classes\Directory\Background\shell\RunbatMaker_RunHere",
        "在此目录运行 MCNP6",
        "--dir \"%V\" --silent --run-mcnp"
    ),
    "file_generate": (
        r"Software\Classes\*\shell\RunbatMaker_Generate",
        "为此文件生成 run.bat",
        "--input \"%1\" --silent"
    ),
    "file_run": (
        r"Software\Classes\*\shell\RunbatMaker_Run",
        "使用 MCNP6 运行",
        "--input \"%1\" --silent --run-mcnp"
    ),
}


def main():
    set_working_directory()
    args = parse_args()

    if args.idle_service:
        run_idle_service()
        return

    maintenance_executed = False

    if args.set_mcnp_path:
        set_mcnp_path(args.set_mcnp_path)
        maintenance_executed = True

    if args.show_mcnp_path:
        show_mcnp_path()
        maintenance_executed = True

    if args.register_shell:
        register_shell_entries()
        maintenance_executed = True

    if args.unregister_shell:
        unregister_shell_entries()
        maintenance_executed = True

    if args.register_startup:
        register_startup()
        maintenance_executed = True

    if args.unregister_startup:
        unregister_startup()
        maintenance_executed = True

    # 如果只执行维护操作且没有指定生成任务，则直接返回
    if maintenance_executed and not (args.input or args.dir):
        return

    run_generation_flow(args)


def run_generation_flow(args: argparse.Namespace) -> None:
    if args.input and args.dir:
        print("`--input` 与 `--dir` 不能同时使用。请选择其一。")
        return

    if args.input:
        if not os.path.isfile(args.input):
            print(f"未找到指定文件: {args.input}")
            return
        target_files = [os.path.abspath(args.input)]
        output_dir = os.path.dirname(target_files[0])
    else:
        target_dir = os.path.abspath(args.dir) if args.dir else os.getcwd()
        if not os.path.isdir(target_dir):
            print(f"未找到指定目录: {target_dir}")
            return
        target_files = collect_input_files(target_dir)
        output_dir = target_dir

    if not target_files:
        print("没有找到 .i 或 .inp 文件。")
        pause_if_needed(args.silent)
        return

    run_bat_path = generate_bat_file(target_files, output_dir)
    print(f"run.bat 文件已生成: {run_bat_path}")
    display_bat_contents(run_bat_path)

    if args.run_mcnp:
        copy_and_run(run_bat_path)

    pause_if_needed(args.silent)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runbat Maker 实用工具")
    parser.add_argument("--dir", help="指定需要扫描的目录")
    parser.add_argument("--input", help="只处理单个 .i/.inp 文件")
    parser.add_argument("--silent", action="store_true", help="抑制交互式暂停")
    parser.add_argument("--run-mcnp", action="store_true", help="生成 run.bat 后复制到 MCNP6 目录并运行")
    parser.add_argument("--set-mcnp-path", help="写入 MCNP6 安装目录 (存储在注册表)")
    parser.add_argument("--show-mcnp-path", action="store_true", help="打印已存储的 MCNP6 路径")
    parser.add_argument("--register-shell", action="store_true", help="注册右键菜单")
    parser.add_argument("--unregister-shell", action="store_true", help="移除右键菜单")
    parser.add_argument("--register-startup", action="store_true", help="将程序加入开机启动 (空闲服务模式)")
    parser.add_argument("--unregister-startup", action="store_true", help="移除开机启动设置")
    parser.add_argument("--idle-service", action="store_true", help="以空闲模式运行 (供自动启动使用)")
    return parser.parse_args()


def collect_input_files(target_dir: str) -> List[str]:
    files = []
    for entry in os.listdir(target_dir):
        if entry.lower().endswith((".i", ".inp")):
            files.append(os.path.abspath(os.path.join(target_dir, entry)))
    return files


def generate_bat_file(target_files: List[str], output_dir: str) -> str:
    output_path = os.path.join(output_dir, "run.bat")
    encoding = locale.getpreferredencoding(False) or "utf-8"
    with open(output_path, "w", encoding=encoding, errors="replace") as bat_file:
        for abs_path in target_files:
            base, ext = os.path.splitext(abs_path)
            output_file = f"{base}.o"
            bat_file.write(f"mcnp6.exe i={abs_path} o={output_file} tasks 93\n")
            bat_file.write("del runtp*\n")
            bat_file.write("del src*\n")
        bat_file.write("pause\n")
    return output_path


def display_bat_contents(path: str) -> None:
    encoding = locale.getpreferredencoding(False) or "utf-8"
    try:
        with open(path, "r", encoding=encoding, errors="replace") as bat_file:
            print(bat_file.read())
    except OSError as exc:
        print(f"无法读取 {path}: {exc}")


def pause_if_needed(silent: bool) -> None:
    if not silent:
        input("按 Enter 键继续...")


def get_winreg_module() -> ModuleType:
    try:
        import winreg  # type: ignore
    except ImportError as exc:  # pragma: no cover - 非 Windows 环境不会运行
        raise EnvironmentError("当前环境不支持 Windows 注册表操作。") from exc
    return winreg


def set_mcnp_path(path: str) -> None:
    winreg = get_winreg_module()
    if not os.path.isdir(path):
        print(f"MCNP6 目录无效: {path}")
        return
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_APP_BASE)
    winreg.SetValueEx(key, REG_MCNPPATH_VALUE, 0, winreg.REG_SZ, os.path.abspath(path))
    winreg.CloseKey(key)
    print(f"MCNP6 目录已保存到注册表: {os.path.abspath(path)}")


def show_mcnp_path() -> None:
    winreg = get_winreg_module()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_APP_BASE)
        value, _ = winreg.QueryValueEx(key, REG_MCNPPATH_VALUE)
        winreg.CloseKey(key)
        print(f"当前 MCNP6 路径: {value}")
    except FileNotFoundError:
        print("尚未设置 MCNP6 路径。使用 --set-mcnp-path 进行配置。")


def get_mcnp_path() -> Optional[str]:
    winreg = get_winreg_module()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_APP_BASE)
        value, _ = winreg.QueryValueEx(key, REG_MCNPPATH_VALUE)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None


def copy_and_run(run_bat_path: str) -> None:
    mcnp_path = get_mcnp_path()
    if not mcnp_path:
        print("未找到 MCNP6 路径，请先执行 --set-mcnp-path。")
        return
    if not os.path.isdir(mcnp_path):
        print(f"登记的 MCNP6 目录无效: {mcnp_path}")
        return
    destination = os.path.join(mcnp_path, "run.bat")
    try:
        import shutil

        shutil.copy(run_bat_path, destination)
        print(f"已复制 run.bat 至 {destination}")
    except OSError as exc:
        print(f"复制 run.bat 失败: {exc}")
        return

    try:
        subprocess.run(["cmd", "/c", "run.bat"], cwd=mcnp_path, check=False)
    except OSError as exc:
        print(f"运行 run.bat 失败: {exc}")


def register_shell_entries() -> None:
    winreg = get_winreg_module()
    exe_path = os.path.abspath(sys.argv[0])
    for entry in SHELL_DEFINITIONS.values():
        reg_path, menu_text, args = entry
        command = f'"{exe_path}" {args}'
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, menu_text)
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
        cmd_key = winreg.CreateKey(key, "command")
        winreg.SetValueEx(cmd_key, None, 0, winreg.REG_SZ, command)
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)
    print("右键菜单已注册。")


def unregister_shell_entries() -> None:
    winreg = get_winreg_module()
    for entry in SHELL_DEFINITIONS.values():
        reg_path = entry[0]
        delete_registry_tree(winreg.HKEY_CURRENT_USER, reg_path, winreg)
    print("右键菜单已移除 (如存在)。")


def register_startup() -> None:
    winreg = get_winreg_module()
    exe_path = os.path.abspath(sys.argv[0])
    command = f'"{exe_path}" --idle-service --silent'
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_STARTUP, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, REG_STARTUP_VALUE, 0, winreg.REG_SZ, command)
    winreg.CloseKey(key)
    print("已加入开机启动。")


def unregister_startup() -> None:
    winreg = get_winreg_module()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_STARTUP, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, REG_STARTUP_VALUE)
        winreg.CloseKey(key)
        print("已移除开机启动设置。")
    except FileNotFoundError:
        print("未找到开机启动设置。")
    except OSError:
        print("开机启动配置不存在或无法删除。")


def delete_registry_tree(root, subkey: str, winreg_module: Optional[ModuleType] = None) -> None:
    winreg = winreg_module or get_winreg_module()
    try:
        key = winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        return

    while True:
        try:
            child = winreg.EnumKey(key, 0)
            delete_registry_tree(root, f"{subkey}\\{child}", winreg)
        except OSError:
            break
    winreg.CloseKey(key)
    try:
        winreg.DeleteKey(root, subkey)
    except OSError:
        pass


def run_idle_service() -> None:
    print("Runbat Maker 已在后台待命，等待右键调用。按 Ctrl+C 退出。")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("已退出空闲模式。")


def set_working_directory():
    # 将工作目录设置为当前脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))


if __name__ == "__main__":
    main()