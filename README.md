# 为视频自动生成字幕

本仓库使用 `ffmpeg` 和 [OpenAI 的 Whisper](https://openai.com/blog/whisper) 工具，可自动为任意视频生成字幕并将其叠加到视频上。


## 安装步骤

开始使用前，你需要安装 Python 3.7 或更高版本。运行以下命令安装相关二进制文件：

    pip install git+https://github.com/xiaomingx/auto-subtitle.git

你还需要安装 [`ffmpeg`](https://ffmpeg.org/)，大多数包管理器中都可获取该工具：

```bash
# 在 Ubuntu 或 Debian 系统上
sudo apt update && sudo apt install ffmpeg

# 在 MacOS 系统上（需使用 Homebrew，安装地址：https://brew.sh/）
brew install ffmpeg

# 在 Windows 系统上（需使用 Chocolatey，安装地址：https://chocolatey.org/）
choco install ffmpeg
```


## 使用方法

运行以下命令，将生成一个 `subtitled/video.mp4` 文件，其中包含带有叠加字幕的输入视频：

    auto_subtitle /path/to/video.mp4 -o subtitled/

默认设置（选用 `small` 模型）适用于英文语音转写。你也可以选择更大的模型以获得更好的效果（对非英文语言尤其明显）。可选模型包括 `tiny`、`tiny.en`、`base`、`base.en`、`small`、`small.en`、`medium`、`medium.en`、`large`。

    auto_subtitle /path/to/video.mp4 --model medium

添加 `--task translate` 参数可将字幕翻译为英文：

    auto_subtitle /path/to/video.mp4 --task translate

运行以下命令可查看所有可用选项：

    auto_subtitle --help


## 许可证

本脚本为开源项目，基于 MIT 许可证授权。如需了解详细信息，请查看 [LICENSE](LICENSE) 文件。