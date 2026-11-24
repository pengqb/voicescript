voice_script项目

识别MP3，生成带时间的语音脚本。

## 安装

程序说明

- 核心程序：[transcribe.py](qoder-app://renderer/Users/pengqiangbing/work/auto/transcribe.py)
- 依赖清单：[requirements.txt](qoder-app://renderer/Users/pengqiangbing/work/auto/requirements.txt)
- macOS/Linux：[setup.sh](qoder-app://renderer/Users/pengqiangbing/work/auto/setup.sh)、[run.sh](qoder-app://renderer/Users/pengqiangbing/work/auto/run.sh)
- Windows：[setup.bat](qoder-app://renderer/Users/pengqiangbing/work/auto/setup.bat)、[run.bat](qoder-app://renderer/Users/pengqiangbing/work/auto/run.bat)

## macOS / Linux

建议使用 Python 3.12。进入源码目录后执行：

```
cd "/path/to/auto"
chmod +x setup.sh run.sh
# ./setup.sh
PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple" ./setup.sh
PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/" ./setup.sh
PIP_INDEX_URL="https://repo.huaweicloud.com/repository/pypi/simple" ./setup.sh
./run.sh "/path/to/audio.mp3"
```

 重新安装

```
rm -rf .venv
PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple" ./setup.sh
```



## Windows

安装 Python 3 时保留 **Python Launcher（py）**。然后在命令提示符中执行：

```
cd /d "C:\path\to\auto"setup.batrun.bat "C:\path\to\audio.mp3"
```

PowerShell 中则使用：

```
cd "C:\path\to\auto".\setup.bat.\run.bat "C:\path\to\audio.mp3"
```

安装脚本会在目标系统重新创建 `.venv`、安装依赖并检查 Python 语法。首次识别需要联网下载约 460 MB 的模型，之后可以离线运行。



## 使用

默认输出到 MP3 同目录，文件名为 `原文件名_transcript.txt`。指定输出或时间轴的方式不变：

```
./run.sh "audio.mp3" -o "result.txt" --timestamps
```

可以下载本地模型

```
models/faster-whisper-small.en/
├── config.json
├── model.bin
├── tokenizer.json
└── vocabulary.txt

cd "/path/to/auto"
mkdir -p models/faster-whisper-small.en
cd models/faster-whisper-small.en
 
wget -c "https://hf-mirror.com/Systran/faster-whisper-small.en/resolve/main/config.json"
wget -c "https://hf-mirror.com/Systran/faster-whisper-small.en/resolve/main/model.bin"
wget -c "https://hf-mirror.com/Systran/faster-whisper-small.en/resolve/main/tokenizer.json"
wget -c "https://hf-mirror.com/Systran/faster-whisper-small.en/resolve/main/vocabulary.txt"
```

指定本地模型运行, 也可指定更大的模型，修改-m 参数即可。

```
cd "/path/to/auto"
 
./run.sh "Review1-3.mp3" \
  -m "/app/models/faster-whisper-small.en" \
  -o "result.txt" \
  --timestamps
```



Windows 对应为：

```
run.bat "audio.mp3" -o "result.txt" --timestamps
```

