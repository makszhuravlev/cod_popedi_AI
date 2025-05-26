import argparse

from transformers import AutoProcessor, MusicgenForConditionalGeneration
import soundfile as sf

import torch

parser = argparse.ArgumentParser(description='Adeptus Altusches AI Loader')
parser.add_argument('--model', action="store", dest='model_name', default="facebook/musicgen-stereo-small")
parser.add_argument('--dir', action="store", dest='model_directory', default="./models/facebook/musicgen-stereo-small")
parser.add_argument('--enable-download', action="store", dest='enable_download', default=True)
parser.add_argument('--enable-testing', action="store", dest='enable_testing', default=True)
args = parser.parse_args()

MODEL_NAME = args.model_name
MODEL_DIR = args.model_directory

if args.enable_download:
    print("=== DOWNLOAD ===")

    print("LOAD PROCESSOR")
    processor = AutoProcessor.from_pretrained(MODEL_NAME, local_files_only=False)
    print("LOAD MODEL")
    model = MusicgenForConditionalGeneration.from_pretrained(MODEL_NAME, local_files_only=False)

    print("SAVE")
    model.save_pretrained(MODEL_DIR)
    processor.save_pretrained(MODEL_DIR)


if args.enable_download:
    print("=== TESTING ===")

    print("LOAD PROCESSOR")
    processor = AutoProcessor.from_pretrained(MODEL_DIR, local_files_only=True)
    print("LOAD MODEL")
    model = MusicgenForConditionalGeneration.from_pretrained(MODEL_DIR, local_files_only=True)

    print("SETUP GENERATION")
    inputs = processor(
        text=["Soviet march, military march, brass, heavy percussion, triumphant melody, Soviet anthem style, patriotic, 120 BPM, trumpets, trombones, accordion, bass drum, snare rolls, heroic atmosphere, ceremonial music"],
        padding=True,
        return_tensors="pt",
    )

    print("GENERATION")
    audio_values = model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=1024)

    print("SAVE")
    sampling_rate = model.config.audio_encoder.sampling_rate
    audio_values = audio_values.cpu().numpy()
    sf.write("../out/TEST_musicgen_out.mp3", audio_values[0].T, sampling_rate)
