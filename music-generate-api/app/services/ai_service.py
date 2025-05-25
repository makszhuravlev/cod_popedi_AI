from transformers import AutoProcessor, MusicgenForConditionalGeneration, PreTrainedTokenizerFast
from transformers.modeling_utils import SpecificPreTrainedModelType
import soundfile as sf

class AiService:
    __model_name: str
    __model_dir: str

    __processor: PreTrainedTokenizerFast | None = None
    __model: SpecificPreTrainedModelType | None = None

    is_busy: bool = False

    def __init__(self, model_name: str = "facebook/musicgen-stereo-small", model_dir: str = "/models/facebook/musicgen-stereo-small"):
        self.__model_name = model_name
        self.__model_dir = model_dir

    def setup(self):
        print(f"[AI] Use {self.__model_name} model")

        print("[AI] Loading AI Processor...")
        self.__processor = AutoProcessor.from_pretrained(self.__model_dir, local_files_only=True)

        print("[AI] Loading AI Model...")
        self.__model = MusicgenForConditionalGeneration.from_pretrained(self.__model_dir, local_files_only=True)

        print("[AI] Ready!")

    def generate(self, *prompt: str, context_size: int = 1024):
        self.is_busy = True

        print("[AI] Setup Generation...")
        inputs = self.__processor(
            text=list(prompt),
            padding=True,
            return_tensors="pt",
        )

        print("[AI] Generation...")
        audio_values = self.__model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=context_size)

        print("[AI] Saving...")
        sampling_rate = self.__model.config.audio_encoder.sampling_rate
        audio_values = audio_values.cpu().numpy()
        sf.write("/out/result.mp3", audio_values[0].T, sampling_rate)

        self.is_busy = False

