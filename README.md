# Runbat Maker

Runbat Maker 会扫描指定目录中的 `.i` / `.inp`（MCNP 输入卡）并生成符合流水线约定的 `run.bat`，同时提供以下 Windows 集成功能：

- MCNP6 安装路径持久化到注册表 `HKCU\Software\RunbatMaker`，供右键菜单与运行逻辑复用。
- 一键注册/卸载目录与文件的右键菜单：“生成 run.bat” 与 “使用 MCNP6 运行”。
- 可选开机自启（空闲模式），保持 EXE 常驻待命。
- `scripts/install.ps1` / `scripts/uninstall.ps1` 自动化拷贝、配置及清理。

## 主要功能

- 在指定目录或单个文件上生成 `run.bat`，内容始终写入绝对路径以及 `tasks 93`、清理命令、`pause`（可参考 `test/run.bat`）。
- 输出的 `run.bat` 会使用当前系统 ANSI/代码页编码（`locale.getpreferredencoding(False)`），以便含中文路径的命令能在 `cmd.exe` / `mcnp6.exe` 下正确解析。
- 所有 `i=` / `o=` 参数都会自动带双引号，保证带空格或中括号的文件名照常运行。
- `--run-mcnp` 会将生成的 `run.bat` 复制到登记的 MCNP6 目录并在该目录中执行，确保 `mcnp6.exe` 可被找到。
- `--register-shell` / `--unregister-shell` 在 Explorer 中注册/移除四个右键项（目录+文件，生成+运行）。
- `--register-startup` / `--unregister-startup` 控制开机自启，启动命令会以 `--idle-service --silent` 方式运行并保持空闲。

## 安装流程

1. 使用 PyInstaller 打包：

   ```powershell
   pyinstaller runbat_maker.spec
   ```

1. 运行安装脚本（会拷贝 exe、写入 MCNP6 目录、注册右键菜单和开机启动）

- 要保证.ps1和.exe在同一目录下
- 直接运行install.ps1并输入:"path\to\MCNP6"

   如果不提供 `-MCNP6Path`，脚本会提示输入。默认安装目录：`%LOCALAPPDATA%\RunbatMaker`。

安装完成后，在资源管理器中可以：

- 对某个文件夹图标点击右键，看到“生成 run.bat / 运行 MCNP6”。
- 在文件夹空白处右键（Directory Background），同样会出现上述菜单并针对当前目录执行。

1. 如需卸载（移除注册表、右键菜单、开机启动并删除安装目录）：

   ```powershell
   pwsh ./uninstall.ps1
   ```

## 命令行参数

| 选项 | 说明 |
| --- | --- |
| `--dir <path>` | 扫描指定目录（默认使用当前目录）。 |
| `--input <path>` | 仅生成指定 `.i` / `.inp` 文件的命令行。 |
| `--run-mcnp` | 生成后复制 `run.bat` 至登记的 MCNP6 目录并执行。 |
| `--silent` | 抑制交互式 `Enter` 暂停（供右键与脚本调用）。 |
| `--set-mcnp-path <path>` | 将 MCNP6 安装目录写入注册表。 |
| `--show-mcnp-path` | 打印当前登记的 MCNP6 目录。 |
| `--register-shell` / `--unregister-shell` | 注册/卸载 Explorer 右键菜单。 |
| `--register-startup` / `--unregister-startup` | 注册/移除开机启动（调用 `--idle-service --silent`）。 |
| `--idle-service` | 进入空闲守候模式（被开机启动使用）。 |

多个维护指令可一次性组合执行；若仅执行维护操作将不会生成 `run.bat`。

## 手动使用示例

```powershell
# 在当前目录生成 run.bat
python runbat_maker.py

# 为指定目录生成并立即运行 MCNP6
runbat_maker.exe --dir "D:\work\case01" --run-mcnp --silent

# 为单个输入文件生成命令
runbat_maker.exe --input "D:\work\case01\deck.inp"
```

## 注意事项

- 始终写入绝对路径（上下游依赖此行为）。
- `tasks 93`、`del runtp*`、`del src*`、`pause` 的顺序不可打乱。
- 输入扫描仅限顶层目录；如需扩展为递归，请新增显式参数并更新文档与测试。
- Windows 注册表均写入 `HKCU`，不需要管理员权限；若 MCNP6 目录位于受保护路径，请以管理员身份运行安装脚本。

## 作者

| 角色 Role | 姓名 / ID | 负责模块 |
| --- | --- | --- |
| Owner | _ryy_ | 项目方向 / 架构 |
| Maintainer | _ryy_ | 安装脚本 / Shell 集成 |
| Contributor | _ryy_ | Feature/修复说明 |

## 联系方式

TEL：18186229445
EMAIL：<ren2321947887@qq.com>
