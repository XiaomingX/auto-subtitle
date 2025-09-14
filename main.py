import os
import ffmpeg
import whisper
import tempfile

def format_timestamp(seconds: float):
    """将秒数转换为SRT字幕格式的时间戳（时:分:秒,毫秒）"""
    assert seconds >= 0, "时间戳必须是非负数"
    milliseconds = round(seconds * 1000.0)
    
    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000
    
    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000
    
    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def write_srt(transcript, file):
    """将转录结果写入SRT文件"""
    for i, segment in enumerate(transcript, start=1):
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )

def get_filename(path):
    """从文件路径中提取不带扩展名的文件名"""
    return os.path.splitext(os.path.basename(path))[0]

def extract_audio(video_path, temp_dir):
    """从视频中提取音频并保存为临时WAV文件"""
    filename = get_filename(video_path)
    audio_path = os.path.join(temp_dir, f"{filename}.wav")
    
    # 使用ffmpeg提取音频，转为16kHz单声道PCM
    ffmpeg.input(video_path).output(
        audio_path,
        acodec="pcm_s16le",  # PCM 16位编码
        ac=1,                # 单声道
        ar="16k"             # 16kHz采样率
    ).run(quiet=True, overwrite_output=True)
    
    return audio_path

def generate_subtitles(audio_path, model, task, language):
    """使用Whisper模型生成字幕"""
    # 转录音频（或翻译）
    result = model.transcribe(audio_path, task=task, language=language)
    return result["segments"]

def add_subtitles_to_video(video_path, srt_path, output_path):
    """将字幕文件叠加到视频上"""
    # 输入视频和音频
    video = ffmpeg.input(video_path)
    audio = video.audio
    
    # 叠加字幕并合并音视频
    ffmpeg.concat(
        video.filter('subtitles', srt_path, force_style="OutlineColour=&H40000000,BorderStyle=3"),
        audio,
        v=1,  # 视频流数量
        a=1   # 音频流数量
    ).output(output_path).run(quiet=True, overwrite_output=True)

def main():
    # --------------------------
    # 配置参数（在此处修改设置）
    # --------------------------
    input_video = "input.mp4"       # 输入视频路径
    output_dir = "subtitled"       # 输出目录
    model_name = "small"           # 使用的模型（tiny, base, small, medium, large）
    output_srt = True              # 是否保存SRT字幕文件
    srt_only = False               # 是否只生成字幕不输出带字幕的视频
    task = "transcribe"            # 任务类型：transcribe（转录）或translate（翻译为英文）
    language = "auto"              # 视频语言，"auto"为自动检测
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载Whisper模型
    print(f"加载模型: {model_name}...")
    model = whisper.load_model(model_name)
    
    # 处理英文专用模型的情况
    if model_name.endswith(".en") and language == "auto":
        print("检测到英文专用模型，强制使用英文识别")
        language = "en"
    
    # 创建临时目录存储中间音频文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 提取音频
        print(f"从视频中提取音频: {input_video}")
        audio_path = extract_audio(input_video, temp_dir)
        
        # 2. 生成字幕
        print("正在生成字幕...（这可能需要一段时间）")
        segments = generate_subtitles(audio_path, model, task, language)
        
        # 3. 保存SRT字幕
        srt_filename = f"{get_filename(input_video)}.srt"
        srt_path = os.path.join(output_dir, srt_filename) if output_srt else os.path.join(temp_dir, srt_filename)
        
        with open(srt_path, "w", encoding="utf-8") as f:
            write_srt(segments, f)
        print(f"字幕已保存到: {srt_path}")
        
        # 4. 如果不需要生成带字幕的视频，直接结束
        if srt_only:
            print("已完成（仅生成字幕）")
            return
        
        # 5. 将字幕叠加到视频
        output_video = os.path.join(output_dir, f"{get_filename(input_video)}_subtitled.mp4")
        print(f"正在将字幕叠加到视频...")
        add_subtitles_to_video(input_video, srt_path, output_video)
        
        print(f"带字幕的视频已保存到: {output_video}")

if __name__ == '__main__':
    main()