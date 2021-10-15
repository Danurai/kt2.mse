import pandas as pd
import numpy
import re

msegame='kt2cards'
msegame='kt2'

def b(x): return str(x).lower() if isinstance(x, bool) else str(x)
def is_style_sheet(s): return re.search('style',s) is not None
def get_choices( choices, gamefile, key ):
	if choices == 'choices' or choices == 'choice_images':
		dfch = pd.read_excel(gamefile, choices)
		return list( filter ( lambda x: not pd.isna(x), dfch[key] ))
	else:
		return choices.split(',')

def get_val_indent( key ):
	return '\t' * int((20 - len(key)) / 2)

def write_sheet(sourcexlsx, sheet, sheetname, outfile):
	indent = '\t\t' if is_style_sheet(sheet) else '\t'
	df = pd.read_excel(sourcexlsx, sheetname)
	f = open(outfile,'w')
	if sheet == 'card_style': f.write('card style:\n')
	if sheet == 'extra_card_style': f.write('extra card style:\n')
	for row in df.itertuples():
		if sheet == 'card_fields': f.write('card field:\n')
		if sheet == 'extra_card_fields': f.write('extra card field:\n')
		fieldname = row.name
		for key in row._fields:
			val=getattr(row,key)
			valindent = get_val_indent(key)
			if key != 'Index' and not pd.isnull(val):
				if key == 'name' and is_style_sheet(sheet):
					f.write(f'\t{val}:\n')
				elif re.match('font',key) is not None:
					if key == 'font_name':
						f.write(f'{indent}font:\n')
						f.write(f'\t\t\tname:{get_val_indent("name")}{val}\n')
					else:
						attr = re.match('font_(.+)',key)[1]
						f.write(f'{indent}\t{attr}:{get_val_indent(attr)}{val}\n')
				elif re.match('symbol_font',key) is not None:
					if key == 'symbol_font_name':
						f.write(f'{indent}symbol_font:\n\t\t\tname:{get_val_indent("name")}{val}\n')
					else:
						attr = re.match('symbol_font_(.+)',key)[1]
						f.write(f'{indent}\t{attr}:{get_val_indent(attr)}{val}\n')
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
	print(f'{sheetname} written')
	del df
	f.close()

if __name__ == "__main__":
	sourcexlsx = f'./mse-set_creation/{msegame}.xlsx'
	write_sheet(sourcexlsx, 'card_fields', 'card_fields', f'{msegame}.mse-game/card_fields.mse')

	struct = pd.read_excel(sourcexlsx, 'struct')
	for style in struct.itertuples():
		stylename = style.style_name
		#sheets = ['card_style', 'extra_card_fields', 'extra_card_style']
		write_sheet(sourcexlsx, 'card_style', style.card_style, f'{msegame}-{stylename}.mse-style/card_style.mse')
		write_sheet(sourcexlsx, 'extra_card_fields', style.extra_card_fields, f'{msegame}-{stylename}.mse-style/extra_card_fields.mse')
		write_sheet(sourcexlsx, 'extra_card_style', style.extra_card_style, f'{msegame}-{stylename}.mse-style/extra_card_style.mse')
		