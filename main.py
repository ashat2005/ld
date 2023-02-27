from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from pytube import YouTube
from dotenv import load_dotenv
from pytube.exceptions import RegexMatchError
import os
import logging

load_dotenv('.env')

buttons = [
    KeyboardButton('/start'),
    KeyboardButton('/help'),
    KeyboardButton('/video'),
    KeyboardButton('/audio')
]

button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*buttons)

bot = Bot(os.environ.get("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    await message.answer(f'Здраствуйте {message.from_user.full_name}', reply_markup=button)

class DownloadVideo(StatesGroup):
    download = State()
class DownloadAudio(StatesGroup):
    downl0ad = State()

@dp.message_handler(commands=['video'])
async def video(message:types.Message):
    await message.reply(f'Отправьте ссылку на видео и я вам скачаю его')
    await DownloadVideo.download.set()

@dp.message_handler(commands=['audio'])
async def audio(message:types.Message):
    await message.reply(f'Отправьте ссылку на аудио и я вам скачаю его')
    await DownloadAudio.downl0ad.set()

@dp.message_handler(state=DownloadAudio.downl0ad)
async def downaudio(msg:types.Message, state: FSMContext):
    await msg.answer("download audio")
    try:
        yt = YouTube(msg.text)
    except RegexMatchError:
        await msg.reply("Неверная ссылка на видео")
    await msg.reply(f'{yt.title}')
    audio = yt.streams.filter(only_audio=True).first().download('audio',f"{yt.title}.mp3")
    try:
        await msg.answer(f'отправляем аудио')
        with open(audio, 'rb') as da:
            await msg.answer_audio(da)
            os.remove(audio)
    except:
        await msg.answer('произошла ошибка при отправке аудио')
    await state.finish()

@dp.message_handler(state=DownloadVideo.download)
async def download_video(message:types.Message, state:FSMContext):
    await message.answer("Скачиваем видео")
    
    try:
        yt = YouTube(message.text)
    except RegexMatchError:
        await message.reply("Неверная ссылка на видео")
    await message.reply(f'{yt.title}')
    video =  yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download('video', f'{yt.title}.mp4')
    try:
        await message.answer(f"Отправляем видео")
        with open(video, 'rb') as down_video:
            await message.answer_video(down_video)
            os.remove(video)
    except:
        await message.answer("Произошла ошибка при отправке видео")
    await state.finish()

@dp.message_handler()
async def not_found(message:types.Message):
    await message.reply(f"Я вас не понял, введите /help")

executor.start_polling(dp)