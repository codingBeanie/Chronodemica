# Components
Für jede UI-Komponente, die vom HTML-Standard verändert wird, ist eine Komponente unter /src/components/ui anzulegen. Also Button, Slider, Inputs, etc. 
In den .svelte Dateien soll möglichst kein CSS Code stehen müssen, da alles über Komponenten eingebunden wird.
Wiederverwende möglichst oft bereits exsitierende Komponenten, solange es keine große Änderung in der Komponente geben muss. Erstelle also so wenige Buttons und andere UI-Elemente wie nötig, damit es einen einheitlichen Look&Feel gibt.
Komponenten können verschachtelt sein. In einer Card-Komponente kann also die Button-Komponente verwedendet werden. Dafür ist keine neue Button-Komponente zu erzeugen. Sollte sich jedoch das Design unterscheiden (z.B. Farbe) ist dies über Props für die einzelnen Komponenten zu lösen.

# Pages
Sammle hier alle .svelte Dateien, die Pages oder Layouts sind.

# Styling
Nutze tailwind-css um alle Komponenten zu stylen.
Nutze ein minimalistisches, aber modernes Design.
Das Design muss über alle Komponenten einheitlich sein. 
Nutze das definierte Color-Theme in /theme.css

# Theming
Biete mir eine zentrale Datei für das Theming an. Folgende Farben werden benötigt:
* Primary
* Secondary
* Accent
* Success
* Failure
Alle Farben können in drei Abstufungen vorhanden sein (-100, -200, -300). 
Verwende ausschließlich diese Farb-Klassen für alle Komponenten. 