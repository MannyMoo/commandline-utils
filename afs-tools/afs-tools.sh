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
