
function unlock-excel() {
    FNAME=$1
    echo "Unlock $FNAME"
    TIMESTAMP="$(date "+%Y%m%d-%H%M%S")"
    TMPDIR="/tmp/unlock-excel-${TIMESTAMP}"
    mkdir $TMPDIR
    FZIP=${$(basename $FNAME)/\.xlsx/.zip}
    cp $FNAME $TMPDIR/$FZIP
    cd $TMPDIR
    unzip $FZIP
    sed -i '' 's/<sheetProtection[^>]*>//' xl/worksheets/sheet*.xml
    zip -u $FZIP xl/worksheets/sheet*.xml
    cd -
    FUNLOCKED=${FNAME/\.xlsx/-unlocked.xlsx}
    cp $TMPDIR/$FZIP ${FNAME/\.xlsx/-unlocked.xlsx}
    echo "Unlocked version at $FUNLOCKED"
}
