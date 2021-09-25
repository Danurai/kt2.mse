import pandas as pd
import numpy


outfile='./kt2cards.mse-game/card_fields.mse'

df = pd.read_excel('./mse-set_creation/kt2cards.xlsx', 'card_fields')

f = open(outfile,'w')

for row in df.itertuples():
	f.write('card field:\n')
	for key in row._fields:
		val=getattr(row,key)
		if not pd.isnull(val):
			if key != 'Index':
				if key == 'choices':
					for choice in val.split(','):
						f.write(f'\tchoice:\t{str(choice)}\n')
				else:
					def b(x): return str(x).lower() if isinstance(x, bool) else str(x).replace('.0','')
					f.write(f'\t{key}:\t{b(val)}\n')
	f.write('\n')

f.close()