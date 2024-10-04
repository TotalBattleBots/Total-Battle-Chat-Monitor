set enabledelayedexpansion
set kingdoms=56 64 70 82 83 86 87 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111

for %%i in (%kingdoms%) do (
	python .\player_database.py -k %%i
)
