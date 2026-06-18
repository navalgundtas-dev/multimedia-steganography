"""
Voice-specific steganography utilities that embed payloads inside voiced frames
of mono 16-bit WAV recordings using an LSB strategy guided by a lightweight VAD.
"""
import os
import struct
import wave
from typing import Dict, Optional, Tuple

import numpy as np

from .crypto import encrypt_data, decrypt_data


class VoiceSteganography:
    """Speech-aware audio steganography."""

    def __init__(self):
        self.max_file_size = 30 * 1024 * 1024  # 30MB
        self.supported_formats = ('.wav',)
        self.min_sample_rate = 16000
        self.min_duration_seconds = 2.0
        self.energy_factor = 1.1
        self.last_report: Dict[str, float] = {}

    def _load_voice(self, voice_path: str) -> Tuple[np.ndarray, wave._wave_params]:
        """Load mono 16-bit PCM WAV samples."""
        if not os.path.exists(voice_path):
            raise FileNotFoundError("Voice recording not found")

        with wave.open(voice_path, 'rb') as voice_in:
            params = voice_in.getparams()
            frames = voice_in.getnframes()
            audio_bytes = voice_in.readframes(frames)

        if params.sampwidth != 2:
            raise ValueError("Only 16-bit PCM WAV files are supported")

        if params.nchannels != 1:
            raise ValueError("Please provide mono voice recordings")

        samples = np.frombuffer(audio_bytes, dtype=np.int16).copy()
        return samples, params

    def _detect_voice_regions(self, samples: np.ndarray) -> np.ndarray:
        """Return boolean mask highlighting voiced samples."""
        if samples.size == 0:
            return np.zeros(0, dtype=bool)

        amplitude = np.abs(samples).astype(np.float32)
        window = max(1, int(0.02 * len(samples)))  # 20 ms approximation
        kernel = np.ones(window) / window
        smoothed = np.convolve(amplitude, kernel, mode='same')

        adaptive_threshold = max(float(smoothed.mean() * self.energy_factor), 150.0)
        mask = smoothed >= adaptive_threshold

        if mask.sum() < len(samples) * 0.03:
            percentile_threshold = max(float(np.percentile(smoothed, 85)), 100.0)
            mask = smoothed >= percentile_threshold

        if mask.sum() == 0:
            mask = smoothed > 0

        return mask

    def _store_report(self, report: Dict[str, float]) -> None:
        self.last_report = report

    def get_last_report(self) -> Dict[str, float]:
        return dict(self.last_report) if self.last_report else {}

    def validate_voice(self, voice_path: str) -> Tuple[bool, str]:
        """Ensure the supplied voice file is suitable for steganography."""
        try:
            if not os.path.exists(voice_path):
                return False, "Voice file not found"

            if not voice_path.lower().endswith(self.supported_formats):
                return False, "Unsupported format. Only WAV files are supported for voice steganography"

            file_size = os.path.getsize(voice_path)
            if file_size > self.max_file_size:
                return False, f"File too large. Max size is {self.max_file_size // (1024 * 1024)}MB"

            with wave.open(voice_path, 'rb') as voice_in:
                params = voice_in.getparams()
                frames = voice_in.getnframes()

                if params.sampwidth != 2:
                    return False, "Only 16-bit PCM WAV files are supported"

                if params.nchannels != 1:
                    return False, "Please upload mono voice recordings"

                if params.framerate < self.min_sample_rate:
                    return False, f"Sample rate too low. Minimum required is {self.min_sample_rate}Hz"

                duration = frames / params.framerate
                if duration < self.min_duration_seconds:
                    return False, f"Recording too short. Minimum duration is {self.min_duration_seconds} seconds"

            return True, ""

        except wave.Error as exc:
            return False, f"Invalid WAV file: {str(exc)}"
        except Exception as exc:
            return False, f"Validation failed: {str(exc)}"

    def embed_data(
        self,
        cover_voice_path: str,
        secret_data: bytes,
        password: str,
        output_path: str,
    ) -> bool:
        """Embed payload inside voiced regions."""
        try:
            samples, params = self._load_voice(cover_voice_path)

            mask = self._detect_voice_regions(samples)
            voice_indices = np.flatnonzero(mask)
            available_bits = len(voice_indices)
            capacity_bytes = available_bits // 8

            encrypted_data = encrypt_data(secret_data, password)
            payload = struct.pack('>I', len(encrypted_data)) + encrypted_data
            binary_payload = ''.join(f"{byte:08b}" for byte in payload) + '1' * 32

            if len(binary_payload) > available_bits:
                raise ValueError(
                    f"Secret data too large for voiced capacity. "
                    f"Available ≈ {capacity_bytes} bytes"
                )

            for bit_idx, sample_idx in enumerate(voice_indices[: len(binary_payload)]):
                bit = int(binary_payload[bit_idx])
                samples[sample_idx] = (samples[sample_idx] & ~1) | bit

            with wave.open(output_path, 'wb') as voice_out:
                voice_out.setparams(params)
                voice_out.writeframes(samples.tobytes())

            voice_ratio = len(voice_indices) / len(samples) if len(samples) else 0
            duration = len(samples) / params.framerate if params.framerate else 0

            self._store_report(
                {
                    'mode': 'embed',
                    'duration_seconds': round(duration, 2),
                    'total_samples': int(len(samples)),
                    'voiced_samples': int(len(voice_indices)),
                    'voice_ratio': round(voice_ratio, 3),
                    'capacity_bytes': int(capacity_bytes),
                    'payload_bytes': int(len(payload)),
                    'technique': 'Voiced-frame LSB + AES encryption',
                }
            )

            return True

        except Exception as exc:
            print(f"Voice embedding failed: {str(exc)}")
            return False

    def extract_data(self, stego_voice_path: str, password: str) -> Optional[bytes]:
        """Recover payload from voiced regions."""
        try:
            samples, params = self._load_voice(stego_voice_path)
            mask = self._detect_voice_regions(samples)
            voice_indices = np.flatnonzero(mask)

            if len(voice_indices) < 64:
                raise ValueError("Not enough voiced samples to decode payload")

            end_marker = ['1'] * 32
            bits = []
            found_marker = False

            for idx in voice_indices:
                bits.append('1' if (samples[idx] & 1) else '0')
                if len(bits) >= 32 and bits[-32:] == end_marker:
                    bits = bits[:-32]
                    found_marker = True
                    break

            if not found_marker:
                raise ValueError("Could not locate embedded payload in voiced frames")

            binary_str = ''.join(bits)
            extracted = bytearray()

            for offset in range(0, len(binary_str), 8):
                byte = binary_str[offset : offset + 8]
                if len(byte) == 8:
                    extracted.append(int(byte, 2))

            if len(extracted) < 4:
                raise ValueError("Corrupted payload header")

            payload_length = struct.unpack('>I', extracted[:4])[0]
            if payload_length <= 0 or payload_length > len(extracted) - 4:
                raise ValueError("Invalid payload length detected")

            encrypted_payload = bytes(extracted[4 : 4 + payload_length])
            decrypted = decrypt_data(encrypted_payload, password)

            voice_ratio = len(voice_indices) / len(samples) if len(samples) else 0
            duration = len(samples) / params.framerate if params.framerate else 0

            self._store_report(
                {
                    'mode': 'extract',
                    'duration_seconds': round(duration, 2),
                    'total_samples': int(len(samples)),
                    'voiced_samples': int(len(voice_indices)),
                    'voice_ratio': round(voice_ratio, 3),
                    'recovered_bytes': int(len(decrypted)),
                    'technique': 'Voiced-frame LSB + AES encryption',
                }
            )

            return decrypted

        except Exception as exc:
            print(f"Voice extraction failed: {str(exc)}")
            return None



