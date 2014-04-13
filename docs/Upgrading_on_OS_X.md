Upgrading on OS X
=====================
This document assumes OS X 10.8.4 or better and that you have an existing installation of Sal, installed using the [instructions provided](https://github.com/grahamgilbert/sal/blob/master/docs/os-x.md). If you don't have an existing installation, you just need to follow the installation instructions.

##Upgrade guide
Start a Terminal session

Switch to the service account

	su saluser
	
	
Change into the Sal virtualenv directory
	
	cd /usr/local/sal_env

Activate the virtualenv

	source bin/activate

Change into the Sal directory and update the code from GitHub

	cd sal
	git pull
	
Run the migration so your database is up to date
	
	python manage.py migrate

Exit the virtual environment, theLaunchDaemon will reload the process automatically.
