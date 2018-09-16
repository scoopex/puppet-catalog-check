
Jenkins Infrastruktur
=====================

* Anzeige der letzten Compile Vorgänge
* Anzeige des Trends bei Compilefehlern

![Workflow Skizze](Jenkins_Job.png)

<BR>

* Anzeige der fehlgeschlagenen Hosts nebst deren Environments
* Browsing der erfolgreichen und fehlgeschlagenen Hosts
* Aufruf der Detailergebnisse bzw Compilezeiten

![Workflow Skizze](Jenkins_Job_failed_hosts.png)

<BR>

* Anzeige der Details bei der Kompilierung des Katalogs
* Fehler, Warnungen und Benachrichtigungen

![Workflow Skizze](Jenkins_Job_host_results.png)

* XML Output im JUnit Format
* Automatisiert lesbares Format z.B. für Jenkins

![JUnit_Output.png](JUnit_Output.png)

Output Report
=============

* Anzeige der verschiedenen Meldungen als HTML Tabelle</BR>
* Die Meldungen werden nach Kategorie, Anzahl, Messagetext gruppiert darstellen
  (Individuelle Aspekte wie z.B. Hostnamen in den Meldungen, werden vereinheitlicht)
* Auflisten von Hosts die die genannte Meldung protokolliert haben
* Sortierung nach verschiedenen Aspekten

![Workflow Skizze](Output_Report.png)

JSON Output
===========

* Erzeugter Karalog als JSON Repräsentation
* Einheitliche Sortierung der Elemente für vereinfachtes Vergleichen

![JSON_output.png](JSON_output.png)

