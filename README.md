Ultra-light docker monitor
==========================

This light tool permits:
 - to export docker container memory usage in a database `data.sqlite`
 - display curves of the memory usages in an interactive html report

The export and the display are two different parts. This allows to run the display in another machine.

Install python virtual env
--------------------------
```bash
sudo apt install python3.8 python3.8-venv
python3.8 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

The python env is now callable in `venv/bin/python`.
Or by activating the virtual env:
```bash
./venv/bin/activate
python --version
...
deactivate
```

Configure the stats export
--------------------------
Open the cron tab in edition mode:
```bash
crontab -e
```

Then add a new line (to run the check each 10 minutes)
```bash
*/10 * * * * /path/to/docker-stats-histo/save_docker_stats.sh > /dev/null  2>&1
```


**Note:**
 - Normally cron send task outputs (echo) via mail. As the MTA (Mail Transfer Agent),
may not be set up, the crontab line redirect the outputs into `/dev/null`.
It can also be a path to a log file.
 - No sudo is needed, crontab is called with current user.


Display stats
-------------
This step permits to generate an html interactive render from the sqlite stats file.
It is simple, just run:
```bash
./generate_html.sh
```

The report is now accessible in `stats.html`.


Advanced parameters
-------------------
Both python scripts can have a finer configuration (sqlite and html paths).
To see all accepted parameters use `-h` flag, like
```bash
python save_docker_stats.py -h
python generate_html.py -h
```
