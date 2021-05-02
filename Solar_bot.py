from telegram.ext import Updater, CommandHandler
import telegram
import logging
import os

def start (update,context):
    logger.info(f"El usuario {update.effective_user['username']}, ha iniciado una conversación")
    name= update.effective_user['first_name']
    user_id=update.effective_user['id']
    context.bot.sendMessage(chat_id=user_id,parse_mode='HTML',text=f'Hola <b>{name}</b>, ¿en que pudo ayudarte?')

#Configurar logging
logging.basicConfig(level= logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s,")

logger = logging.getLogger()

TOKEN = os.getenv('TOKEN')

if __name__=='__main__':
    my_bot = telegram.Bot(token=TOKEN)

updater= Updater(my_bot.token, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler('start',start))
updater.start_polling()
updater.idle()