'''Update date: 2020-Jan-13'''
import argparse, os, sys, re
from typing import List
import args
from os.path import basename, splitext
import pandas as pd

mentions_update = 0

def extract_indices_from_brat_annotation(indices: str) -> List[int]:
    indices = re.findall(r"\d+", indices)
    indices = sorted([int(i) for i in indices])
    return indices


def parse_parameters(parser=None):
    if parser is None: parser = argparse.ArgumentParser()

    # Required
    parser.add_argument("--input_ann", default="/data/dai031/Corpora/CADEC/cadec/original", type=str)
    parser.add_argument("--input_text", default="/data/dai031/Corpora/CADEC/cadec/text", type=str)
    parser.add_argument("--output_filepath", default="/data/dai031/Experiments/CADEC/all/ann", type=str)
    parser.add_argument("--type_of_interest", default="")

    args, _ = parser.parse_known_args()
    return args


def _get_mention_from_text(text, indices):
    tokens = []
    for i in range(0, len(indices), 2):
        start = int(indices[i])
        end = int(indices[i + 1])
        tokens.append(text[start:end])
    return " ".join(tokens)


if __name__ == "__main__":
    # args = parse_parameters()
    num_annotations = 0
    columns = ['doc_name', "gold_boundary", "gold_text", 'modified_boundary', 'modified_text']
    df = pd.DataFrame(columns=columns)

    with open(args.output_filepath, "w") as out_f:
        for document in os.listdir(args.input_ann):
            with open(os.path.join(args.input_ann, document), "r") as in_f:
                doc_name = splitext(basename(document))[1]
                if doc_name == ".ann":
                    document = document.replace(".ann", "")
                    text = open(os.path.join(args.input_text, "%s.txt" % document)).read()
                    for line in in_f:
                        line = line.strip()
                        if line[0] != "T": continue
                        sp = line.strip().split("\t")
                        assert len(sp) == 3
                        mention = sp[2]
                        sp = sp[1].split(" ")
                        label = sp[0]
                        if args.type_of_interest != "" and args.type_of_interest != label: continue
                        indices = extract_indices_from_brat_annotation(" ".join(sp[1:]))
                        mention_from_text = _get_mention_from_text(text, indices)
                        if mention != mention_from_text:
                            new_rows = [{'doc_name': document, "gold_boundary" : " ".join(sp[1:]), "gold_text": mention, 'modified_boundary':indices, 'modified_text':mention_from_text}]
                            df = df.append(new_rows, ignore_index=True)
                            print("Update the mention from (%s) to (%s)." % (mention, mention_from_text))
                            mention = mention_from_text
                            mentions_update +=1
                        num_annotations += 1

                        # Added ent_id in the end
                        out_f.write("%s\t%s\t%s\t%s\t%s\n" % (document, label, ",".join([str(i) for i in indices]), mention, line.strip().split("\t")[0]))

    print("Extract %d annotations." % num_annotations)
    print("Mentions update: ", mentions_update)
    # df.to_csv(
    #     "/Users/shashankgupta/Documents/Raredis/dai_et_al/corrected_anno_latest/final_correction_data/test_mentions_update.csv",
    #     index=False)

