import os
import displayers
eula = False
if os.path.exists(r'..\.\temp/eula.txt'):
	with open(r'..\.\temp/eula.txt', 'r') as test:
		for lines in test.readlines():
			if lines.startswith('User Agreed to EULA'):
				eula = True
is_token = os.path.exists(r'..\.\temp/data/token.json')
main_back_end = displayers.MainBackEnd(is_token=is_token, eula_accepted=eula)
main_back_end.mainloop()

