#!/bin/bash

# Get HandBrake presets in python format.

HandBrakeCLI -z >& /tmp/presets.txt

echo 'presets = {'
i=0
short=(vfast fast hq superhq)
for q in 'Very Fast' Fast HQ 'Super HQ' ; do
    for p in 1080 720 576 480 ; do
	echo "    '${short[$i]}_$p' : '$(grep "    $q $p" /tmp/presets.txt | sed 's/    //')',"
    done
    let i+=1
done
echo '}'
