import os
import re
import json
import argparse
from zipfile import ZipFile
from PIL import Image


# Create kt2 data cards from JSON

def convertmarkdown( md, faction ):
	rtn = md
	rtn = md.replace('\n','\n\t\t')
	rtn = re.sub(r"\*(.+?)\*",r"<b>\1</b>",rtn)
	rtn = re.sub(r"\[\[(.+?)\]\]",lambda m: f'<b><color:rgb(227,86,39)>{m[1].upper()}</color></b><sym>S</sym>' if m[1].upper() == faction.upper() else f'<b>{m[1].upper()}</b>',rtn)
	rtn = re.sub(r"\[(\d)\]", r"<sym>\1</sym>", rtn)
	return rtn

def prettywrite(file, key, val):
	tabs = '\t' * int(( 20 - len(key) ) / 2)
	file.write(f'\t{key}:{tabs}{val}\n')

def aua_text( aualist ):
	txt = []
	tabs = '\t' * 2
	for aua in aualist:
		txt.append('\n{}<b>{}{}:</b> {}'.format(tabs, aua['name'], ' ({})'.format(aua['cost']) if 'cost' in aua else'', convertmarkdown(aua['text'],faction) ) )
	return ''.join(txt)
	
def writeoperative( f, op, kt, ft, artno ):
	wpn_count = []
	print(op['role'])
	f.write('card:\n')
	prettywrite( f, 'has_styling', 'false')
	if 'art' in op: prettywrite( f, 'art', f'art{artno}')
	prettywrite( f, 'killteam', kt['name'] )
	prettywrite( f, 'info', op['info'] )
	prettywrite( f, 'fireteamop', '{} ({})'.format(ft['name'], op['role'] ) )
	if 'leader' in op: prettywrite( f, 'leader', 'yes')
	prettywrite( f, 'stat_m', op['stats']['m'] )
	prettywrite( f, 'stat_ga', op['stats']['ga'] )
	prettywrite( f, 'stat_apl', op['stats']['apl'] )
	prettywrite( f, 'stat_df', op['stats']['df'] )
	prettywrite( f, 'stat_sv', str(op['stats']['sv']) + '+' )
	prettywrite( f, 'stat_w', op['stats']['w'] )	
#abilities - name/text
	if 'abilities' in op: prettywrite( f, 'abilities', aua_text(op['abilities']))
#actions	- uniquactions name/cost/text
	if 'uniqueactions' in op: prettywrite( f, 'actions', aua_text(op['uniqueactions']))
	prettywrite( f, 'skill_combat', 'yes' if op['skills']['combat'] else 'no')
	prettywrite( f, 'skill_staunch', 'yes' if op['skills']['staunch'] else 'no')
	prettywrite( f, 'skill_marksman', 'yes' if op['skills']['marksman'] else 'no')
	prettywrite( f, 'skill_scout', 'yes' if op['skills']['scout'] else 'no')
#show_weapons
#wpntblstripes - calculate based on weapons, default 2,4
	# for w in weapons
	for idx, w in enumerate(op['weapons']):
		id = idx+1
		wpn_count.append( f'Slot {id:02d}' )
		if w['type'] == "ranged":
			type = "Ranged" if not 'ammo' in w else "Ranged Ammo"
		elif w['type'] == "combat":
			type = "Combat"
		else:
			type = "Ammo"
		prettywrite( f, f'w{id}type', type)
		prettywrite( f, f'w{id}name', ('- ' if type == "Ammo" else '') + w['name'])
		if type != "Ranged Ammo":
			prettywrite( f, f'w{id}a', w['a'])
			prettywrite( f, f'w{id}bsws', str(w['bsws']) + '+')
			prettywrite( f, f'w{id}dmg', '{}/{}'.format(w['d'][0],w['d'][1]) )
			if 'sr' in w: 
				prettywrite( f, f'w{id}sr', convertmarkdown(', '.join(w['sr']),'') if w['sr'] else '-' ) 
			else:
				prettywrite( f, f'w{id}sr', '-')
			if 'i' in w: 
				prettywrite( f, f'w{id}i', convertmarkdown( ', '.join(w['i']), '') if w['i'] else '-' ) 
			else:
				prettywrite( f, f'w{id}i', '-')
	prettywrite( f, 'wpntblshow', ', '.join(wpn_count) )


if __name__ == "__main__":
	faction = "Harlequins" # Space marines, Craftworlds, Harlequins
	chapter = "TBC" # White Scars, Something Spooky
	filename = "../Saved Sets/set"
	zipfilename = f'../Saved Sets/kt2-{faction.lower().replace(" ","_")}-set.mse-set'
	jsonfile = "./mse-set_creation/kt2data.json"

	f = open(filename, "w")
	zf = ZipFile(zipfilename,'w')

	header = {
		"mse_version": "2.0.2",
		"game": "kt2",
		"game_version": "2021-09-01",
		"stylesheet": "style",
		"stylesheet_version": "2021-09-01"
	}

	for key in header:
		f.write( key + ': ' + header[key] + '\n')

	f.write(f'\nstyling:\n')
	f.write(f'\tkt2-style:\n')
	f.write(f'\t\tChapter:\t\t{chapter}\n\n')
	ktdata = json.load(open(jsonfile))

	kt = list(filter(lambda x: (x['name'] == faction), ktdata))[0]
	artno = 0
	for ft in kt['fireteams']:
		for op in ft['operatives']:
			writeoperative(f, op, kt, ft, artno)
			if 'art' in op:
				# open the image
				art_ratio = 173/149 # w/h
				with Image.open('../Saved sets/setart/{}'.format(op['art'])) as art:
					width, height = art.size
					(cropw, croph) = ( height * art_ratio, width / art_ratio )
					if cropw > width:
						(left, upper, right, lower) = (0, 0, width, croph)
					else:
						(left, upper, right, lower) = (0, 0, cropw, height )
					art_crop = art.crop((left, upper, right, lower))
					art_crop.save(f'art{artno}.png')
				# zip image
				zf.write(f'art{artno}.png',f'art{artno}')
				# delete image
				os.remove(f'art{artno}.png')
				artno += 1


	f.close()

	zf.write(filename, 'set')

	zf.close()
	#os.remove(filename)
