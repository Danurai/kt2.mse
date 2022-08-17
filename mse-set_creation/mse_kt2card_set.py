import os
import re
import json
from zipfile import ZipFile

def convertmarkdown( md, faction ):
	rtn = md
	rtn = md.replace('\n','\n\t\t')
	rtn = re.sub(r"\*(.+?)\*",r"<b>\1</b>",rtn)
	rtn = re.sub(r"\[\[(.+?)\]\]",lambda m: f'<b><color:rgb(227,86,39)>{m[1].upper()}</color></b><sym>S</sym>' if m[1].upper() == faction.upper() else f'<b>{m[1].upper()}</b>',rtn)
	rtn = re.sub(r"\[(\d)\]", r"<sym>\1</sym>", rtn)
	return rtn

def writeploy( file, ploy, faction, type):
	print("writing", type, "ploy:", ploy['name'])
	file.write('card:\n')
	file.write('\trestriction: <color:rgb(227,86,39)>' + faction.upper() + '</color><sym>S</sym>\n')
	file.write('\tname: ' + ploy['name'].upper() + '\n')
	file.write('\ttype: ' + type + ' Ploy' + '\n')
	file.write('\tcost: ' + str(ploy['cp']) + '\n')
	if 'action' in ploy:
		file.write('\teffect:\tAction\n')
		file.write('\trule: ' + convertmarkdown(ploy['text'], faction) + '\n')
		file.write('\taction_cost:\t{}\n'.format(ploy['action']['ap']))
		file.write('\taction_rule:\t{}\n'.format(convertmarkdown(ploy['action']['text'], faction)))
	else:
		file.write('\teffect: Effect\n')
		file.write('\trule:\n\t\t' + convertmarkdown(ploy['text'], faction) + '\n')
	file.write('\n')

def writeitem( file, item, faction):
	print("writing equipment:", item['name'])
	oprestriction = ''
	if 'restriction' in item:
		item['restriction']=[x.upper() for x in item['restriction']]
		oprestriction = '<b>' + ', '.join(item['restriction']) + '</b> only. '
	
	file.write('card:\n')
	file.write(f'\trestriction: <color:rgb(227,86,39)>{faction.upper()}</color><sym>S</sym>\n')
	file.write(f'\tname: {item["name"].upper()}\n')
	file.write('\ttype: Equipment\n')
	file.write('\tcost: {}\n'.format(str(item['cost'])))
	if 'unique' in item: file.write('\tunique: {}\n'.format("yes" if item['unique'] else "no"))
	if 'ability' in item:
		file.write('\trule:\n\t\t{}This operative gains the following ability for the battle:\n\t\t\n\t\t<b>{}:</b> {}\n'.format(oprestriction, item['name'],convertmarkdown(item['ability']['text'], faction)))
		file.write('\teffect:\tAbility\n')
	elif 'weapon' in item:
		file.write('\teffect:\tAttack\n')
		file.write('\trule:\n\t\t{}This operative is equipped with the following {} weapon for the battle:\n'.format(oprestriction, item['type']))
		file.write('\twpn_a: {}\n'.format(str(item['weapon']['a'])))
		file.write('\twpn_bsws: {}+\n'.format(str(item['weapon']['bsws'])))
		file.write('\twpn_d: {}/{}\n'.format(str(item['weapon']['d'][0]), str(item['weapon']['d'][1])))
		if 'sr' in item['weapon']: file.write('\twpn_sr: {}\n'.format(convertmarkdown(', '.join(item['weapon']['sr']), faction)))
		if 'i' in item['weapon']: file.write('\twpn_i: {}\n'.format(convertmarkdown(', '.join(item['weapon']['i']), faction)))
	elif 'action' in item:
		file.write('\teffect:\tAction\n')
		file.write('\trule: ' + convertmarkdown(item['text'], faction) + '\n')
		file.write('\taction_cost:\t{}\n'.format(item['action']['cost']))
		file.write('\taction_rule:\t{}\n'.format(convertmarkdown(item['action']['text'], faction)))
	elif 'text' in item:
		file.write('\teffect:\tEffect\n')
		file.write('\trule: ' + convertmarkdown(item['text'], faction) + '\n')
	file.write('\n')

filename = "../Saved Sets/set"
jsonfile = "./mse-set_creation/kt2data.json"
f = open(filename, "w")

header = {
	"mse_version": "2.0.2",
	"game": "kt2cards",
	"game_version": "2021-09-01",
	"stylesheet": "style",
	"stylesheet_version": "2021-09-01"
}

for key in header:
	f.write( key + ': ' + header[key] + '\n')

ktdata = json.load(open(jsonfile))

for kt in ktdata:
	for sp in (kt['ploys']['strategic']):
		writeploy(f, sp, kt['killteamname'],'Strategic')
	for sp in (kt['ploys']['tactical']):
		writeploy(f, sp, kt['killteamname'],'Tactical')
	for sp in (kt['equipment']):
		writeitem(f, sp, kt['killteamname'])


f.close()

ZipFile('../Saved Sets/pyset.mse-set', 'w').write(filename, 'set')

#os.remove(filename)

# restriction, name, type, cost, rule