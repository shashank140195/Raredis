# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

SAVE_DIR=/content/BioGPT/checkpoints/RE-Raredis-BioGPT
mkdir -p ${SAVE_DIR}

fairseq-train \
    /content/BioGPT/data/Raredis/relis-bin --save-dir ${SAVE_DIR} \
    --user-dir /content/BioGPT/src \
    --finetune-from-model /content/BioGPT/checkpoints/Pre-trained-BioGPT/checkpoint.pt \
    --task language_modeling_prompt \
    --arch transformer_lm_prompt_biogpt \
    --share-decoder-input-output-embed --decoder-learned-pos \
    --optimizer adam --adam-betas '(0.9, 0.98)' \
    --weight-decay 0.01 --clip-norm 0.0 \
    --lr 1e-4 --lr-scheduler inverse_sqrt --warmup-updates 30 --warmup-init-lr 1e-07 \
    --tokens-per-sample 1024 --max-source-positions 640 --max-target-positions 1024 \
    --max-tokens 1024 --update-freq 32 \
    --skip-invalid-size-inputs-valid-test \
    --max-epoch 100 --keep-last-epochs 5 \
    --learned-prompt 9