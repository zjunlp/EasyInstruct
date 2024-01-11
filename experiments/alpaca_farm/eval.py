import os
import json
import openai
import argparse

openai.api_key = ''
from alpaca_farm.auto_annotations.analysis import head2head_to_metrics
from alpaca_farm.auto_annotations import PairwiseAutoAnnotator

from easyinstruct.utils.api import set_proxy

set_proxy("http://127.0.0.1:7890")

if 'OPENAI_API_KEY' not in os.environ:
    decoding_kwargs = dict(
        openai_api_key = openai.api_key
    )
    assert decoding_kwargs["openai_api_key"] is not None, "OPENAI_API_KEY not found you should set it in environment or above"
else:
    decoding_kwargs = {}


parser = argparse.ArgumentParser()

parser.add_argument('--baseline', type=str)
parser.add_argument('--target', type=str)

args = parser.parse_args()

if args.baseline.endswith(".jsonl"):
    outputs_baseline = [json.loads(l) for l in open(args.baseline, "r")]
elif args.baseline.endswith(".json"):
    outputs_baseline = json.load(open(args.baseline, "r"))

if args.target.endswith(".jsonl"): 
    outputs_target = [json.loads(l) for l in open(args.target, "r")]
elif args.target.endswith(".json"):
    outputs_target = json.load(open(args.target, "r"))

annotator_pool = PairwiseAutoAnnotator(annotators_config="annotators/test/configs.yaml", **decoding_kwargs)

annotated_sft = annotator_pool.annotate_head2head(outputs_1=outputs_baseline, outputs_2=outputs_target)
res = head2head_to_metrics(preferences=[a["preference"] for a in annotated_sft])

print(f'base: {args.baseline}')
print(f'target: {args.target}')
print(res)
