from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import argparse
import numpy as np
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--cls_model', type=str, default="")
    parser.add_argument('--batch_size', type=int, default=16)
    FLAGS = parser.parse_args()

    texts = []
    with open(FLAGS.input, 'r', encoding="utf-8") as reader:
        for line in reader:
            data = json.loads(line)
            texts.append(data['text'])

    cls_tokenizer = AutoTokenizer.from_pretrained(FLAGS.cls_model)
    cls_model = AutoModelForSequenceClassification.from_pretrained(FLAGS.cls_model)
    writer = open(FLAGS.output, 'w', encoding="utf-8")
    for i in range(0, len(texts), FLAGS.batch_size):
        batch_text = texts[i:i+FLAGS.batch_size]
        encoding = cls_tokenizer(batch_text, return_tensors='pt')
        labels = torch.tensor([1]).unsqueeze(0)  
        outputs = cls_model(**encoding, labels=labels)
        logits = outputs.logits
        preds = np.argmax(logits.detach().numpy(), axis=1)
        if FLAGS.language == "zh":
            topics = [int(it) for it in preds]
        else:
            topics = [int(it) for it in preds]
        for topic in topics:
            writer.write(topic+"\n")


if __name__ == "__main__":
    main()


