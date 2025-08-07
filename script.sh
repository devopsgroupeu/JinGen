#! /usr/bin/env bash

python3 src/main.py \
       --debug \
       --source git \
       --branch wip \
       --repo-url https://github.com/devopsgroupeu/openprime-infra-templates.git \
       --input-dir templates/ \
       --output-dir rendered_tf/ \
       --data-files 00_base.yaml \
                    01_startup.yaml \
                    02_standard.yaml \
                    03_premium.yaml \
                    04_addons.yaml \
                    10_override.yaml