import os
import pydub
import uuid
import logging
import subprocess


from settings import BASE_DIR

AUDIOS_DIR = os.path.join(BASE_DIR, 'telegram_ai', 'temp', 'voice')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_dir_if_not_exists(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def generate_unique_name():
    uuid_value = uuid.uuid4()
    return f"{str(uuid_value)}"


def download_voice_as_ogg(downloaded_file):
    create_dir_if_not_exists(AUDIOS_DIR)
    ogg_filepath = os.path.join(AUDIOS_DIR, f"{generate_unique_name()}.ogg")
    with open(ogg_filepath, 'wb') as new_file:
        new_file.write(downloaded_file)

    return ogg_filepath


def convert_ogg_to_mp3(file_path):
    mp3_path = os.path.splitext(file_path)[0] + ".mp3"
    subprocess.run(["ffmpeg", "-i", file_path, mp3_path])
    if os.path.exists(mp3_path):
        os.remove(file_path)
        logger.info('audiofile converted to mp3')
        return mp3_path
    else:
        logger.error(f"Conversion of {file_path} to mp3 failed.")
        return None


def convert_to_min_bitrate(file_path):
    new_file_path = "./temp/voice/new_min_file.mp3"
    #mono_file = "./temp/voice/new_mono_file.mp3"
    try:
        """stereo_audio = pydub.AudioSegment.from_file(file_path, format='mp3')
        logging.info('50%')
        mono_audios = stereo_audio.split_to_mono()
        logging.info('60%')
        mono = mono_audios[0].export(mono_file, format='mp3')
        logging.info('70%')"""
        audio = pydub.AudioSegment.from_file(file_path, format="mp3")
        logging.info('80%')
        audio.export(new_file_path, format="mp3", bitrate="24k")
        logger.info("100% \nStereo->Mono Done!")
        os.remove(file_path)
        #os.remove(mono_file)
        return new_file_path
    except Exception as e:
        logger.info(f"Comfert to min bitrate Error: {e}")