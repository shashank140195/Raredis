import os
import json

#Path to json files
data_dir = "/Users/shashankgupta/Documents/Raredis/BioMedLM/"


def sort_triples(triples, text):
    sorted_triples = sorted(triples, key=lambda x: text.find(x['arg1']))
    return sorted_triples


def build_target_seq_relis(triples):
    answer = ""
    for z in triples:
        rel = z["rel"].lower()
        if rel == "no relation":
            answer = "there are no relations in the abstract; "

        else:
            arg1 = z["arg1"].lower()
            list1 = arg1.split()
            type1 = list1[0]
            if type1 == "raredisease":
                type1 = "rare disease"
            elif type1 == "skinraredisease":
                type1 = "rare skin disease"

            arg2 = z["arg2"].lower()
            list2 = arg2.split()
            type2 = list2[0]
            if type2 == "raredisease":
                type2 = "rare disease"
            elif type2 == "skinraredisease":
                type2 = "rare skin disease"

            if rel == "produces":
                answer += f"{' '.join(list1[1:])} is a {type1} that {rel} {' '.join(list2[1:])}, as a {type2}; "

            elif rel == "anaphora":
                answer += f"the term {' '.join(list2[1:])} is an {type2} that refers back to the entity of the {type1} {' '.join(list1[1:])}; "

            elif rel == "is_synon":
                answer += f"the {type1} {' '.join(list1[1:])} and the {type2} {' '.join(list2[1:])} are synonyms; "

            elif rel == 'is_acron':
                answer += f"the acronym {' '.join(list1[1:])} stands for {' '.join(list2[1:])}, a {type2}; "

            elif rel == 'increases_risk_of':
                answer += f"the presence of the {type1} {' '.join(list1[1:])} increases the risk of developing the {type2} {' '.join(list2[1:])}; "

            elif rel == "is_a":
                answer += f"the {type1} {' '.join(list1[1:])} is a type of {' '.join(list2[1:])}, a {type2}; "

            else:
                answer += f"the relationship between {arg1} and {arg2} is {rel}; "

    return answer[:-2] + "."


def build_target_seq_relis_wo_enttype(triples):
    answer = ""
    for z in triples:
        rel = z["rel"].lower()
        if rel == "no relation":
            answer = "no relations present in the abstract; "

        else:
            arg1 = z["arg1"].lower()
            list1 = arg1.split()

            arg2 = z["arg2"].lower()
            list2 = arg2.split()

            if rel == "produces":
                answer += f"{' '.join(list1[1:])} {rel} {' '.join(list2[1:])}; "

            elif rel == "anaphora":
                answer += f"the term {' '.join(list2[1:])} refers back to the entity {' '.join(list1[1:])}; "

            elif rel == "is_synon":
                answer += f"the {' '.join(list1[1:])} and the {' '.join(list2[1:])} are synonyms; "

            elif rel == 'is_acron':
                answer += f"the acronym {' '.join(list1[1:])} stands for {' '.join(list2[1:])}; "

            elif rel == 'increases_risk_of':
                answer += f"the presence of the {' '.join(list1[1:])} increases the risk of developing the {' '.join(list2[1:])}; "

            elif rel == "is_a":
                answer += f"the {' '.join(list1[1:])} is a type of {' '.join(list2[1:])}; "

            else:
                answer += f"the relationship between {arg1} and {arg2} is {rel}; "

    return answer[:-2] + "."


def loader(fname, fn):
    ret = []
    null_cnt = 0
    suc_cnt = 0
    null_flag = False
    with open(fname, "r", encoding="utf8") as fr:
        data = json.load(fr)
    for pmid, v in data.items():
        content = v["abstract"].strip()

        content = content.lower()
        if v["triples"] is None or len(v["triples"]) == 0:
            if not null_flag:
                print(f"Following PMID in {fname} has no extracted triples:")
                null_flag = True
            print(f"{pmid} ", end="")
            null_cnt += 1

        else:
            triples = v['triples']
            if "arg1" in triples[0].keys():
                triples = sort_triples(triples, content)
            answer = fn(triples)
            ret.append((pmid, content, answer))
            suc_cnt += 1
    if null_flag:
        print("")
    print(f"{len(data)} samples in {fname} has been processed with {null_cnt} samples has no triples extracted.")
    return ret


def dumper(content_list, prefix):
    fw_pmid = open(prefix + ".pmid", "w")
    fw_content = open(prefix + ".source", "w")
    fw_label = open(prefix + ".target", "w")

    for pmid, x, y in content_list:
        print(pmid, file=fw_pmid)
        print(x, file=fw_content)
        print(y, file=fw_label)

    fw_pmid.close()
    fw_content.close()
    fw_label.close()


def worker(fname, prefix, fn):
    ret = loader(fname, fn)
    dumper(ret, prefix)


for split in ['train', 'valid', 'test']:
    worker(os.path.join(f"{data_dir}", f"{split}.json"), os.path.join(f"{data_dir}", split),
           build_target_seq_relis)
