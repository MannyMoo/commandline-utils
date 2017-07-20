# Utilities for use with AFS. 

function set_afs_perm_recur() {
    find $1 -type d -exec fs sa {} $2 $3 \;
}

function afs-screen() {
    # Move .screenrc to ~/public so it can be accessed without AFS tokens. 
    # Requires pagsh.krb and k5reauth to be in PATH.
    screen -q -raAd $1 || \
	(pagsh.krb -c "SCREENRC=$HOME/public/.screenrc screen -S $1 -d -m k5reauth \
&& screen -raAd $1")
}

function start-krenew() {
    if [ -z "$(which ps 2> /dev/null)" ] || [ -z "$(which grep 2> /dev/null)" ] || [ -z "$(which krenew 2> /dev/null)" ]
    then
	return 1
    fi

    kproc="$(ps x -u ${USER} | grep krenew | grep ${KRB5CCNAME})"
    if [ -z "${kproc}" ]
    then
        krenew -K 60 -t -k ${KRB5CCNAME} &
    fi
}
