from PIL import Image
import cv2
import argparse
import os
import time
import json
from pathlib import Path
import numpy as np



def process_images(directory, watermark_filename, dpi, quality):
    start_time = time.time()

    result_path = os.path.join(directory, 'С ЛОГО')
    try:
        os.mkdir(result_path)
    except OSError as error:
        print(error)

    onlyfiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    watermark = Image.open(watermark_filename)
    watermark.load()


    for filename in onlyfiles:
        file_path = Path(directory) / filename
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            with Image.open(file_path) as image:
                image.load()
                cv_image = cv2.imdecode(np.fromfile(str(file_path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                if (cv_image.shape[1], cv_image.shape[0]) != image.size:
                    image = image.transpose(Image.ROTATE_90)
                    fixed_width = int(image.width * 0.5)
                else:
                    fixed_width = int(image.width * 0.3)

                height_size = int(fixed_width / watermark.width * watermark.height)
                resized_watermark = watermark.resize((fixed_width, height_size))

                xpos = int(image.width - resized_watermark.width - 0.03 * image.width)
                ypos = int(image.height - resized_watermark.height - 0.03 * image.width)

                image.paste(resized_watermark, (xpos, ypos), resized_watermark)

                result_filename = os.path.join(result_path, filename)
                image.save(result_filename, dpi=(dpi, dpi), quality=quality)

    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Описание скрипта')

    parser.add_argument('-p', '--path', type=str, default=os.getcwd(),
                        help='Название папки (по умолчанию - текущая директория)')
    parser.add_argument('-w', '--watermark', type=str, default='nsh',
                        help='Сокращение для выбора водяного знака (nsh - nsh_mark.png, eco - eco_mark.png)')
    parser.add_argument('-q', '--quality', type=int, default=95,
                        help='Качество сохранения изображений (от 1 до 95 или 100)')
    parser.add_argument('-d', '--dpi', type=int, default=96,
                        help='DPI изображений (по умолчанию - 96)')

    args = parser.parse_args()

    directory = args.path

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'watermarks.json')) as file:
        watermarks = json.load(file)

    watermark_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), watermarks[args.watermark])

    process_images(directory, watermark_filename, args.dpi, args.quality)

    input('Press ENTER to exit')