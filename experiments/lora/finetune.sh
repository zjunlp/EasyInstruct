# dataset="evol_instruct_5k"
dataset="self_instruct_5k"
# dataset="alpaca_data_5k"
CUDA_VISIBLE_DEVICES=0 accelerate launch finetune.py --data_path /mnt/16t/oyx/EasyInstruct/data/${dataset}.jsonl --base_model /mnt/16t/share/llama-2-converted/7b --output_dir /mnt/16t/oyx/EasyInstruct/experiments/lora/output/${dataset}