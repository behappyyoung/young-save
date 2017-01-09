alias l="ls -laF"
alias cddev="cd /Users/s0199669/gimp/gimpdev"
# alias venv="source venv/bin/activate"
alias pserver='python -m SimpleHTTPServer 9000'
alias superd='supervisord -c /usr/local/etc/supervisord.ini'
alias superc='supervisorctl -c /usr/local/etc/supervisord.ini'
alias goerp='ssh root@erp.ypark.org'
#alias getdb='scp root@erp.ypark.org:/var/www/erp/herp/db.sqlite3 ./'
#alias getdb2='scp root@erp.ypark.org:/var/www/erp/herp/logdb.sqlite3 ./'
#alias gogl='gcloud compute ssh s0199669@cgs-demo-webservices-instance-group-wprd --zone us-central1-a'
alias gg='ssh -i ~/.ssh/google_compute_engine -A 10.249.16.3'

export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagaced
export PATH=/Users/s0199669/bin:$PATH ##/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
PS1='\[\033[01;32m\]\u\033[01;31m\]@\033[01;32m\]\h\[\033[00m\] : \[\033[06;33m\]\w\[\033[00m\]\$ '
function cdc() {
if [ ! $1 ]
then	
	echo "move to gcloud gims"
	cd /Users/s0199669/gcloud/gims
elif [ $1 == 'gc' ]
then
	echo 'move to google cloud'
	cd ~/gcloud/gims
elif [ $1 == 'loom' ]
then
	echo 'move to loom'
	cd ~/github/loom				
elif [ $1 == 'git' ]
then
	cd ~/github/
	echo "move to $1"
elif [ $1 == 'herp' ]
then
	echo "move to ~/bitbuck/erp/herp"
	cd ~/bitbuck/erp/herp
elif [ $1 == 'gitp' ]
then
	echo "move to github PythonSampleCodes"
	cd /Users/s0199669/github/PythonSampleCodes	
else
	cd ~/gimp/gimpdev
fi
}
function venv() {
	if [ $1 ]
	then
		source ./$1/bin/activate
	else
		source venv/bin/activate
	fi
}
function prun(){
	if [ ! $1 ]
	then
		python manage.py runserver 
	elif [ $1 == 'dev' ]
	then
		python manage.py runserver  gims-dev.shc.org:8080
	else
		python manage.py runserver 127.0.0.1:$1
	fi
}

# The next line updates PATH for the Google Cloud SDK.
source '/Users/s0199669/Downloads/google-cloud-sdk/path.bash.inc'

# The next line enables shell command completion for gcloud.
source '/Users/s0199669/Downloads/google-cloud-sdk/completion.bash.inc'
