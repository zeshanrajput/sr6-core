"""
Audio Transcription, Stream Downloader, and Session Audio Management for Tabletop Sessions.
Uses faster-whisper with CUDA GPU acceleration and yt-dlp.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator, Tuple


def setup_cuda_dlls() -> bool:
    """
    On Windows, ensures PyTorch CUDA DLL directories (cublas, cudnn, etc.)
    are added to os.add_dll_directory and PATH so that CTranslate2 can load them.
    """
    if sys.platform != "win32":
        return True

    success = False
    try:
        import torch
        torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
        if os.path.exists(torch_lib):
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(torch_lib)
                    success = True
                except Exception:
                    pass
            os.environ["PATH"] = torch_lib + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass
    return success


def format_timestamp(seconds: float) -> str:
    """Formats seconds into [HH:MM:SS]."""
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_audio_duration(audio_path: str) -> Optional[float]:
    """Retrieves audio duration in seconds using mutagen or av."""
    try:
        from mutagen.mp3 import MP3
        audio = MP3(audio_path)
        return float(audio.info.length)
    except Exception:
        pass

    try:
        import av
        with av.open(audio_path) as container:
            stream = container.streams.audio[0]
            if stream.duration and stream.time_base:
                return float(stream.duration * stream.time_base)
    except Exception:
        pass

    return None


def transcribe_session_audio(
    audio_path: str,
    model_size: str = "small.en",
    device: Optional[str] = None,
    compute_type: Optional[str] = None,
    beam_size: int = 5,
    output_dir: Optional[str] = None,
    session_title: Optional[str] = None,
    char_id: Optional[str] = None,
    quiet: bool = False
) -> Dict[str, Any]:
    """
    Transcribes a session audio recording using faster-whisper on CUDA/CPU.
    Outputs both Markdown (transcript.md) and JSON (transcript.json).
    """
    setup_cuda_dlls()

    import torch
    from faster_whisper import WhisperModel

    audio_file = Path(audio_path).resolve()
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if compute_type is None:
        compute_type = "float16" if device == "cuda" else "int8"

    if output_dir is None:
        target_dir = audio_file.parent
    else:
        target_dir = Path(output_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

    duration = get_audio_duration(str(audio_file))
    duration_str = f" ({format_timestamp(duration)})" if duration else ""

    if not quiet:
        print(f"\n[Transcribe] Initializing faster-whisper model: {model_size} on {device.upper()} ({compute_type})")
        print(f"[Transcribe] Processing: {audio_file.name}{duration_str}")

    t_start_model = time.time()
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    t_model_loaded = time.time() - t_start_model

    if not quiet:
        print(f"[Transcribe] Model loaded in {t_model_loaded:.2f}s. Beginning decoding...")

    t_start_transcribe = time.time()
    segments_iter, info = model.transcribe(str(audio_file), beam_size=beam_size)

    segments_data: List[Dict[str, Any]] = []
    md_lines: List[str] = []

    title = session_title or audio_file.stem
    md_lines.append(f"# Session Transcript: {title}\n")
    if char_id:
        md_lines.append(f"**Character Portfolio:** {char_id.capitalize()}  ")
    md_lines.append(f"**Source Audio:** `{audio_file.name}`  ")
    if duration:
        md_lines.append(f"**Total Duration:** {format_timestamp(duration)}  ")
    md_lines.append(f"**Model Engine:** `faster-whisper` (`{model_size}`, {device.upper()})  ")
    md_lines.append(f"**Language Detected:** {info.language} (probability: {info.language_probability:.2f})\n")
    md_path = target_dir / "transcript.md"
    json_path = target_dir / "transcript.json"

    # Start writing transcript.md immediately and flush incrementally
    md_file = open(md_path, "w", encoding="utf-8")
    md_file.writelines(md_lines)
    md_file.flush()

    last_logged_time = 0.0
    for segment in segments_iter:
        seg_dict = {
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "start_ts": format_timestamp(segment.start),
            "end_ts": format_timestamp(segment.end),
            "text": segment.text.strip(),
            "avg_logprob": segment.avg_logprob,
            "no_speech_prob": segment.no_speech_prob
        }
        segments_data.append(seg_dict)

        md_line = f"**[{seg_dict['start_ts']} -> {seg_dict['end_ts']}]** {seg_dict['text']}\n"
        md_file.write(md_line)
        md_file.flush()

        # Periodic console progress update every 30 seconds of audio processed
        if not quiet and (segment.end - last_logged_time >= 30.0 or last_logged_time == 0.0):
            last_logged_time = segment.end
            percent_str = f" ({segment.end / duration * 100:.1f}%)" if duration and duration > 0 else ""
            elapsed = time.time() - t_start_transcribe
            print(f"  [Progress] {format_timestamp(segment.end)}{percent_str} | Elapsed: {int(elapsed)}s | Text: {seg_dict['text'][:60]}...")

    md_file.close()

    total_time = time.time() - t_start_transcribe
    speed_factor = (duration / total_time) if duration and total_time > 0 else 0.0

    summary_data = {
        "title": title,
        "character": char_id,
        "audio_file": str(audio_file),
        "duration_seconds": duration,
        "duration_formatted": format_timestamp(duration) if duration else None,
        "model": model_size,
        "device": device,
        "compute_type": compute_type,
        "transcription_time_seconds": total_time,
        "speed_factor": f"{speed_factor:.2f}x realtime" if speed_factor else None,
        "language": info.language,
        "language_probability": info.language_probability,
        "segment_count": len(segments_data),
        "segments": segments_data
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    if not quiet:
        print(f"\n[Transcribe] Completed in {total_time:.2f}s ({speed_factor:.2f}x realtime)!")
        print(f"[Transcribe] Markdown transcript written to: {md_path}")
        print(f"[Transcribe] JSON transcript written to:     {json_path}\n")

    return summary_data


def download_session_audio(
    url: str,
    output_dir: str,
    filename_stem: Optional[str] = None,
    quiet: bool = False
) -> str:
    """
    Downloads audio from a URL (YouTube, Twitch, Discord stream, etc.)
    using yt-dlp and converts to 160k MP3.
    Returns the path to the downloaded MP3.
    """
    import yt_dlp

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = filename_stem or "%(title)s"
    out_template = str(out_dir / f"{stem}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "160",
        }],
        "outtmpl": out_template,
        "quiet": quiet,
        "no_warnings": quiet
    }

    if not quiet:
        print(f"[Download] Fetching audio from: {url}")
        print(f"[Download] Target directory: {out_dir}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_path = Path(filename).with_suffix(".mp3")

    if not quiet:
        print(f"[Download] Successfully saved to: {mp3_path}")

    return str(mp3_path)
