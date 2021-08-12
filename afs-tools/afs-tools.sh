# Utilities for use with AFS. 

function set_afs_perm_recur() {
    find $1 -type d -exec fs sa {} $2 $3 \;
}

function check_keytab() {
    keytab=~/.${USER}.keytab
    if [ ! -e $keytab ] ; then
	make_krb_keytab
    fi
    cp $keytab /tmp
    echo "/tmp/$(basename $keytab)"
}

function afs-screen() {
    if [ -z "$1" ] ; then
	name=default
    else
	name="$1"
    fi
    keytab=$(check_keytab)
    screen -q -raAd $name || pagsh.krb -c "k5reauth -f -k $keytab -- screen -S $name"
}

function afs-tmux() {
    if [ -z "$1" ] ; then
	name=default
    else
	name="$1"
    fi
    keytab=$(check_keytab)
    tmux attach-session -t $name || pagsh.krb -c "k5reauth -f -k $keytab -- tmux new-session -s $name"
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

function make_krb_keytab() {
    # Make the keytab for use at CERN
    keytab.py $USER --algorithms=arcfour-hmac-md5,aes256-cts --and-test
}

