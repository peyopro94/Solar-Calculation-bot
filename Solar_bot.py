from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import telegram
import logging
import os
import math
#Importar ficheros locales
from Calculo_Solar import NASA, pot_sistema, vol_sis, perdidas, n_panles

logger = logging.getLogger()

TOKEN = os.getenv('TOKEN')

SLOC, LAT, HP_MIN, FIN, ALOC, PSIS, HSIS, PPAN, SCALC = range(9)

ubicacion=[] #LON,LAT
data=[]

#Configurar logging
logging.basicConfig(level= logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s,")

def start (update,context):
    logger.info(f"El usuario {update.effective_user['username']}, ha iniciado una conversación")
    name= update.effective_user['first_name']
    user_id=update.effective_user['id']
    reply_keyboard=[['Manual','Ubicación Actual']]
    
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        f'Hola <b>{name}</b>.\n'
        'Soy un BOT que se dedica a realizar Dimensionamiento Solar.\n'
        'Uso la data de POWER NASA para extraer la información necesaria según la ubicación.\n'
    )
    
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        '<u>Comandos</u>\n\n'
        '/empezar Empezar con el aplicativo\n'
        '/help Ayuda sobre la aplicación\n'
        '/autor Información Sobre el autor\n'
    )


def solar (update,context):
    reply_keyboard=[['Manual','Ubicación Actual']]
    
    update.message.reply_text(
        '¿Como desea ingresar la ubicación del proyecto?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True)
    )
    return SLOC

def loc_state(update,context):    
    i=str(update.message.text)
    if i=='Manual':
        update.message.reply_text(
        'Ingresa la Longitud de la Ubicación:',
        reply_markup=ReplyKeyboardRemove())
        return LAT
    elif i=='Ubicación Actual':
        location_keyboard= KeyboardButton(text='Enviar Ubicación',request_location=True)
        location_solicitud=[[location_keyboard]]
        update.message.reply_text(
        'Se va a pedir permiso para obtener su ubicación',
        reply_markup=ReplyKeyboardMarkup(location_solicitud,one_time_keyboard=True)
        )
        return ALOC
    else:
        update.message.reply_text(
        'Opción Invalida, presione /star para reinicia',
        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
def input_lat(update,context):
    ubicacion.append(update.message.text)
    update.message.reply_text(
        'Ingresa la Latitud de la Ubicación:'
    )
    return HP_MIN

def HP_min(update,context):
    ubicacion.append(update.message.text)
    update.message.reply_text(
        'Buscando data de su ubicación en POWER NASA, espere... '
    )

    HP_min=NASA(ubicacion[0],ubicacion[1])
    if HP_min=='Error':
        update.message.reply_text(
            'ERROR, la ubicación enviada es incorrecta'
            'Presione /start para empezar',    
        reply_markup=ReplyKeyboardRemove())
        ubicacion.clear()
        return ConversationHandler.END 
    else:    
        update.message.reply_text(
            'La Hora Pico Minima de la Zona es:\n' 
            f'{HP_min} [kW-hr/m^2/dia]',
        reply_markup=ReplyKeyboardRemove()
        )
        data.append(HP_min)
        ubicacion.clear()
        update.message.reply_text(
            'Ingrese la potencia alimentar el sistema (W):'
        )
        return PSIS

def HP_min_aut(update,context):
    ubicacion.append(update.message.location.latitude)
    ubicacion.append(update.message.location.longitude)
    
    update.message.reply_text(
        'Buscando data de su ubicación en POWER NASA, espere... '
    )
    
    HP_min=NASA(ubicacion[0],ubicacion[1])
    
    if HP_min=='Error':
        update.message.reply_text(
            'ERROR, no hemos podido conectar a POWER NASA'
            'Para intentar de nuevo, presione /start',
        reply_markup=ReplyKeyboardRemove()    
        )
        ubicacion.clear()
        return ConversationHandler.END  
    else:    
        update.message.reply_text(
            'La Hora Pico Minima de la Zona es:\n' 
            f'{HP_min} [kW-hr/m^2/dia]',
        reply_markup=ReplyKeyboardRemove()
        )
        update.message.reply_text(
            'Ingrese la potencia alimentar el sistema (W):'
        )
        data.append(HP_min)
        ubicacion.clear()
        return PSIS

def pot_sis(update,context):
    pot=update.message.text
    data.append(float(pot))
    user_id=update.effective_user['id']
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        f'La potencia ingresada es <b>{float(pot)/1000} kW </b>'
    )
    update.message.reply_text(
        'Ingrese horas de funcionamiento del sistema:'
    )
    return HSIS

