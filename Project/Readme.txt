Radek Duchoň, xducho07

Soubory:
	out.csv - ukázka dat bez chyb
	out.csv_output.txt - ukázka výstupu bez chyb
	out2.csv - ukázka dat s chybami
	out2.csv_output.txt - ukázka výstupu s úspěšně detekovanou chybou
	filter.py - filtr a export důležitých dat do csv
		- spuštění - python3 filter.py
	analyze.py - kód vytvářející statistický model nad prvními dvěmi třetinami dat a testujucím na zbývající třetině
		- spuštění: python3 analyze.py csv_soubor [délka časového okna]
	analyze_func.py - funkce pro analyze.py
	xducho07.pdf - dokumentace