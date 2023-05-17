from PIL import Image, ExifTags
import argparse
import os
import time
import json
from pathlib import Path
from tqdm import tqdm


def get_image_orientation_tag(image):
    try:
        exif_data = image.getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == 'Orientation':
                    return value
    except AttributeError:
        pass
    return 1


def process_images(directory, watermark_filename, dpi, quality):
    start_time = time.time()

    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    path = Path(directory)
    onlyfiles = [file.name for file in path.iterdir() if file.is_file() and file.suffix.lower() in image_extensions]

    if len(onlyfiles) == 0:
        print("--- Folder is empty ---")
        return

    print("Count files: %s" % len(onlyfiles))

    progress_bar = tqdm(total=len(onlyfiles))

    result_path = os.path.join(directory, 'С ЛОГОТИПОМ')
    try:
        os.mkdir(result_path)
    except OSError as error:
        print(error)

    watermark = Image.open(watermark_filename)
    watermark.load()

    for filename in onlyfiles:
        file_path = Path(directory) / filename
        with Image.open(file_path) as image:
            image.load()
            # Get image orientation
            orientation_tag = get_image_orientation_tag(image)
            if orientation_tag == 8:
                image = image.transpose(Image.ROTATE_90)
            fixed_width = int(image.width * 0.3)
            height_size = int(fixed_width / watermark.width * watermark.height)
            resized_watermark = watermark.resize((fixed_width, height_size))
            xpos = int(image.width - resized_watermark.width - 0.02 * image.width)
            ypos = int(image.height - resized_watermark.height - 0.02 * image.width)
            image.paste(resized_watermark, (xpos, ypos), resized_watermark)
            image.save(os.path.join(result_path, filename), dpi=(dpi, dpi), quality=quality)
            progress_bar.update(1)
    progress_bar.close()
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Этот скрипт выполняет обработку изображений'
                                     'с применением водяных знаков.')

    parser.add_argument('-p', '--path', type=str, default=os.getcwd(),
                        help='Название папки (по умолчанию - текущая директория)')
    parser.add_argument('-w', '--watermark', type=str, default='default',
                        help='Сокращение для выбора водяного знака (nsh - nsh_mark.png, eco - eco_mark.png)')
    parser.add_argument('-q', '--quality', type=int, default=95,
                        help='Качество сохранения изображений (от 1 до 95 или 100)')
    parser.add_argument('-d', '--dpi', type=int, default=96,
                        help='DPI изображений (по умолчанию - 96)')

    args = parser.parse_args()

    directory = args.path

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/watermarks.json')) as file:
        watermarks = json.load(file)

    watermark_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), watermarks[args.watermark])

    process_images(directory, watermark_filename, args.dpi, args.quality)

    input('Press ENTER to exit')