def hour_sis(update,context):
    hour=update.message.text
    data.append(float(hour))
    user_id=update.effective_user['id']
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        f'El sistema estara funcionando <b>{hour} horas</b>'
    )
    update.message.reply_text(
        'Las perdidas que se tomarán son las siguientes:\n'
        'n_r=0.95       Eficiencia del regulador\n'
        'n_inv=0.90     Eficiencia del inversor\n'
        'n_x= 0.97      Eficiencia por otras pérdidas\n'
        'f_c=0.05       Factor de contingencia'
    )
    update.message.reply_text(
        'Ingrese la potencia de los paneles a usar (Wp):'
    )
    return PPAN

def pot_paneles(update,context):
    panel_pot=update.message.text
    data.append(float(panel_pot))
    user_id=update.effective_user['id']
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        f'La potencia pico de los paneles a instalar es de <b>{panel_pot} Wp\n</b>'
    )
    update.message.reply_text(
        'Por ultimo, ingresar el Power Factor (PF) del sistema (recomendable: 0.85) :'
    )
    return SCALC

def solar_calculos(update,context):
    PF=update.message.text
    data.append(float(PF))
    Egen=pot_sistema(data[1],data[2])
    vol_sistema= vol_sis(Egen)
    n_t= perdidas(0.95,0.90,0.97)
    n_paneles=n_panles(data[3],data[0],Egen,n_t)
    P_sim=data[1]*1.2
    S_inv=P_sim/float(PF)
    
    user_id=update.effective_user['id']
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        '<u>Dimesionamiento del sistema\n</u>'
        f'Energia diaria del sistema: <b>{Egen/1000} kWh/dia</b>\n'
        f'Voltaje del Sistema : <b>{vol_sistema} V</b>\n'
        f'Perdidas del sistema: <b>{round(n_t*100,2)}%</b>\n'
        f'Numero de paneles necesarios a instalar: <b>{math.ceil(n_paneles)} Ud.</b>\n'
        f'Tamaño del inversor: <b>{math.ceil(S_inv/1000)} kVA</b> '
    )
    return FIN

def end(update,context):    
    update.message.reply_text(
        'Espero haberte ayudado! Si quieres comenzar nuevamente, envia /start'
    )
    return ConversationHandler.END

def cancel(update,context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Espero hablemos pronto', 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def help(update,context):
    user_id=update.effective_user['id']
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        '<u>Ayuda</u>\n'
        '<b>Potencia:</b> Carga promedio/maximo que tiene instalado en el lugar (W)\n'
        '<b>Horas de funcionamiento:</b> Poner las horas promedio/maximo durante radiacion solar que se usan esas cargas\n'
        '<b>Potencia Paneles:</b> Ver fabricante, se ingresa la potencia de 1 panel.Cada uno va desde 350 a 600 Wp'
    )
    update.message.reply_text(
        'Pulse /start para empezar de nuevo'
    )   
    return ConversationHandler.END

def autor(update,context):
    user_id=update.effective_user['id']
    context.bot.sendMessage(
        chat_id=user_id,parse_mode='HTML',text=
        '<u>Sobre el autor</u>\n'
        '<b>Nombre:</b> Alfredo Pró (aka peyopro94)\n'
        '<b>Profesión:</b> Ingeniero de Energía\n'
        '<b>App version:</b> 1.0 alpha'
    )
    update.message.reply_text(
        'Pulse /start para empezar de nuevo'
    )
    return ConversationHandler.END

def main():
    #Iniciar bot
    my_bot = telegram.Bot(token=TOKEN)
    updater= Updater(my_bot.token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler('autor',autor))
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('empezar',solar)
        ],

        states={
            SLOC:[MessageHandler(Filters.text, loc_state)],
            ALOC:[MessageHandler(Filters.location, HP_min_aut)],
            LAT:[MessageHandler(Filters.text, input_lat)],
            HP_MIN:[MessageHandler(Filters.text, HP_min)],
            PSIS:[MessageHandler(Filters.text, pot_sis)],
            HSIS:[MessageHandler(Filters.text, hour_sis)],
            PPAN:[MessageHandler(Filters.text, pot_paneles)], 
            SCALC:[MessageHandler(Filters.text, solar_calculos)],
            FIN:[MessageHandler(Filters.text, end)]
        },

        fallbacks=[MessageHandler(Filters.command, cancel)],
    ))
    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()