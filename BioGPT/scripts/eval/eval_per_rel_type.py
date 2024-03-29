import json, os
import pandas as pd

true_positive_sum, pred_sum, true_sum = 0, 0, 0

# change path to file from post processed file
pred_file = "/home/generate_checkpoint_avg.pt.detok.extracted.json"

# change path to gold test.json file
gold_file = "/home/test.json"

# change path to .pmid file
pmids_file = "/home/relis_test.pmid"


def do_eval(preds, pmids, golden):
    num_missing = 0
    fp = 0
    fn = 0
    tn = 0

    produce_fp, produce_tp, produce_fn = 0, 0, 0
    is_a_fp, is_a_tp, is_a_fn = 0, 0, 0
    iro_fp, iro_tp, iro_fn = 0, 0, 0
    syn_fp, syn_tp, syn_fn = 0, 0, 0
    acro_fp, acro_tp, acro_fn = 0, 0, 0
    anaphora_fp, anaphora_tp, anaphora_fn = 0, 0, 0

    columns = ['doc_name', 'gold_rels', 'pred_rels', 'rel_type', 'fp_prediction', "fn_prediction"]
    df = pd.DataFrame(columns=columns)

    for pred, idx in zip(preds, pmids):
        print(idx)
        gold_arg1_set, gold_arg2_set, gold_rel_set, gold_set = set(), set(), set(), set()
        pred_arg1_set, pred_arg2_set, pred_rel_set, pred_set = set(), set(), set(), set()
        gold_rel = ""
        if idx not in golden:
            num_missing += 1
            # print("----Missing:", idx)
            continue
        if golden[idx]["triples"]:
            for tp in golden[idx]["triples"]:
                gold_rel = tp["rel"].strip().lower()
                if gold_rel != "no relation":
                    arg1 = tp["arg1"].strip().lower()
                    arg2 = tp["arg2"].strip().lower()
                    gold_arg1_set.add(arg1)
                    gold_arg2_set.add(arg2)
                    gold_rel_set.add(gold_rel)
                    gold_set.add((arg1, arg2, gold_rel))

        if pred["triple_list_pred"] and pred["triple_list_pred"][0]["subject"] != 'failed':
            for tp in pred["triple_list_pred"]:
                rel = tp["relation"].strip().lower()
                if rel == "no relation" and gold_rel == "no relation":
                    tn += 1
                    continue

                elif gold_rel == "no relation" and rel != "no relation":
                    fp += len(pred_set)
                    continue

                elif gold_rel != "no relation" and rel == "no relation":
                    fn += len(gold_set)
                    continue

                arg1 = tp["subject"].strip().lower()
                arg2 = tp["object"].strip().lower()
                pred_arg1_set.add(arg1)
                pred_arg2_set.add(arg2)
                pred_rel_set.add(rel)
                pred_set.add((arg1, arg2, rel))

        fp_rel = pred_rel_set - gold_rel_set

        new_rows = [
            {'doc_name': idx, 'gold_rels': gold_rel_set, 'pred_rels': pred_rel_set, 'rel_type': "", 'fp_prediction': "",
             'fn_prediction': ""}]
        df = df.append(new_rows, ignore_index=True)

        fp_dic = dict()
        for x in fp_rel:
            fp_lst = set()
            for y in pred_set:
                if y[2] == x:
                    fp_lst.add(y)

            if x == "produces":
                produce_fp += len(fp_lst)
            elif x == "is_a":
                is_a_fp += len(fp_lst)
            elif x == "increases_risk_of":
                iro_fp += len(fp_lst)
            elif x == "is_synon":
                syn_fp += len(fp_lst)
            elif x == "is_acron":
                acro_fp += len(fp_lst)
            elif x == "anaphora":
                anaphora_fp += len(fp_lst)

            fp_dic[x] = fp_lst

        fn_dic = dict()
        fp_dic_2 = dict()

        for z in gold_rel_set:
            gold = set()
            prediction = set()
            for f in gold_set:
                if f[2] == z:
                    gold.add(f)
            for g in pred_set:
                if g[2] == z:
                    prediction.add(g)

            fn_rel = gold - prediction
            tp_rel = gold.intersection(prediction)
            fp_rels = prediction - gold

            if len(fn_rel) or len(tp_rel) or len(fp_rels) > 0:
                if z == "produces":
                    produce_fn += len(fn_rel)
                    produce_tp += len(tp_rel)
                    produce_fp += len(fp_rels)
                elif z == "is_a":
                    is_a_fn += len(fn_rel)
                    is_a_tp += len(tp_rel)
                    is_a_fp += len(fp_rels)
                elif z == "increases_risk_of":
                    iro_fn += len(fn_rel)
                    iro_tp += len(tp_rel)
                    iro_fp += len(fp_rels)
                elif z == "is_synon":
                    syn_fn += len(fn_rel)
                    syn_tp += len(tp_rel)
                    syn_fp += len(fp_rels)
                elif z == "is_acron":
                    acro_fn += len(fn_rel)
                    acro_tp += len(tp_rel)
                    acro_fp += len(fp_rels)
                elif z == "anaphora":
                    anaphora_fn += len(fn_rel)
                    anaphora_tp += len(tp_rel)
                    anaphora_fp += len(fp_rels)

                fn_dic[z] = fn_rel
                fp_dic_2[z] = fp_rels

        if len(fp_dic) > 0:
            for a in fp_dic.keys():
                new_rows = [
                    {'doc_name': "", 'gold_rels': "", 'pred_rels': "", 'rel_type': a, 'fp_prediction': fp_dic[a],
                     'fn_prediction': ""}]
                df = df.append(new_rows, ignore_index=True)

        if len(fn_dic) > 0 or len(fp_dic_2) > 0:
            for b in fn_dic.keys():
                new_rows = [
                    {'doc_name': "", 'gold_rels': "", 'pred_rels': "", 'rel_type': b, 'fp_prediction': fp_dic_2[b],
                     'fn_prediction': fn_dic[b]}]
                df = df.append(new_rows, ignore_index=True)

    # Produce Scores
    P_prod = produce_tp / (produce_tp + produce_fp)
    R_prod = produce_tp / (produce_tp + produce_fn)
    Fscore_prod = 2 * P_prod * R_prod / (P_prod + R_prod)

    print("Produce precision is: ", P_prod)
    print("Produce Recall is: ", R_prod)
    print("Produce F-score is: ", Fscore_prod)

    # Anaphora Scores
    P_ana = anaphora_tp / (anaphora_tp + anaphora_fp)
    R_ana = anaphora_tp / (anaphora_tp + anaphora_fn)
    Fscore_ana = 2 * P_ana * R_ana / (P_ana + R_ana)

    print("Anaphora precision is: ", P_ana)
    print("Anaphora Recall is: ", R_ana)
    print("Anaphora F-score is: ", Fscore_ana)

    # is_a Scores
    P_is_a = is_a_tp / (is_a_tp + is_a_fp)
    R_is_a = is_a_tp / (is_a_tp + is_a_fn)
    Fscore_is_a = 2 * P_is_a * R_is_a / (P_is_a + R_is_a)

    print("is_a precision is: ", P_is_a)
    print("is_a Recall is: ", R_is_a)
    print("is_a F-score is: ", Fscore_is_a)

    # is_acron Scores
    P_is_acron = acro_tp / (acro_tp + acro_fp)
    R_is_acron = acro_tp / (acro_tp + acro_fn)
    Fscore_is_acron = 2 * P_is_acron * R_is_acron / (P_is_acron + R_is_acron)

    print("is_acron precision is: ", P_is_acron)
    print("is_acron Recall is: ", R_is_acron)
    print("is_acron F-score is: ", Fscore_is_acron)

    # is_synon Scores
    P_is_synon = syn_tp / (syn_tp + syn_fp)
    R_is_synon = syn_tp / (syn_tp + syn_fn)
    if P_is_synon == 0.0 or R_is_synon == 0.0:
        Fscore_is_synon = 0.0
    else:
        Fscore_is_synon = 2 * P_is_synon * R_is_synon / (P_is_synon + R_is_synon)

    print("is_synon precision is: ", P_is_synon)
    print("is_synon Recall is: ", R_is_synon)
    print("is_synon F-score is: ", Fscore_is_synon)

    # increase_risk_of Scores
    P_iro = iro_tp / (iro_tp + iro_fp)
    R_iro = iro_tp / (iro_tp + iro_fn)
    if P_iro == 0.0 or R_iro == 0.0:
        Fscore_iro = 0.0
    else:
        Fscore_iro = 2 * P_iro * R_iro / (P_iro + R_iro)

    print("increase_risk_of precision is: ", P_iro)
    print("increase_risk_of Recall is: ", R_iro)
    print("increase_risk_of F-score is: ", Fscore_iro)

    # Overall
    fp = produce_fp + is_a_fp + iro_fp + syn_fp + acro_fp + anaphora_fp
    fn += produce_fn + is_a_fn + iro_fn + syn_fn + acro_fn + anaphora_fn
    tp = produce_tp + is_a_tp + iro_tp + syn_tp + acro_tp + anaphora_tp

    P_overall = tp / (tp + fp)
    R_overall = tp / (tp + fn)
    F_overall = 2 * P_overall * R_overall / (P_overall + R_overall)

    print("Overall precision is: ", P_overall)
    print("Overall Recall is: ", R_overall)
    print("Overall F-score is: ", F_overall)

    # dumps the csv for error analysis
    df.to_csv("/home/error_analysis_rel_type.csv", index=False)


preds = []
with open(pred_file) as reader:
    for line in reader:
        preds.append(json.loads(line))

with open(gold_file) as reader:
    golden = json.load(reader)

with open(pmids_file) as reader:
    if '.json' in pmids_file:
        pmids = json.load(reader)
    else:
        pmids = []
        for line in reader:
            pmids.append(line.strip())

print("\n====File: ", os.path.basename(pred_file))
do_eval(preds, pmids, golden)
