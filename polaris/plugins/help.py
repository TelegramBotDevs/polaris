import json
import logging

from DictObject import DictObject

from polaris.utils import get_input, is_command, remove_html


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.help.commands
        self.commands.append({
            'command': '/help',
            'description': self.bot.trans.plugins.help.commands[0].description,
            'keep_default': True
        })
        self.commands.append({
            'command': '/genhelp',
            'hidden': True
        })
        self.description = self.bot.trans.plugins.help.description

    # Plugin action #
    def run(self, m):
        input = get_input(m)
        commands = []

        if input:
            for plugin in self.bot.plugins:
                if hasattr(plugin, 'description'):
                    text = plugin.description
                else:
                    text = ''

                if hasattr(plugin, 'commands'):
                    for command in plugin.commands:
                        command = DictObject(command)
                        # If the command is hidden, ignore it #
                        if ('hidden' in command and not command.hidden) or not 'hidden' in command:
                            # Adds the command and parameters#
                            if input in command.command.replace('/', '').rstrip('\s'):
                                text += '\n • ' + \
                                    command.command.replace(
                                        '/', self.bot.config.prefix)
                                if 'parameters' in command and command.parameters:
                                    for parameter in command.parameters:
                                        name, required = list(
                                            parameter.items())[0]
                                        # Bold for required parameters, and italic for optional #
                                        if required:
                                            text += ' <b>&lt;%s&gt;</b>' % name
                                        else:
                                            text += ' [%s]' % name

                                if 'description' in command:
                                    text += '\n   <i>%s</i>' % command.description
                                else:
                                    text += '\n   <i>?¿</i>'

                                return self.bot.send_message(m, text, extra={'format': 'HTML'})
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        if is_command(self, 3, m.content):
            text = ''
        else:
            text = self.bot.trans.plugins.help.strings.commands

        # Iterates the initialized plugins #
        for plugin in self.bot.plugins:
            if hasattr(plugin, 'commands'):
                for command in plugin.commands:
                    command = DictObject(command)
                    # If the command is hidden, ignore it #
                    if not 'hidden' in command or not command.hidden:
                        # Adds the command and parameters#
                        if is_command(self, 3, m.content):
                            show = False
                            if 'parameters' in command and command.parameters:
                                allOptional = True
                                for parameter in command.parameters:
                                    name, required = list(
                                        parameter.items())[0]
                                    if required:
                                        allOptional = False

                                show = allOptional

                            else:
                                show = True

                            if self.bot.config.prefix != '/' and (not 'keep_default' in command or not command.keep_default):
                                show = False

                            if show:
                                text += '\n' + command.command.lstrip('/')

                                if 'description' in command:
                                    text += ' - %s' % command.description
                                    commands.append({
                                        'command': command.command.lstrip('/'),
                                        'description': command.description
                                    })
                                else:
                                    text += ' - ?¿'
                                    commands.append({
                                        'command': command.command.lstrip('/'),
                                        'description': '?¿'
                                    })

                        else:
                            text += '\n • ' + \
                                command.command.replace(
                                    '/', self.bot.config.prefix)
                            if 'parameters' in command and command.parameters:
                                for parameter in command.parameters:
                                    name, required = list(parameter.items())[0]
                                    # Bold for required parameters, and italic for optional #
                                    if required:
                                        text += ' <b>&lt;%s&gt;</b>' % name
                                    else:
                                        text += ' [%s]' % name

                            if 'description' in command:
                                text += '\n   <i>%s</i>' % command.description
                            else:
                                text += '\n   <i>?¿</i>'

        if is_command(self, 3, m.content):
            self.bot.send_message(m, 'setMyCommands', 'api', extra={
                                  'commands': json.dumps(commands)})

        self.bot.send_message(m, text, extra={'format': 'HTML'})

    def inline(self, m):
        input = get_input(m)

        results = []

        for plugin in self.bot.plugins:
            if hasattr(plugin, 'inline') and hasattr(plugin, 'commands'):
                for command in plugin.commands:
                    if not 'hidden' in command or not command.hidden:
                        title = command.command.replace('/', '')

                        if 'description' in command:
                            description = command.description
                        else:
                            description = ''

                        parameters = ''
                        if 'parameters' in command and command.parameters:
                            for parameter in command.parameters:
                                name, required = list(parameter.items())[0]
                                # Bold for required parameters, and italic for optional #
                                if required:
                                    parameters = ' <b>&lt;%s&gt;</b>' % name
                                else:
                                    parameters = ' [%s]' % name

                        results.append({
                            'type': 'article',
                            'id': command.command.replace('/', self.bot.config.prefix),
                            'title': title,
                            'input_message_content': {
                                'message_text': command.command.replace('/', self.bot.config.prefix)
                            },
                            'description': description
                        })

        self.bot.answer_inline_query(m, results)
