Final Task
Final Task for EPAM Python Training 2021.09 by FirsovaVV

I am proposed to implement Python RSS-reader using python 3.9.

RSS reader is a command-line utility which receives RSS URL and prints results in human-readable format.
Format of the news console output:
$ rss_reader.py https://rssexport.rbc.ru/rbcnews/news/30/full.rss --limit 1
1.
title: Гузеева сообщила, что находится в больнице в Коммунарке три недели

link: https://www.rbc.ru/rbcfreenews/616968439a794773ac304f2b

published: Fri, 15 Oct 2021 15:34:56 +0300

description: Актриса и ведущая программы «Давай поженимся!» Лариса Гузеева сообщила, что уже в течение трех недель находится в московской городской клинической больнице № 40 в Коммунарке, где лечат зараженных коронавирусом.

category: Общество

Utility provides the following interface:
usage: rss_reader.py source [-h] [--version] [--json] [--verbose] [--limit LIMIT] [--date] [--html] [--pdf]

Pure Python command-line RSS reader.

positional arguments:
  source         Input your RSS-link hear. Your link have to start with
                 "https://"

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Outputs verbose status messages
  --limit LIMIT  Limit news topics if this parameter provided
  --date DATE    Choose the date in yyyymmdd format to output news from
                 storage. For example: --date 20191020
  --pdf          Conversion to pdf
  --html         Conversion to html
  --json         Print result as JSON in stdout
  --version      show program's version number and exit

installing the package (if Python is installed, check the version python>=3.9, <3.10)
1. create a folder, put .tar-file to your folder
2. create a virtual environment 
   1. download virtualenv for win 'pip install virtualenv' and for Ubuntu 'sudo apt-get install python3-venv'
   2. create the env for win 'python -m venv env' and for  linux '/usr/bin/python3 -m venv env')
3. activate the environment (for win 'env\Scripts\activate.bat', for Ubuntu 'source env/bin/activate')
4. pip install 'specify the full local path to the folder with the archive format.tar'

The package is ready to use