
function is_ssh_agent_running() {
    if [ `ps aux | grep 'ssh-agent -s' | wc -l` = 1 ] ; then
	echo 0
    else
	echo 1
    fi
}

function start_ssh_agent() {
    if [ `is_ssh_agent_running` = 0 ] ; then
	eval "$(ssh-agent -s)"
    fi
}
