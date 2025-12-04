# Runbat Maker

本项目旨在从当前目录读取 `.i` 或 `.inp` 文件，并根据这些文件的内容生成一个 `run.bat` 文件。

## 项目结构

```txt
runbat_maker
├── runbat_maker.py
├── README.md
└── requirements.txt
```

## 功能

- 扫描当前目录下的 `.i` 或 `.inp` 文件。
- 读取找到的文件内容。
- 使用输入文件的内容生成 `run.bat` 文件。

## 使用方法

1. 将你的 `.i` 或 `.inp` 文件放在与 `runbat_maker.exe` 相同的目录下。
2. 双击运行 `runbat_maker.exe` 或在终端中运行：

   ```bash
   ./runbat_maker.exe
   ```

3. 程序会自动生成 `run.bat` 文件。

## 注意事项

- 确保 `.i` 和 `.inp` 文件与 `runbat_maker.exe` 位于同一目录。
- 如果运行时提示未找到文件，请检查工作目录是否正确。
- 生成的 `run.bat` 文件内容示例：

  ```txt
  mcnp6.exe i=example.i o=example.o tasks 93
  del runtp*
  del src*
  pause
  ```
