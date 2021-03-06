import logging

from polaris.utils import (get_full_name, get_input, get_target, is_int,
                           set_data)


class plugin(object):
    # Loads the text strings from the bots language #
    def __init__(self, bot):
        self.bot = bot
        self.commands = self.bot.trans.plugins.info.commands
        self.description = self.bot.trans.plugins.info.description

    # Plugin action #
    def run(self, m):
        gid = str(m.conversation.id)
        target = get_target(self.bot, m, get_input(m))

        text = ''
        name = ''
        username = ''
        description = ''
        tags = ''
        messages = 0
        members = 0
        invite_link = None

        gname = ''
        gusername = ''
        gdescription = ''
        gtags = ''
        gmessages = 0
        gmembers = 0
        ginvite_link = None

        if target and int(target) > 0:
            info = self.bot.bindings.server_request(
                'getUser',  {'user_id': int(target)})
            info_full = self.bot.bindings.server_request(
                'getUserFullInfo',  {'user_id': int(target)})

        else:
            if target and target.startswith('-100'):
                info = self.bot.bindings.server_request(
                    'getSupergroup',  {'supergroup_id': int(target[4:])})
                info_full = self.bot.bindings.server_request(
                    'getSupergroupFullInfo',  {'supergroup_id': int(target[4:])})

        if target and (int(target) == 0 or not (target in self.bot.users or target in self.bot.groups or info)):
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        if target:
            if int(target) > 0:
                if target in self.bot.users:
                    name = get_full_name(self.bot, target, False)

                    if 'username' in self.bot.users[target] and self.bot.users[target].username:
                        username = '@' + self.bot.users[target].username

                    if 'description' in self.bot.users[target]:
                        description = self.bot.users[target]['description']

                    messages = self.bot.users[target].messages

                else:
                    if info:
                        self.bot.users[target] = {
                            'first_name': info['first_name'],
                            'last_name': info['last_name'],
                            'messages': 0
                        }

                if info:
                    name = info['first_name'] + ' ' + info['last_name']

                    if len(info['username']) > 0:
                        username = '@' + info['username']
                        self.bot.users[target]['username'] = username

                if info_full:
                    description = info_full['bio']
                    self.bot.users[target]['description'] = description

                set_data('users/%s/%s' %
                         (self.bot.name, target), self.bot.users[target])

                if target in self.bot.tags:
                    for tag in self.bot.tags[target]:
                        tags += tag + ', '
                    tags = tags[:-2]
            else:
                if target in self.bot.groups:
                    if 'title' in self.bot.groups[target] and self.bot.groups[target].title:
                        name = self.bot.groups[target].title

                    if 'username' in self.bot.groups[target]:
                        username = '@' + self.bot.groups[target]['username']

                    if 'description' in self.bot.groups[target]:
                        description = self.bot.groups[target]['description']

                    if 'member_count' in self.bot.groups[target]:
                        members = self.bot.groups[target]['member_count']

                    if 'invite_link' in self.bot.groups[target]:
                        invite_link = self.bot.groups[target]['invite_link']

                    messages = self.bot.groups[target].messages

                else:
                    if info:
                        self.bot.groups[target] = {
                            'title': info['title'],
                            'messages': 0
                        }

                if info:
                    if len(info['username']) > 0:
                        username = '@' + info['username']
                        self.bot.groups[target]['username'] = info['username']

                if info_full:
                    description = info_full['description']
                    members = info_full['member_count']
                    invite_link = info_full['invite_link']
                    self.bot.groups[target]['description'] = description
                    self.bot.groups[target]['member_count'] = members
                    self.bot.groups[target]['invite_link'] = invite_link

                set_data('groups/%s/%s' %
                         (self.bot.name, target), self.bot.groups[target])

                if target in self.bot.tags:
                    for tag in self.bot.tags[target]:
                        tags += tag + ', '
                    tags = tags[:-2]

        else:
            return self.bot.send_message(m, self.bot.trans.errors.no_results, extra={'format': 'HTML'})

        if int(gid) < 0 and not get_input(m):
            if gid in self.bot.groups:
                if 'title' in self.bot.groups[gid] and self.bot.groups[gid].title:
                    gname = self.bot.groups[gid].title

                if 'username' in self.bot.groups[gid]:
                    gusername = '@' + self.bot.groups[gid]['username']

                if 'description' in self.bot.groups[gid]:
                    gdescription = self.bot.groups[gid]['description']

                if 'member_count' in self.bot.groups[gid]:
                    gmembers = self.bot.groups[gid]['member_count']

                if 'invite_link' in self.bot.groups[gid]:
                    ginvite_link = self.bot.groups[gid]['invite_link']

                gmessages = self.bot.groups[gid].messages

                if gid.startswith('-100'):
                    info = self.bot.bindings.server_request(
                        'getSupergroup',  {'supergroup_id': int(gid[4:])})
                    info_full = self.bot.bindings.server_request(
                        'getSupergroupFullInfo',  {'supergroup_id': int(gid[4:])})

                    if info:
                        if len(info['username']) > 0:
                            gusername = '@' + info['username']

                        self.bot.groups[gid]['username'] = info['username']

                    if info_full:
                        gdescription = info_full['description']
                        gmembers = info_full['member_count']
                        ginvite_link = info_full['invite_link']
                        self.bot.groups[gid]['description'] = gdescription
                        self.bot.groups[gid]['member_count'] = gmembers
                        self.bot.groups[gid]['invite_link'] = ginvite_link

            if gid in self.bot.tags:
                for tag in self.bot.tags[gid]:
                    gtags += tag + ', '
                gtags = gtags[:-2]

        if len(username) > 0:
            name += '\n\t     ' + username

        if (target and int(target) > 0):
            text = self.bot.trans.plugins.info.strings.user_info % (
                name, target, messages)
        elif (target and int(target) < 0):
            text += self.bot.trans.plugins.info.strings.group_info % (
                name, target, messages)

        if invite_link and len(invite_link) > 0:
            text += '\n🔗 {}'.format(invite_link)

        if len(tags) > 0:
            text += '\n🏷 {}'.format(tags)

        if len(description) > 0:
            text += '\n\n{}'.format(description)

        if int(gid) < 0 and not get_input(m):
            text += '\n\n'
            if len(gusername) > 0:
                gname += '\n\t     ' + gusername
            text += self.bot.trans.plugins.info.strings.group_info % (
                gname, gid, gmessages)

            if ginvite_link and len(ginvite_link) > 0:
                text += '\n🔗 {}'.format(ginvite_link)

            if len(gtags) > 0:
                text += '\n🏷 {}'.format(gtags)

            if len(gdescription) > 0:
                text += '\n\n{}'.format(gdescription)

        self.bot.send_message(m, text, extra={'format': 'HTML'})
