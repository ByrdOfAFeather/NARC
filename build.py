from pip._internal.operations.freeze import freeze

with open('requirements.txt', 'w') as f:
	for r in freeze():
		f.write(r)
