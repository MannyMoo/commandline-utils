
function source_all() {
    if [ ! -z "$1" ] ; then 
	local d="$1"
    else
	local d="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    fi
    for f in `find "$d" -mindepth 1 -name "*.sh"` ; do
	#echo $f
	source $f
    done
}
