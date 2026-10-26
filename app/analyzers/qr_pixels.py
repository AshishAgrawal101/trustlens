"""QR-only white-background normalization; frozen model decoding stays unchanged."""
from contextlib import closing
import io

from PIL import Image, ImageOps
from app.analyzers.image import decode_image, InvalidImage


def decode_qr_image(content):
    validated = decode_image(content)
    try:
        with closing(Image.open(io.BytesIO(content))) as header:
            transparent = 'A' in header.getbands() or 'transparency' in header.info
        if not transparent:
            return validated
        # Release the first full RGB before the bounded second decode for alpha.
        validated.close()
        with closing(Image.open(io.BytesIO(content))) as source:
            with closing(ImageOps.exif_transpose(source)) as oriented:
                with closing(oriented.convert('RGBA')) as rgba:
                    with closing(rgba.getchannel('A')) as mask:
                        canvas = Image.new('RGB', rgba.size, 'white')
                        try:
                            canvas.paste(rgba, mask=mask)
                            return canvas
                        except BaseException:
                            canvas.close()
                            raise
    except (OSError, ValueError) as exc:
        validated.close()
        raise InvalidImage('This file could not be read as an image.') from exc
    except BaseException:
        validated.close()
        raise
