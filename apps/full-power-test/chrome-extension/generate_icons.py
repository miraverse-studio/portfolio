"""
Mira Corp. Hub — Chrome Extension Icon Generator
Run this script to create icon PNG files in the icons/ folder.
Requires only Python stdlib (no pip needed).
"""
import struct, zlib, os

def png_from_rgba(width, height, rgba_pixels):
    """Build a valid PNG from raw RGBA bytes."""
    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        return c + struct.pack('>I', zlib.crc32(name + data) & 0xffffffff)

    raw = b''
    for row in range(height):
        raw += b'\x00'  # filter type None
        for col in range(width):
            raw += bytes(rgba_pixels[row][col])

    compressed = zlib.compress(raw, 9)
    return (
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) +
        chunk(b'IDAT', compressed) +
        chunk(b'IEND', b'')
    )

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(4))

def make_mira_icon(size):
    """Draw a gradient circle with 'A' letter."""
    COLOR_A = (124, 58, 237, 255)   # violet
    COLOR_B = (245, 158, 11, 255)   # gold

    pixels = []
    cx, cy = size / 2, size / 2
    radius = size * 0.45

    for row in range(size):
        row_pixels = []
        for col in range(size):
            dx, dy = col - cx, row - cy
            dist = (dx*dx + dy*dy) ** 0.5

            if dist <= radius:
                t = (col / size + row / size) / 2
                bg = lerp_color(COLOR_A, COLOR_B, t)

                # Draw letter "A" in white
                nx, ny = (col - cx) / radius, (row - cy) / radius

                # Simple "A" raster approximation
                in_letter = False

                # Normalize to 0..1 letter box
                lx = (col - cx/2) / size
                ly = (row - cy/2) / size
                # Letter A box: center 0.5, height 0.6, width 0.35
                lx2 = (col - cx + size*0.18) / (size * 0.36)  # 0..1 within letter
                ly2 = (row - cy + size*0.28) / (size * 0.56)  # 0..1 within letter

                if 0.04 <= lx2 <= 0.96 and 0.02 <= ly2 <= 0.98:
                    thick = max(1, int(size * 0.07))
                    # Left stroke
                    left_x = lx2 * (size*0.36)
                    left_expected = ly2 * (size*0.36) * 0.6
                    # Right stroke
                    right_expected = (size*0.36) - left_expected

                    lx_px = col - (cx - size*0.18)
                    ly_px = row - (cy - size*0.28)
                    width_px = size * 0.36
                    height_px = size * 0.56

                    # Left diagonal
                    left_x_at_y = (ly_px / height_px) * (width_px * 0.5)
                    if abs(lx_px - left_x_at_y) < thick:
                        in_letter = True

                    # Right diagonal
                    right_x_at_y = width_px - left_x_at_y
                    if abs(lx_px - right_x_at_y) < thick:
                        in_letter = True

                    # Crossbar
                    if 0.4 < ly_px/height_px < 0.55 and (left_x_at_y) < lx_px < right_x_at_y:
                        in_letter = True

                if in_letter:
                    color = (255, 255, 255, 230)
                else:
                    # Slight inner glow near edge
                    edge_t = max(0, 1 - (radius - dist) / (radius * 0.15))
                    color = lerp_color(bg, (0,0,0,0), edge_t * 0.3)
                    color = list(color); color[3] = 255; color = tuple(color)

                row_pixels.append(color)
            else:
                row_pixels.append((0, 0, 0, 0))  # transparent

        pixels.append(row_pixels)

    return pixels

def main():
    os.makedirs('icons', exist_ok=True)
    for size in (16, 48, 128):
        pixels = make_mira_icon(size)
        data   = png_from_rgba(size, size, pixels)
        path   = f'icons/icon{size}.png'
        with open(path, 'wb') as f:
            f.write(data)
        print(f'  ✓ {path} ({size}x{size})')
    print()
    print('アイコン生成完了！Chromeの拡張機能ページで読み込んでください。')
    print('chrome://extensions/ → デベロッパーモード ON → パッケージ化されていない拡張機能を読み込む')

if __name__ == '__main__':
    print()
    print('Mira Corp. Hub — アイコン生成中...')
    main()
