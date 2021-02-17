# Bachelorarbeit Patrick Malik

## General structure

Das gesamte Projekt ist in einige Teile unterteil. Außerdem ist zu erwähnen, dass der Großteil der Dateien die
Rezensionen beinhalten aufgrund der Größe weggelassen wurde. Das gesamte Projekt hat lokal etwa 45GB, wobei der Großteil
davon von Rezensionen in /csvs/ und /langidTry/ stammt. Alle relevanten Rezensionen sind jedoch in /reviews/ verfügbar.

### bleuComparison

dieser Ordner bietet die Grundlage der Informationen aus Kapitel 2.2 und erzeugt die Lern- bzw. Testdaten für das
restliche Projekt. Ein großer Teil dieses Abschnitts wurde händisch gemacht. Die Dateien englisch.txt und deutsch.txt
kommen aus dem in der Arbeit referenzierten Corpus und werden als Grundlage für die Übersetzung bzw. den Vergleich der
Übersetzungen verwendet. Die beiden python files aws- und azureTranslationRequest senden die notwendigen requests an die
Übersetzungswerkzeuge der jeweiligen Dienste, wobei die, mittlerweile sowieso veralteten, Authentifizierungsdaten
entfernt wurden. Diese Skripte können also aktuell in dieser Form nicht mehr verwendet werden. Je nach Tool mussten dann
weitere Mappings durchgeführt werden. Dieses Mapping passiert in fixLinebreaks.py. Für den BLEU-Vergleich wurden die
jeweiligen Übersetzungen weiters in die gleichnamigen txt-Dateien gespeichert. BLEUMultipleFileComparison errechnet dann
den jeweiligen BLEU-Score, verglichen zu den Übersetzungen, die der Corpus zur Verfügung stellt und gibt ihn aus. Der
Inhalt von deepL.txt und google.txt wurden händisch aus deren online-Übersetzern bezogen, da das zum Zeitpunkt der
Ausführung der billigste oder einfachste Weg war. Diese Infrastruktur wurde in weiterer Folge für das Übersetzen der
Reviews verwendet. Das azureTranslationRequest.py File sendet die ausgewählten deutschen Rezensionen an azure und
speichert die übersetzten Rezensionen zunächst in original/translations. Die Inhalte dieser Dateien werden dann weiter
gemapped, um für diese Versuche verwendbar zus sein.

#### Zusammengefasst

Die Dateien im Ordner original werden als Lern- und Testdaten in der Arbeit verwendet, wobei nachdem
Übersetzungs-Request etwas Nachbearbeitung erfolgen muss. Der BLEU-Score der unterschiedlichen Übersetzungstools kann
mit BLEUMultipleFileComparison.py berechnet werden. Außerdem stellt der Ordner originally_english die
original-englischen Daten zur Verfügung.

### csvs

Dieser Ordner beinhaltet die unerfolgreichen Versuche, deutsche Reviews aus der Menge der mehrsprachigen zu filtern. Die
eigentlichen csvs sind entweder gefilterte Versuche oder das originale File, das die gesammelten Rezensionen zur
Verfügung gestellt hat. Diese sind allerdings aus latzgründen nicht im repository enthalten. Die zugehörigen
shell-Scripts können auch in diesem Ordner gefunden werden. Die Ergebnisse dieses Abschnitts haben es nur als
Unterkapitel in die Arbeit geschafft, sie wurden nicht praktisch weiterverwendet.

### langidTry

Dieser Ordner beinhaltet einen weiteren unerfolgreichen Versuch die deutschen Rezensionen herauszufiltern. In diesem
Fall mit langid. Auch diese Daten wurden nicht weiterverwendet.

### reviews

Beinhaltet zusammengefasst, die in der Arbeit verwendeten Rezensionen. Wobei direkt im Ordner reviews die korrigierten
deutschen Reviews und korrigiert-übersetzten Reviews zur Verfügung gestellt werden. Im Ordner original die
unkorrigierten Pendants und originally-english beinhaltet die unübersetzten englischen Reviews.

### sentimentanalysis

Hierbei handelt es sich um den Kern des Projekts, der die eigentliche Versuche der Arbeit beinhaltet. util.py
beinhaltet, wie zu erwarten, reine util-Funktionen. randomizeFromFiles.py verarbeitet die Rezensionen zu Lern- und
Testdaten sets. In einer früheren Version des Projekts wurde noch keine k-fold Crossvalidation verwendet, daher war ein
anderes System für die Lern- bzw. Testdaten notwendig. Diese Funktionen wurden hier als deprecated markiert. Die
aktuelle Version verwendet hingegen k-fold Crossvalidation und damit die restlichen Funktionen des files. Ganz grob
zusammengefasst wird hier zwischen parallelen und composite file-readern unterschieden. Da in Kapitel 5.1 viele Ansätze
mit den selben Lern- bzw. Testdaten verglichen werden sollen, wird dort der parallele Filereader verwendet. Kapitel 5.2
hingegen basiert auf der Idee, Rezensionen verschiedenen Ursprungs gemeinsam zu verwenden, in unterschiedlichen
Zusammensetzungen. Dafür wird der composite-Filereader verwendet. Generell wird bei allen verwendeten Filereadern darauf
geachtet, dass gleich viele Rezensionen jeder Bewertungsklasse
(1-Stern, 2-Sterne, ...) im Datenset verwendet werden. Da der Inhalt dieses Files nicht selbst verwendet werden muss,
sondern in anderen Abschnitten automatisch angewandt wird, gehe ich nicht weiter auf die Eigenheiten des Codes ein.
Schließlich gibt es noch die beiden relevanten files standard_run.py und transfer_run.py.

