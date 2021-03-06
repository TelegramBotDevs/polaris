import logging
from collections import OrderedDict
from threading import Thread
from time import sleep, time

from DictObject import DictObject
from firebase_admin import db

from polaris.types import AutosaveDict, Conversation, Message
from polaris.utils import (all_but_first_word, catch_exception, first_word,
                           generate_command_help, get_input, init_if_empty,
                           is_int, set_data, wait_until_received)


class plugin(object):
    # Loads the text strings from the bots language #

    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.reminders.commands
        self.description = self.bot.trans.plugins.reminders.description

    # Plugin action #

    def run(self, m):
        input = get_input(m, ignore_reply=False)
        if not input:
            return self.bot.send_message(m, generate_command_help(self, m.content), extra={'format': 'HTML'})
            # return self.bot.send_message(m, self.bot.trans.errors.missing_parameter, extra={'format': 'HTML'})

        delay = first_word(input)
        if delay:
            delaytime = delay[:-1]
            unit = delay[-1:]
            if not is_int(delaytime) or is_int(unit) or not self.to_seconds(delaytime, unit):
                return self.bot.send_message(m, self.bot.trans.plugins.reminders.strings.wrongdelay)

        alarm = time() + self.to_seconds(delaytime, unit)

        text = all_but_first_word(input)
        if not text:
            return self.bot.send_message(m, self.bot.trans.plugins.reminders.strings.noreminder)

        reminder = DictObject(OrderedDict())
        reminder.id = '%s:%s' % (m.sender.id, time())
        reminder.alarm = alarm
        reminder.chat_id = m.conversation.id
        reminder.text = text
        reminder.first_name = m.sender.first_name
        if m.sender.username:
            reminder.username = m.sender.username

        self.bot.reminders = wait_until_received('reminders/' + self.bot.name)
        self.sort_reminders()
        self.bot.reminders['list'].append(reminder)
        self.sort_reminders()

        if unit == 's':
            delay = delay.replace('s', ' seconds')
        if unit == 'm':
            delay = delay.replace('m', ' minutes')
        if unit == 'h':
            delay = delay.replace('h', ' hours')
        if unit == 'd':
            delay = delay.replace('d', ' days')

        message = self.bot.trans.plugins.reminders.strings.added % (
            m.sender.first_name, delay, text)

        return self.bot.send_message(m, message, extra={'format': 'HTML'})

    def cron(self):
        self.bot.reminders = wait_until_received('reminders/' + self.bot.name)
        if not 'list' in self.bot.reminders or not self.bot.reminders['list']:
            self.bot.reminders['list'] = []

        while len(self.bot.reminders['list']) > 0 and self.bot.reminders['list'][0].alarm < time():
            reminder = self.bot.reminders['list'][0]
            text = '<i>%s</i>\n - %s' % (reminder.text, reminder.first_name)
            if 'username' in reminder:
                text += ' (@%s)' % reminder.username

            m = Message(None, Conversation(reminder.chat_id), None, None)
            self.bot.send_message(m, text, extra={'format': 'HTML'})
            self.bot.reminders['list'].remove(reminder)
            self.sort_reminders()
            set_data('reminders/%s' % self.bot.name, self.bot.reminders)

    @staticmethod
    def to_seconds(delaytime, unit):
        if unit == 's':
            return float(delaytime)
        elif unit == 'm':
            return float(delaytime) * 60
        elif unit == 'h':
            return float(delaytime) * 60 * 60
        elif unit == 'd':
            return float(delaytime) * 60 * 60 * 24

    def sort_reminders(self):
        logging.info('sort_reminders: %s' % self.bot.reminders)
        if not 'list' in self.bot.reminders or not self.bot.reminders['list']:
            self.bot.reminders['list'] = []

        if len(self.bot.reminders['list']) > 0:
            self.bot.reminders['list'] = sorted(
                self.bot.reminders['list'], key=lambda k: k.alarm)

        set_data('reminders/%s' % self.bot.name, self.bot.reminders)
