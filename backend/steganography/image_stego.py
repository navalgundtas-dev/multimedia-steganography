from PIL import Image

class ImageSteganography:

    def validate_image(self, image_path):
        try:
            img = Image.open(image_path)
            img.verify()
            return True, ""
        except Exception as e:
            return False, str(e)

    def embed_data(self, cover_path, secret_data: bytes, password: str, output_path):
        """
        Embed secret_data into the cover image using 2 LSB per channel.
        """
        img = Image.open(cover_path)
        img = img.convert('RGB')
        width, height = img.size

        # Max bytes using 2 LSB per channel
        max_bytes = (width * height * 3 * 2) // 8
        if len(secret_data) > max_bytes:
            raise ValueError(f"Secret data too large: {len(secret_data)} bytes. Max allowed: {max_bytes} bytes")

        # Convert secret data to bit string
        secret_bits = ''.join(f'{byte:08b}' for byte in secret_data)
        secret_bits += '00000000'  # EOF marker byte

        pixels = list(img.getdata())
        new_pixels = []
        bit_idx = 0

        for pixel in pixels:
            r, g, b = pixel
            new_pixel = []

            for color in (r, g, b):
                if bit_idx < len(secret_bits):
                    # Take next 2 bits from secret
                    bits_to_embed = secret_bits[bit_idx:bit_idx+2].ljust(2, '0')
                    color = (color & 0b11111100) | int(bits_to_embed, 2)
                    bit_idx += 2
                new_pixel.append(color)
            new_pixels.append(tuple(new_pixel))

        img.putdata(new_pixels)
        img.save(output_path)
        return True

    def extract_data(self, stego_path, password: str):
        """
        Extract secret data from stego image using 2 LSB per channel.
        """
        img = Image.open(stego_path)
        img = img.convert('RGB')
        pixels = list(img.getdata())

        bits = ''
        for pixel in pixels:
            for color in pixel:
                bits += f'{color & 0b00000011:02b}'

        # Convert bits to bytes
        secret_bytes = bytearray()
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8:
                break
            b = int(byte, 2)
            if b == 0:  # EOF marker
                break
            secret_bytes.append(b)

        return bytes(secret_bytes)
