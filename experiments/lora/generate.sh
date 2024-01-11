# dataset="self_instruct_5k"
# dataset="alpaca_data_5k"
dataset="evol_instruct_5k"
CUDA_VISIBLE_DEVICES=1 torchrun --master_port=29502 generate.py \
    --base_model /mnt/16t/share/llama-2-converted/7b \
    --lora_weights /mnt/16t/oyx/EasyInstruct/experiments/lora/output/${dataset}_epoch3 \
    --output_file /mnt/16t/oyx/EasyInstruct/experiments/alpaca_farm/generates/llama2-7b-${dataset}_epoch3.jsonl \
    --input_file /mnt/16t/oyx/EasyInstruct/experiments/alpaca_farm/eval_gpt-3.5-turbo-0301.json \
    --model_name llama2-7b-${dataset}