#### standard_run.py

Hier wird zum einen das model zur Verfügung gestellt, das für Reviews verwendet wird. Über dieses Model kann entschieden
werden, welche Vorverarbeitungsschritte notwendig sind und wie die Review zurückgegeben werden soll. Es kann also eine
Rezension bspw. als Text, BoW-Vektor oder Vektor für NB zurückgegeben werden. Außerdem befindet sich RunData in diesem
File. In diesem Objekt wird im Prinzip die Infrastruktur eines Durchlaufs gehandhabt. Hier wird geregelt, mit welcher
Sprache welches Klassifizierungswerkzeug aufgerufen werden soll, etc.. Außerdem ist während des Projekts die Größe der
Daten mehrmals zum Problem geworden. Da ein großer Teil der Daten im RAM gehalten wird, aus Rechenzeitgründen auch
teilweise mehrmals in verschiedenen Ausführungen, war es ab einem Punkt notwendig, zu regeln, wie viele Reviews
tatsächlich im RAM gehalten werden. Dafür wird RunData auch in gewisser Weise als Proxy-Objekt verwendet. Die
Main-Funktion der Datei führt den Versuch aus, der in Kapitel 5.1 relevant ist. Es werden die in utils definierten
Werkzeuge verwendet. Außerdem wird in run_data_dict angegeben, welche Dateinamen, welcher Art von Versuch zugeordnet
werden sollen. Diesen Versuchen wird dann auch eine Sprache zugeordnet, um im Durchlauf das Werkzeug der jeweiligen
Sprache verwenden zu können. Hier wird auch das k festgelegt, das in den Versuchen der Arbeit auf 20 gesetzt wurde.
Danach werden die notwendigen Kombinationen an Klassifzieren und Sprachen durchgeführt und letztendlich die Ergebnisse
ausgegeben.

#### transfer_run.py

In diesem Skript wird der Versuch aus Kapitel 5.2 gehandhabt. Eine recht genaue Erklärung welche Kombinationen verwendet
werden, ist im File als Kommentar zu finden. Danach wird lediglich der Versuch ausgeführt. Dieser Teil ist hier deutlich
kürzer, da nur SVM und NB verglichen werden. Außerdem wurden die notwendigen Grundlagen bereits in standard_run.py
geschaffen. Da während des Versuchs kaum unterschieden wird, aus wie vielen Daten ein Set besteht und aus welchen
Partitionen sich dieses zusammensetzt, muss bei der Ausgabe der Genauigkeitswerte diese Liste nochmals aufdividiert
werden, um an die Werte der jeweiligen Kombinationen zu kommen. Ein möglicherweise entwas obskurer Wert ist "partitions"
. Dieser Wert gibt die Anzahl an Partitionen an. Da sich die Partitionen auf ein Datenset mit 4000 Werten beziehen,
erzeugt ein partitions-Wert von 4, 4 Partitionen mit je 1000 Rezensionen. Das führt zu den +0k, +1k, +3k von denen in
der Arbeit die Rede ist.

## Ausführung

Nach dem Klonen dieses repositories muss das repo für GerVADER geklont werden, da die Deutsche Variante von VADER in
dieser Arbeit verwendet wird. Dazu in der project root folgendes git clone command
ausführen: `git clone https://github.com/KarstenAMF/GerVADER.git`. Danach muss das Verzeichnis noch für imports
erkennbar gemacht werden (im Prinzip zum classpath hinzufügen). In JetBrains Produkten muss das repo dafür einfach als
sources-root markiert werden. Ansonsten kann das directory mit
`conda develop GerVADER` hinzugefügt werden. Um die Versuche, wie sie in der Arbeit verwendet wurden, nachzustellen,
sind ein paar Schritte durchzuführen. Zunächst muss sich entschieden werden, welches der beiden Kapitel 5.1 oder 5.2
reproduziert werden soll. Soll der Vergleich aller Werkzeuge unter Verwendung eines parallelen Datensets durchgeführt
werden, also Kapitel 5.1, muss standard_run.py ausgeführt werden. Soll Kapitel 5.2 also die Kombination der Datenbasen,
reproduziert werden, ist transfer_run.py relevant. Danach muss in util.py die "implementations" Liste angepasst werden.
In einem Kommentar darüber sind alle möglichen Optionen aufgelistet. Für Kapitel 5.1 können all diese Optionen verwendet
werden, für Kapitel 5.2 muss die Liste auf
["svm", "nb"] geändert werden. Wenn ein Versuch mit NLP durchgeführt werden soll, muss zunächst ein CoreNLP-Server
gestartet werden. Eine Anleitung kann unter https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK gefunden
werden. Für die Vergleiche in der Arbeit wurde folgendes Command verwendet um den Server zu starten:<br/>
`java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse,sentiment -status_port 9000 -port 9000 -timeout 15000`

Es sei dazu gesagt, dass ein kompletter Durchlauf ein paar Stunden dauern kann. Insbesondere die CoreNLP Implementierung
ist recht langsam.