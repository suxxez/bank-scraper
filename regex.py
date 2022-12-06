street = "((Ober|Unter den|An |Im |Platz |Berg |Am |Alt\-).+|(?:([A-Z][a-zäüö-]+){1,2})).([Cc]haussee|[Aa]llee|[sS]tr(\.|(a(ss|ß)e))|[Rr]ing|berg|gasse|grund|hörn| Nord|graben|[mM]arkt|[Uu]fer|[Ss]tieg|[Ll]inden|[Dd]amm|[pP]latz|brücke|Steinbüchel|Burg|stiege|[Ww]eg|rain|park|[Ww]eide|[Hh][oö]f|pfad|garten).+?(\d{1,4})([a-zäöüß]+)?(\-?\d{1,4}[a-zäöüß]?)?"

city = "(\d{5})\s*(.+)?"

#city = "\d{5} [a-zA-Z\u00F0-\u02AF]* [a-zA-Z\u00F0-\u02AF]* [a-zA-Z\u00F0-\u02AF]*"
email = "[\w.+-]+@[\w-]+\.[\w.-]+"