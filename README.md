# TerraForge

```sh
py src/template_tf.py \
    --input-dir ../../Packages/aws-premium/jinja/templates \
    --output-dir ../../Packages/aws-premium/terraform \
    --data-files ../../Packages/aws-premium/jinja/data/00_base.yaml \
        ../../Packages/aws-premium/jinja/data/01_startup.yaml \
        ../../Packages/aws-premium/jinja/data/02_standard.yaml \
        ../../Packages/aws-premium/jinja/data/03_premium.yaml \
        ../../Packages/aws-premium/jinja/data/10_override.yaml
```
