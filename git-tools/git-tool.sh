# Utilities for working with git.

function gen_git_key() {
    if [ ! -e ~/.ssh ] ; then
	mkdir ~/.ssh
    fi
    local keyname=~/.ssh/id_rsa.git
    ssh-keygen -t rsa -b 4096 -f "$keyname" -C "$(git config --get user.email)"
    if [ -z `eval "$(ssh-agent -s)"` ] ; then
	echo "ssh agent isn't running! Can't add git id."
    else
	ssh-add "$keyname"
    fi
    if [ ! -e ~/.ssh/config ] ; then 
	touch ~/.ssh/config
    fi
    local configlines=`sed '1 i\
Host github.com\
\   PubkeyAuthentication yes\
\   IdentityFile '"${keyname}"'\
' ~/.ssh/config`
    echo "$configlines" > ~/.ssh/config
    echo "Public key:"
    cat "${keyname}.pub"
}

function test_git_ssh() {
    ssh -T git@github.com
}

