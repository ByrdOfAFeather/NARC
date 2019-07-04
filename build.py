from pip._internal.operations.freeze import freeze

with open('requirements.txt', 'w') as f:
	for r in freeze():
		if "+mkl" in r:
			# Numpy technically is not a requirement, but is extremely difficult to install on windows with +mkl
			# so I have to not write it out here since it's technically not a separate package (installed whenever
			# you have a compatible system)
			f.write(r.split("+")[0] + "\n")
		else:
			f.write(r + "\n")
