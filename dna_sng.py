import os
import multiprocessing as mp
import re

from telegram.ext import CommandHandler, Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.update import Update
from telegram import ReplyKeyboardRemove

from generator import generator

# Must keep it safe!
API_KEY = 'Place your API key here'

RNA_DNA_SELECT = 1
GENERATOR_NUM_SEQ = 2
GENERATOR_SEQ_LENGTH = 3
GENERATOR_GC_CONTENT = 4
GENERATOR_DI_CONTENT = 5

def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    reply_kb = ReplyKeyboardMarkup([['DNA', 'RNA']], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='*Send a generator type*',
        reply_markup=reply_kb,
        parse_mode='Markdown'
    )
    context.user_data['user_id'] = update.effective_user.id
    return RNA_DNA_SELECT

def rna_dna_select(update: Update, context: CallbackContext):
    generator_type = update.message.text
    context.user_data['generator_type'] = generator_type
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode='Markdown',
        text=f'*{generator_type}* generator was chosen. Starting the process',
        reply_markup=ReplyKeyboardRemove(),
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Enter the number of sequences to generate:',
    )
    return GENERATOR_NUM_SEQ

# Number of sequences
def num_seqs(update: Update, context: CallbackContext):
    num_seqs = update.message.text
    context.user_data['num_seqs'] = int(num_seqs)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Enter the sequence length:',
    )
    return GENERATOR_SEQ_LENGTH

# Sequence length
def seq_length(update: Update, context: CallbackContext):
    seq_len = update.message.text
    context.user_data['seq_length'] = int(seq_len)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Specify the GC content in %. Use the following format: *<min>-<max>*',
        parse_mode='Markdown',
    )
    return GENERATOR_GC_CONTENT

# GC content, %
def gc_content(update: Update, context: CallbackContext):
    gc = update.message.text.split('-')
    context.user_data['gc_min'] = float(gc[0])
    context.user_data['gc_max'] = float(gc[1])
    if context.user_data.get('gc_max', 0) <= context.user_data.get('gc_min', 0):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'*ERROR: Specified GC content is not valid.* In order to start again send \`/start\` command.',
            parse_mode='Markdown',
        )
        context.user_data.clear()
        return ConversationHandler.END
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Specify the dinucleotides content in %. Use the following format: *<min>-<max>*. If dinucleotides are not mandatory send *0-0*.',
        parse_mode='Markdown',
    )
    return GENERATOR_DI_CONTENT

# Dinucleotides content
def di_content(update: Update, context: CallbackContext):
    di = update.message.text.split('-')
    context.user_data['di_min'] = float(di[0])
    context.user_data['di_max'] = float(di[1])
    if (context.user_data.get('di_max', 0) != 0 and context.user_data.get('di_min', 0) != 0) \
    and (context.user_data.get('di_max', 0) <= context.user_data.get('di_min', 0)):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'*ERROR: Specified dinucleotide content is not valid.* In order to start again send \`/start\` command.',
            parse_mode='Markdown',
        )
        context.user_data.clear()
        return ConversationHandler.END

    process = mp.Process(target=generator, args=(context.user_data, ))
    process.start()
    context.bot_data['schedule'].update(
        {
            update.effective_chat.id: {
                'output_file': f'{context.user_data["user_id"]}_output.csv',
                'job_process': process,
            }
        }
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Your job is queued. Please, wait for the result.',
    )

    context.user_data.clear()
    return ConversationHandler.END

def gen_error(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'*ERROR:* {context.user_data.get("gen_error", "Undefined")} In order to start again send \`/start\` command.',
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END

def reset(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='*Reseting the state*',
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='*Done.* In order to start again send \`/start\` command.',
        parse_mode='Markdown',
    )

def cancel(update: Update, context: CallbackContext):
    context.user_data.clear()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='*ERROR: Specified parameters are not valid.* In order to start again send \`/start\` command.',
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

def cite(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='''*Authors:*
*Kiryanova O. Yu.* (Ufa Federal Research Center of Russian Academy of Sciences, Institute of Biochemistry and Genetics)
*Kiryanov I. I.* (Corning, Inc.)
*Chemeris A. V.* (Ufa Federal Research Center of Russian Academy of Sciences, Institute of Biochemistry and Genetics)
*Garafutdinov R. R.* (Ufa Federal Research Center of Russian Academy of Sciences, Institute of Biochemistry and Genetics)''',
        parse_mode='Markdown',
    )

def job_schedule_init(context: CallbackContext):
    context.bot_data['schedule'] = dict()

def job_schedule(context: CallbackContext):
    for chat_id in list(context.bot_data['schedule'].keys()):
        process: mp.Process = context.bot_data['schedule'][chat_id]['job_process']
        if not process.is_alive():
            file_path = context.bot_data['schedule'][chat_id]['output_file']
            with open(file_path, 'rb') as f:
                context.bot.send_document(
                    chat_id=chat_id,
                    filename=file_path,
                    document=f,
                )
            os.remove(file_path)
            context.bot_data['schedule'].pop(chat_id)

if __name__ == '__main__':

    # Main config
    updater = Updater(token=API_KEY, use_context=True)
    dispatcher = updater.dispatcher

    # Job queue
    jq = updater.job_queue
    jq.run_once(job_schedule_init, when=0)
    jq.run_repeating(job_schedule, interval=10)

    # Command handlers
    start_handler = CommandHandler('start', start)
    reset_handler = CommandHandler('reset', reset)
    cite_handler = CommandHandler('cite', cite)
    conv_handler = ConversationHandler(
        entry_points=[start_handler, ],
        states={
            RNA_DNA_SELECT: [MessageHandler(Filters.regex(re.compile(r'^(DNA|RNA)$', re.I)), rna_dna_select)],
            GENERATOR_NUM_SEQ: [
                MessageHandler(Filters.regex(re.compile(r'^\d+$', re.I)), num_seqs),
                MessageHandler(~Filters.regex(re.compile(r'^\d+$', re.I)), cancel),
            ],
            GENERATOR_SEQ_LENGTH: [
                MessageHandler(Filters.regex(re.compile(r'^\d+$', re.I)), seq_length),
                MessageHandler(~Filters.regex(re.compile(r'^\d+$', re.I)), cancel),
            ],
            GENERATOR_GC_CONTENT: [
                MessageHandler(Filters.regex(re.compile(r'^\d+\.{0,}\d{0,}-\d+\.{0,}\d{0,}$', re.I)), gc_content),
                MessageHandler(~Filters.regex(re.compile(r'^\d+\.{0,}\d{0,}-\d+\.{0,}\d{0,}$', re.I)), cancel),
            ],
            GENERATOR_DI_CONTENT: [
                MessageHandler(Filters.regex(re.compile(r'^\d+\.{0,}\d{0,}-\d+\.{0,}\d{0,}$', re.I)), di_content),
                MessageHandler(~Filters.regex(re.compile(r'^\d+\.{0,}\d{0,}-\d+\.{0,}\d{0,}$', re.I)), cancel),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(reset_handler)
    dispatcher.add_handler(cite_handler)

    updater.start_polling()
    updater.idle()
