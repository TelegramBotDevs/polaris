from __main__ import *
from utilies import *

doc = config.command_start + 'define *[term]*\nReturns the first definition for a given term from [Urban Dictionary](http://urbandictionary.com).'

triggers = {
	'^' + config.command_start + 'define',
	'^' + config.command_start + 'ud',
	'^' + config.command_start + 'urbandictionary',
	'^' + config.command_start + 'urban'
}

typing = True

def action(msg):
	input = get_input(msg.text)
		
	if not input:
		return core.send_message(msg.chat.id, doc, parse_mode="Markdown")	
		
	url = 'http://api.urbandictionary.com/v0/define'
	params = {
		'term': input
	}
	
	jstr = requests.get(
		url,
		params = params,
	)
		
	if jstr.status_code != 200:
		return core.send_message(msg.chat.id, config.locale.errors['connection'].format(jstr.status_code), parse_mode="Markdown")
	
	jdat = json.loads(jstr.text)

	if jdat['result_type'] == 'no_results':
		return core.send_message(msg.chat.id, config.locale.errors['results'])

	i = random.randint(1, len(jdat['list']))-1
	
	text = '*' + jdat['list'][i]['word'] + '*\n'
	text += jdat['list'][i]['definition'] + '\n'
	if jdat['list'][i]['example']:
		text += '\nExample:\n_' + jdat['list'][i]['example'] + '_'
	
	core.send_message(msg.chat.id, text, parse_mode="Markdown")