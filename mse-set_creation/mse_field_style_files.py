import pandas as pd
import numpy
import re

#msegame='kt2cards'
msegame='kt2'
sheets = ['card_fields', 'card_style', 'extra_card_fields', 'extra_card_style'] 

output_files = {
	'card_fields':				'.mse-game/card_fields.mse',
	'card_style':					'-style.mse-style/card_style.mse',
	'extra_card_fields':  '-style.mse-style/extra_card_fields.mse',
	'extra_card_style':		'-style.mse-style/extra_card_style.mse',
}

def b(x): return str(x).lower() if isinstance(x, bool) else str(x)
def is_style_sheet(s): return re.search('style',sheet) is not None
def get_choices( choices, gamefile, key ):
	#print(key, choices)
	if choices == 'choices' or choices == 'choice_images':
		dfch = pd.read_excel(gamefile, choices)
		return list( filter ( lambda x: not pd.isna(x), dfch[key] ))
	else:
		return choices.split(',')


for sheet in sheets:
	sourcexlsx = f'./mse-set_creation/{msegame}.xlsx'
	outfile=f'./{msegame}{output_files[sheet]}'
	indent = '\t\t' if is_style_sheet(sheet) else '\t'
	df = pd.read_excel(sourcexlsx, sheet)
	f = open(outfile,'w')
	if sheet == 'card_style': f.write('card style:\n')
	if sheet == 'extra_card_style': f.write('extra card style:\n')
	for row in df.itertuples():
		if sheet == 'card_fields': f.write('card field:\n')
		if sheet == 'extra_card_fields': f.write('extra card field:\n')
		fieldname = row.name
		for key in row._fields:
			val=getattr(row,key)
			valindent = '\t' * int((20 - len(key)) / 2)
			if key != 'Index' and not pd.isnull(val):
				if key == 'name' and is_style_sheet(sheet):
					f.write(f'\t{val}:\n')
				elif re.match('font',key) is not None:
					if key == 'font_name':
						f.write(f'{indent}font:\n\t\t\tname:\t{val}\n')
					else:
						attr = re.match('font_(.+)',key)[1]
						f.write(f'{indent}\t{attr}:\t{val}\n')
				elif re.match('symbol_font',key) is not None:
					if key == 'symbol_font_name':
						f.write(f'{indent}symbol_font:\n\t\t\tname:\t{val}\n')
					else:
						attr = re.match('symbol_font_(.+)',key)[1]
						f.write(f'{indent}\t{attr}:\t{val}\n')
				elif key == 'choices':
					for ch in get_choices(val, sourcexlsx, fieldname):
						if re.match('name:', ch):
							chname = re.search('name:\s(.+)',ch)[1]
							f.write(f'{indent}choice:\n{indent}\tname: {chname}\n')
						elif re.match('group choice:',ch) or re.match('choice:',ch):
							f.write(f'{indent}\t{ch}\n')
						else:
							f.write(f'{indent}choice:\t{ch}\n')
				elif key == 'choice_images':
					f.write(f'{indent}choice images:\n')
					for ch in get_choices(val, sourcexlsx, fieldname):
						f.write(f'{indent}\t{ch}\n')
				else:
					val = re.sub('^(\d{1,2})\.0',r'\1',b(val))
					f.write(f'{indent}{key}:{valindent}{val}\n')
		f.write('\n')
	print(f'{sheet} written')
	f.close()