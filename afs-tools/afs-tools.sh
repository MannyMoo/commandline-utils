# Utilities for use with AFS. 

function set_afs_perm_recur() {
    find $1 -type d -exec fs sa {} $2 $3 \;
}

function afs-screen() {
    keytab=~/.${USER}.keytab
    if [ ! -e $keytab ] ; then
	make_krb_keytab
    fi
    screen -q -raAd $1 || k5reauth -f -i 3600 -p $USER -k $keytab -- screen -S $1
}

function afs-tmux() {
    keytab=~/.${USER}.keytab
    if [ ! -e $keytab ] ; then
	make_krb_keytab
    fi
    tmux attach-session -t $1 || k5reauth -f -i 3600 -p $USER -k $keytab -- tmux new-session -s $1
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

