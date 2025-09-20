import os
import sys

def main():
    set_working_directory()
    # 获取当前目录路径
    current_dir = os.getcwd()
#   print(f"当前工作目录: {current_dir}")
    
    # 获取文件名称列表
    files = os.listdir(current_dir)
#   print(f"目录中的文件: {files}")
    
    # 筛选出以 .i 或 .inp 结尾的文件
    target_files = [f for f in files if f.endswith('.i') or f.endswith('.inp')]
    
    if not target_files:
        print("没有找到 .i 或 .inp 文件。")
        input("按 Enter 键继续...")
        return

#   print(f"目标文件: {target_files}")
    # 生成 run.bat 文件
    generate_bat_file(target_files)

def generate_bat_file(target_files):
    with open('run.bat', 'w') as bat_file:
        for file_name in target_files:
            abs_path = os.path.abspath(file_name)
            if file_name.endswith('.i'):
                output_file = abs_path.replace('.i', '.o')
            else:  # file_name ends with '.inp'
                output_file = abs_path.replace('.inp', '.o')
            bat_file.write(f"mcnp6.exe i={abs_path} o={output_file} tasks 93\n")
            bat_file.write(f"del runtp*\n")
            bat_file.write(f"del src*\n")
        bat_file.write("pause\n")
    print("run.bat 文件已生成。")
    # 打印.bat 文件内容
    with open('run.bat', 'r') as bat_file:
        print(bat_file.read())
    input("按 Enter 键继续...")

def set_working_directory():
    # 将工作目录设置为当前脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

if __name__ == "__main__":
    main()