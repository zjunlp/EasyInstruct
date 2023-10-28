from .base_prompt import BasePrompt
import base64
import requests
import numpy as np
from PIL import Image
from torchvision.transforms import transforms

CAPTION_URL = "https://nielsr-comparing-captioning-models.hf.space/run/predict"
CAPTION_INSTRUCTION = "You are a highly intelligent and accurate Image-Text Question Answering system. You take the textual captions of the image as input and your task is to answer questions about the image.\nThis is the textual captions: {}.\n"
ASCII_INSTRUCTION = "You are a highly intelligent and accurate Image-Text Question Answering system. You take ASCII images (converted from images) as input and your task is to answer questions about the ASCII images.\nThis is an ASCII image: {}.\n"


class MMPrompt(BasePrompt):
    """Class for multimodal prompt"""

    def __init__(self, resize=224):
        super().__init__()
        self.resize = resize
        self.transform = transforms.Compose(
            [
                lambda x: Image.open(x).convert("RGB"),
                transforms.Resize((self.resize, self.resize)),
                transforms.ToTensor(),
            ]
        )

    def build_prompt(
        self,
        prompt: str,
        img_path: str,
        encode_format: str = "ASCII",
        scale: float = 10,
    ):
        """
        Args:
            prompt (str): textual question about the image
            img_path (str): the path of the image
            encode_format (str): caption or ASCII

        Returns:
            None
        """
        image = self.transform(img_path)
        if encode_format == "caption":
            img_prompt = self._image_to_caption(img_path)
            img_prompt = ". ".join(img_prompt)
            instruction = CAPTION_INSTRUCTION.format(img_prompt)
        elif encode_format == "ASCII":
            img_prompt = self._image_to_ASCII(image, scale, numerical=False)
            instruction = ASCII_INSTRUCTION.format(img_prompt)
        else:
            raise ValueError(
                'Invalid encode_format! encode_format must in ("caption", "ASCII")'
            )

        self.prompt = instruction + prompt
        print(self.prompt)
        return self.prompt

    def _image_to_caption(self, img_path):
        """Generate captions of the image

        Args:
            img_path (_type_): the path of the image
        Returns:
            captions (List): list of captions, each caption is a string
        """
        img_base64 = base64.b64encode(open(img_path, "rb").read())
        response = requests.post(
            CAPTION_URL,
            json={
                "data": [
                    "data:image/png;base64," + img_base64.decode("utf-8"),
                ]
            },
        ).json()
        if "data" not in response:
            raise ValueError("Return null caption!")
        captions = [caption.strip() for caption in response["data"]]
        return captions

    def _image_to_ASCII(self, image, scale=10, numerical=False):
        """Convert RGB image to ASCII image

        Args:
            image (torch.Tensor): transformed RGB image
            scale (int): 3 options to pick from:
                            ASCII_68: 68 levels of brightness
                            ASCII_10: 10 levels of brightness
                            ASCII_10n: 10 levels of brightness using integers to denote level
            numerical (bool): ASCII_10 or ASCII_10n
        """

        def image_float2int(image):
            return np.clip(image * 255.0, 0.0, 255.0).astype(np.uint8)

        def rgb_to_grayscale(rgb):
            return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

        # No periods or spaces bc I thought that might interfere with LLM
        ASCII_68 = (
            "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'"
        )
        ASCII_10 = "@%#*+=-:`'"
        ASCII_10n = "".join([str(i) for i in range(len(ASCII_10))[::-1]])

        image = np.transpose(image.numpy(), (1, 2, 0))
        image = rgb_to_grayscale(image_float2int(image))

        if scale > 10:
            ascii_scale = ASCII_68
        elif numerical:
            ascii_scale = ASCII_10n
        else:
            ascii_scale = ASCII_10
        ascii_img = "".join(
            [ascii_scale[int(p * (scale - 1) / 255)] for p in np.array(image).flatten()]
        )

        self._pretty_print_ascii(ascii_img, self.resize, self.resize)
        return ascii_img

    def _pretty_print_ascii(self, text, width, height):
        num_lines = int(len(text) / width)
        assert num_lines == height
        print_str = []
        for i in range(num_lines - 1):
            print_str.append(f"{text[i * width: (i + 1) * width]}\n")
        i += 1
        print_str.append(f"{text[i * width: (i + 1) * width]}")
        print("".join(print_str))
