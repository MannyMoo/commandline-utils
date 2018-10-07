#!/bin/bash

function one-shot-service() {
    name="$1"
    desc="$2"
    script="$3"
    fout="$name.service"
    echo "[Unit]
Description=$desc

[Service]
Type=oneshot
RemainAfterExit=no
ExecStart=$script

[Install]
WantedBy=multi-user.target
" > "$fout"
    sudo cp "$fout" /etc/systemd/system/
    sudo systemctl daemon-reload
}
