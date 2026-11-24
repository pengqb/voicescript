#!/usr/bin/env python3
"""Transcribe an English MP3 file to a UTF-8 text file."""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = "small.en"

# Model files stay with the program. The mirror can be overridden before running:
# HF_ENDPOINT=https://huggingface.co ./run.sh input.mp3
os.environ.setdefault("HF_HOME", str(APP_DIR / ".cache" / "huggingface"))
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "30")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "60")


class TranscriptionError(RuntimeError):
    """An error that can be shown to the user without a traceback."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将英语 MP3 听力音频转写为 UTF-8 文本（本地识别，不上传音频）。"
    )
    parser.add_argument("input", type=Path, help="输入 MP3 文件路径")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="输出文本路径；默认为输入文件同目录下的“文件名_transcript.txt”",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        help=f"Whisper 模型，默认 {DEFAULT_MODEL}；也可使用 base.en、medium.en 等",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="识别搜索宽度，默认 5；调大可能提高准确率，但更耗时",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="在每段文字前保留开始和结束时间",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="允许覆盖已经存在的输出文件",
    )
    args = parser.parse_args()
    if args.beam_size < 1:
        parser.error("--beam-size 必须是大于或等于 1 的整数")
    return args


def decode_mp3(input_path: Path):
    """Decode MP3 to mono 16 kHz float PCM with PyAV's bundled FFmpeg."""
    try:
        import av
        import numpy as np
    except ImportError as exc:
        raise TranscriptionError("缺少依赖，请先运行安装脚本。") from exc

    raw_buffer = io.BytesIO()
    try:
        with av.open(str(input_path), mode="r") as container:
            if not container.streams.audio:
                raise TranscriptionError("MP3 文件中没有音频流。")
            resampler = av.audio.resampler.AudioResampler(
                format="s16", layout="mono", rate=16000
            )
            for frame in container.decode(audio=0):
                for converted in resampler.resample(frame):
                    raw_buffer.write(converted.to_ndarray().tobytes())
            # Flush samples buffered by the resampler at the end of the stream.
            for converted in resampler.resample(None):
                raw_buffer.write(converted.to_ndarray().tobytes())
    except TranscriptionError:
        raise
    except Exception as exc:
        raise TranscriptionError(f"MP3 解码失败：{exc}") from exc

    if raw_buffer.tell() == 0:
        raise TranscriptionError("音频中没有可识别的声音数据。")
    pcm = np.frombuffer(raw_buffer.getbuffer(), dtype="<i2")
    return pcm.astype(np.float32) / 32768.0


def format_timestamp(seconds: float) -> str:
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def prepare_model(model_name: str) -> str:
    """Download a model with visible progress, or return its cached/local path."""
    try:
        from faster_whisper.utils import _MODELS
        from huggingface_hub import snapshot_download
        from tqdm import tqdm
    except ImportError as exc:
        raise TranscriptionError("缺少依赖，请先运行安装脚本。") from exc

    if Path(model_name).is_dir():
        return model_name
    repo_id = _MODELS.get(model_name, model_name)
    if "/" not in repo_id:
        raise TranscriptionError(f"未知模型：{model_name}")

    print(
        f"正在检查模型 {model_name}；如需下载，将显示文件和字节进度……",
        file=sys.stderr,
        flush=True,
    )
    return snapshot_download(
        repo_id=repo_id,
        allow_patterns=[
            "config.json",
            "preprocessor_config.json",
            "model.bin",
            "tokenizer.json",
            "vocabulary.*",
        ],
        # faster-whisper disables this progress bar internally, so enable it here.
        tqdm_class=tqdm,
    )


def transcribe(audio, model_name: str, beam_size: int, timestamps: bool) -> tuple[str, float]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise TranscriptionError("缺少依赖，请先运行 ./setup.sh。") from exc

    try:
        model_path = prepare_model(model_name)
        print(f"正在加载模型 {model_name}……", file=sys.stderr, flush=True)
        model = WhisperModel(
            model_path,
            device="cpu",
            compute_type="int8",
            cpu_threads=min(4, os.cpu_count() or 1),
        )
    except Exception as exc:
        raise TranscriptionError(
            f"模型下载或加载失败：{exc}\n"
            "请检查网络后重试；也可以设置 HF_ENDPOINT=https://huggingface.co 后重试。"
        ) from exc

    print("正在识别英语语音……", file=sys.stderr)
    try:
        segments, info = model.transcribe(
            audio,
            language="en",
            beam_size=beam_size,
            vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt="English listening comprehension exercises for elementary school students.",
        )
        lines: list[str] = []
        for segment in segments:
            text = segment.text.strip()
            if not text:
                continue
            if timestamps:
                lines.append(
                    f"[{format_timestamp(segment.start)} --> "
                    f"{format_timestamp(segment.end)}] {text}"
                )
            else:
                lines.append(text)
            print(lines[-1], flush=True)
    except Exception as exc:
        raise TranscriptionError(f"语音识别失败：{exc}") from exc

    if not lines:
        raise TranscriptionError("没有识别出英语语音，请检查音频内容和音量。")
    return "\n".join(lines) + "\n", info.duration


def main() -> int:
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    output_path = (
        args.output.expanduser().resolve()
        if args.output
        else input_path.with_name(f"{input_path.stem}_transcript.txt")
    )

    try:
        if not input_path.is_file():
            raise TranscriptionError(f"输入文件不存在：{input_path}")
        if input_path.suffix.lower() != ".mp3":
            raise TranscriptionError("输入文件必须是 .mp3 格式。")
        if input_path == output_path:
            raise TranscriptionError("输出文件不能覆盖输入 MP3。")
        if output_path.exists() and not args.overwrite:
            raise TranscriptionError(
                f"输出文件已存在：{output_path}\n请使用 -o 指定其他路径，或添加 --overwrite。"
            )
        if not output_path.parent.is_dir():
            raise TranscriptionError(f"输出目录不存在：{output_path.parent}")

        audio = decode_mp3(input_path)
        text, duration = transcribe(
            audio, args.model, args.beam_size, args.timestamps
        )
        output_path.write_text(text, encoding="utf-8")
    except TranscriptionError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"文件操作失败：{exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130

    print(f"\n识别完成：音频时长 {duration:.1f} 秒", file=sys.stderr)
    print(f"文本已保存：{output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
