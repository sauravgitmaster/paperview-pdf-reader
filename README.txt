PAPERVIEW — SIMPLE PDF READER FOR WINDOWS AND MAC

PaperView gives you a clean window for reading PDFs, with page navigation,
zoom, fit-to-page / fit-to-width, text search, and printing.

QUICK START (Windows)
1. Install Python 3 from python.org. During setup, enable the option to add
   Python to PATH.
2. Double-click “Run PaperView on Windows.bat”. It installs the two libraries
   PaperView needs and starts the reader.

MAKE A STANDALONE APP
1. Double-click “Build Windows App.bat”.
2. When it finishes, find PaperView.exe in the new dist folder. Copy that EXE
   wherever you like; Python is not needed to run the built EXE.

DOWNLOAD THE READY-MADE APP
Open the repository's Releases page on GitHub and download the build for your
computer. Windows users download PaperView.exe. Mac users download either
PaperView-macOS-Apple-Silicon.zip. Unzip the Mac download and move PaperView.app
to Applications. On first launch, macOS may ask you to confirm opening the app;
control-click PaperView.app, choose Open, then confirm Open.

USING IT
- Click Open PDF, or press Ctrl+O.
- Use the page field or the arrow buttons to navigate.
- Use + / − or Ctrl+mouse wheel to zoom. Fit page and Fit width reset the view.
- Type a word in the search box and press Enter or click Find. Find again
  cycles to the next matching place.
- Click Print or press Ctrl+P to send the PDF to Windows' default PDF handler.
- You can also open a PDF by dragging it onto PaperView.py, or by launching
  PaperView.exe with a PDF file path.

Running from source or building the app needs an internet connection to
download the required Python packages. The ready-made app opens local PDFs
offline.
