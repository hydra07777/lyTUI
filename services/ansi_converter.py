from PIL import Image
import io

UNICODE_GRADIENT = (
    " .`^\",:;Il!i~+_-?][}{1)(|\\/*tfjrxnuvczXYUJCLQ0OZ"
    "mwqpdbkhao*#MW&8%B@$"
)

def resize_image(image, width):
    ratio = image.height / image.width
    height = int(width * ratio * 0.5)
    return image.resize((width, height), Image.Resampling.LANCZOS)

def convert_cover_ansi(cover_byte):
    if not cover_byte:
        return "Pas de cover"

    try:
        image = Image.open(io.BytesIO(cover_byte)).convert("RGB")
        image = resize_image(image, 70)

        pixels = image.load()
        lines = []

        for y in range(image.height):
            line = ""
            for x in range(image.width):
                r, g, b = pixels[x, y]
                luminance = int(0.2126*r + 0.7152*g + 0.0722*b)
                char = UNICODE_GRADIENT[
                    luminance * (len(UNICODE_GRADIENT) - 1) // 255
                ]
                line += f"\x1b[38;2;{r};{g};{b}m{char}\x1b[0m"
            lines.append(line)

        return "\n".join(lines)

    except Exception as e:
        return f"Error generating ASCII art: {e}"
