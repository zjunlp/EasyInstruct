config_file=configs/self_instruct.yaml
openai_api_key=""
openai_base_url=""

python demo/run.py \
    --config  $config_file\
    --openai_api_key $openai_api_key \
    --openai_base_url $openai_base_url \