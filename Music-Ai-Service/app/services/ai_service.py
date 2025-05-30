from transformers import AutoProcessor, MusicgenForConditionalGeneration, PreTrainedTokenizerFast
from transformers.modeling_utils import SpecificPreTrainedModelType
import soundfile as sf

class AiService:
    __model_name: str
    __model_dir: str

    __processor  = None
    __model = None

    is_busy: bool = False

    def __init__(self, model_name: str = "facebook/musicgen-stereo-small", models_dir: str = "/models/"):
        self.__model_name = model_name
        self.__model_dir = models_dir+model_name

    def setup(self):
        print(f"[AI] Use \"{self.__model_name}\" model")
        print(f"[AI] Path \"{self.__model_dir}\"")

        print("[AI] Loading AI Processor...")
        self.__processor = AutoProcessor.from_pretrained(self.__model_dir, local_files_only=True)

        print("[AI] Loading AI Model...")
        self.__model = MusicgenForConditionalGeneration.from_pretrained(self.__model_dir, local_files_only=True)

        print("[AI] Ready!")

    def generate(self, prompt: str, output_path: str="out/result.mp3", context_size: int = 1024):
        self.is_busy = True

        print("[AI] Setup Generation...")
        inputs = self.__processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        )

        print("[AI] Generation...")
        audio_values = self.__model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=context_size)

        print("[AI] Saving...")
        sampling_rate = self.__model.config.audio_encoder.sampling_rate
        audio_values = audio_values.cpu().numpy()
        sf.write(output_path, audio_values[0].T, sampling_rate)

        self.is_busy = False
