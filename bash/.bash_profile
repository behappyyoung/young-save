alias l="ls -laF"
alias cddev="cd /Users/s0199669/gimp/gimpdev"
alias superd='supervisord -c /usr/local/etc/supervisord.ini'
alias superc='supervisorctl -c /usr/local/etc/supervisord.ini'

export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagaced
export PATH=/Users/s0199669/bin:$PATH ##/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
PS1='\[\033[01;32m\]\u\033[01;31m\]@\033[01;32m\]\h\[\033[00m\] : \[\033[06;33m\]\w\[\033[00m\]\$ '
function cdc() {
if [ ! $1 ]
then	
	cd ~/gimp/gimpdev
elif [ $1 == 'git' ]
then
	cd ~/github/
	echo "move to $1"
elif [ $1 == 'herp' ]
then
	echo "move to ~/bitbuck/erp/herp"
	cd ~/bitbuck/erp/herp
elif [ $1 == 'dev' ]
then
	echo 'move to dev'
	cd ~/gimp/gimpdev	
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
	if [ $1 ]
	then
		python manage.py runserver 127.0.0.1:$1
	else
		python manage.py runserver 
	fi
}
