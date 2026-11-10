"""
Audio Transcription, Stream Downloader, and Session Audio Management for Tabletop Sessions.
Uses faster-whisper with CUDA GPU acceleration and yt-dlp.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
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

    CHUNK_DURATION_SEC = 1800  # 30-minute chunks to prevent RAM allocation bottlenecks on multi-hour recordings
    use_chunking = duration is not None and duration > CHUNK_DURATION_SEC
    temp_chunks_dir = None
    chunks_to_process: List[Tuple[Path, float]] = []

    if use_chunking:
        temp_chunks_dir = tempfile.mkdtemp(prefix="sr6_chunks_")
        chunk_pattern = os.path.join(temp_chunks_dir, "chunk_%03d.mp3")
        if not quiet:
            print(f"[Transcribe] Audio duration ({format_timestamp(duration)}) exceeds chunk threshold. Segmenting into {CHUNK_DURATION_SEC // 60}-minute chunks via ffmpeg...")
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(audio_file), "-f", "segment", "-segment_time", str(CHUNK_DURATION_SEC), "-c", "copy", chunk_pattern],
                capture_output=True,
                check=True
            )
            raw_chunks = sorted(Path(temp_chunks_dir).glob("chunk_*.mp3"))
            for cp in raw_chunks:
                cdur = get_audio_duration(str(cp)) or float(CHUNK_DURATION_SEC)
                chunks_to_process.append((cp, cdur))
            if not quiet:
                print(f"[Transcribe] Segmented into {len(chunks_to_process)} chunks successfully.")
        except Exception as e:
            if not quiet:
                print(f"[Transcribe] Warning: ffmpeg segmenting failed ({e}). Falling back to single-pass transcription.")
            chunks_to_process = [(audio_file, duration or 0.0)]
    else:
        chunks_to_process = [(audio_file, duration or 0.0)]

    t_start_transcribe = time.time()
    segments_data: List[Dict[str, Any]] = []
    md_lines: List[str] = []
    md_path = target_dir / "transcript.md"
    json_path = target_dir / "transcript.json"

    title = session_title or audio_file.stem
    detected_lang = "en"
    detected_prob = 1.0
    header_written = False

    md_file = open(md_path, "w", encoding="utf-8")

    try:
        current_offset = 0.0
        global_seg_id = 0
        last_logged_time = 0.0

        for chunk_idx, (chunk_path, chunk_dur) in enumerate(chunks_to_process, 1):
            if not quiet and len(chunks_to_process) > 1:
                print(f"\n[Transcribe] Processing Chunk {chunk_idx}/{len(chunks_to_process)}: {chunk_path.name} (offset: {format_timestamp(current_offset)})...")

            segments_iter, info = model.transcribe(str(chunk_path), beam_size=beam_size)

            if not header_written:
                detected_lang = info.language
                detected_prob = info.language_probability
                md_lines.append(f"# Session Transcript: {title}\n")
                if char_id:
                    md_lines.append(f"**Character Portfolio:** {char_id.capitalize()}  ")
                md_lines.append(f"**Source Audio:** `{audio_file.name}`  ")
                if duration:
                    md_lines.append(f"**Total Duration:** {format_timestamp(duration)}  ")
                md_lines.append(f"**Model Engine:** `faster-whisper` (`{model_size}`, {device.upper()})  ")
                md_lines.append(f"**Language Detected:** {detected_lang} (probability: {detected_prob:.2f})\n")
                md_file.writelines(md_lines)
                md_file.flush()
                header_written = True

            for segment in segments_iter:
                seg_start = current_offset + segment.start
                seg_end = current_offset + segment.end
                seg_dict = {
                    "id": global_seg_id,
                    "start": seg_start,
                    "end": seg_end,
                    "start_ts": format_timestamp(seg_start),
                    "end_ts": format_timestamp(seg_end),
                    "text": segment.text.strip(),
                    "avg_logprob": segment.avg_logprob,
                    "no_speech_prob": segment.no_speech_prob
                }
                global_seg_id += 1
                segments_data.append(seg_dict)

                md_line = f"**[{seg_dict['start_ts']} -> {seg_dict['end_ts']}]** {seg_dict['text']}\n"
                md_file.write(md_line)
                md_file.flush()

                # Periodic console progress update every 30 seconds of audio processed
                if not quiet and (seg_end - last_logged_time >= 30.0 or last_logged_time == 0.0):
                    last_logged_time = seg_end
                    percent_str = f" ({seg_end / duration * 100:.1f}%)" if duration and duration > 0 else ""
                    elapsed = time.time() - t_start_transcribe
                    print(f"  [Progress] {format_timestamp(seg_end)}{percent_str} | Elapsed: {int(elapsed)}s | Text: {seg_dict['text'][:60]}...")

            current_offset += chunk_dur

    finally:
        md_file.close()
        if temp_chunks_dir and os.path.exists(temp_chunks_dir):
            shutil.rmtree(temp_chunks_dir, ignore_errors=True)

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
        "language": detected_lang,
        "language_probability": detected_prob,
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
