"""Build data/election2569.json from the election-69-OCR-result dataset.

Usage:
    git clone --depth 1 https://github.com/killernay/election-69-OCR-result ocr
    python scripts/build_data.py ocr/data/matched data/election2569.json

Source: ECT Form สส.6/1 (via OCR by Chanon Ngernthongdee, election-69-OCR-result).
"""
import json
import os
import sys
from collections import Counter, defaultdict

# 2550 (2007) proportional-representation areas, 10 seats each.
# บึงกาฬ (split from หนองคาย in 2554) is assigned to area 3 with หนองคาย.
PR2550 = {
    1: "เชียงใหม่ เชียงราย แม่ฮ่องสอน พะเยา น่าน ลำปาง ลำพูน แพร่ สุโขทัย ตาก กำแพงเพชร",
    2: "นครสวรรค์ อุทัยธานี เพชรบูรณ์ พิจิตร พิษณุโลก ชัยภูมิ ขอนแก่น ลพบุรี อุตรดิตถ์",
    3: "หนองคาย บึงกาฬ อุดรธานี เลย นครพนม สกลนคร หนองบัวลำภู กาฬสินธุ์ มุกดาหาร มหาสารคาม อำนาจเจริญ",
    4: "ร้อยเอ็ด ยโสธร อุบลราชธานี ศรีสะเกษ สุรินทร์ บุรีรัมย์",
    5: "นครราชสีมา นครนายก ปราจีนบุรี สระแก้ว ฉะเชิงเทรา ชลบุรี ระยอง จันทบุรี ตราด ปทุมธานี",
    6: "กรุงเทพมหานคร นนทบุรี สมุทรปราการ",
    7: "กาญจนบุรี สุพรรณบุรี นครปฐม ราชบุรี เพชรบุรี ประจวบคีรีขันธ์ ชุมพร ระนอง ชัยนาท สิงห์บุรี อ่างทอง พระนครศรีอยุธยา สระบุรี สมุทรสาคร สมุทรสงคราม",
    8: "สุราษฎร์ธานี พังงา นครศรีธรรมราช กระบี่ ภูเก็ต ตรัง พัทลุง สตูล สงขลา ปัตตานี นราธิวาส ยะลา",
}
# Obvious OCR misspellings of party names in constituency results -> canonical name.
# Ambiguous variants (e.g. "ชาติ", "ไทยสร้างชาติ") are left as-is; none of them won a seat.
ALIASES = {
    "บ้านเมือง": "เพื่อบ้านเมือง", "รวมไทยสร้าง": "รวมไทยสร้างชาติ", "รวมไทยสร้างชา": "รวมไทยสร้างชาติ",
    "ไทยก้าวใหม": "ไทยก้าวใหม่", "ฟิวชน": "ฟิวชัน", "แรงงานสร้างไทย": "แรงงานสร้างชาติ",
    "ปวงชนชาวไทย": "ปวงชนไทย", "กลาธรรม": "กล้าธรรม", "กล้าธรรรม": "กล้าธรรม", "กล้าทา": "กล้าธรรม",
    "ประชาธิปัติย์": "ประชาธิปัตย์", "ประชาธิปปัตย์": "ประชาธิปัตย์", "พลังประชาชารัฐ": "พลังประชารัฐ",
    "พรรคเศรษฐกิจ": "เศรษฐกิจ",
}
PROV_TO_PR = {p: g for g, names in PR2550.items() for p in names.split()}

REGION_OVERRIDE = {"10": "กรุงเทพฯ", "11": "กลาง", "12": "กลาง", "13": "กลาง", "25": "ตะวันออก",
                   "26": "กลาง", "27": "ตะวันออก", "60": "เหนือ", "61": "เหนือ", "62": "เหนือ", "63": "เหนือ",
                   "64": "เหนือ", "65": "เหนือ", "66": "เหนือ", "67": "เหนือ", "70": "ตะวันตก", "71": "ตะวันตก",
                   "72": "กลาง", "73": "กลาง", "74": "กลาง", "75": "กลาง", "76": "ตะวันตก", "77": "ตะวันตก"}


def region(code):
    return REGION_OVERRIDE.get(code) or {"1": "กลาง", "2": "ตะวันออก", "3": "อีสาน", "4": "อีสาน",
                                         "5": "เหนือ", "6": "เหนือ", "7": "ตะวันตก", "8": "ใต้", "9": "ใต้"}[code[0]]


def main(src, out):
    pl_dir = os.path.join(src, "party_list")
    cs_dir = os.path.join(src, "constituency")

    # canonical party code -> most common name
    names = defaultdict(Counter)
    pl = {}
    for fn in sorted(os.listdir(pl_dir)):
        d = json.load(open(os.path.join(pl_dir, fn), encoding="utf-8"))
        key = f"{d['province_code']}_{d['constituency_number']}"
        votes = {}
        for p in d["matched_parties"]:
            code = str(p["party_code"])
            names[code][p["party"]] += 1
            votes[code] = votes.get(code, 0) + int(p.get("votes") or 0)
        pl[key] = {"v": votes, "s": d["summary"]}

    parties = {c: n.most_common(1)[0][0] for c, n in names.items()}
    name_to_code = {v: k for k, v in parties.items()}

    districts = {}
    provinces = {}
    extra = 1000
    for fn in sorted(os.listdir(cs_dir)):
        d = json.load(open(os.path.join(cs_dir, fn), encoding="utf-8"))
        pc = str(d["province_code"])
        pname = d["province_name_normalized"]
        provinces[pc] = pname
        key = f"{pc}_{d['constituency_number']}"
        cands = []
        for c in d["matched_candidates"]:
            pname_party = ALIASES.get(c["party"], c["party"])
            code = name_to_code.get(pname_party)
            if code is None:  # party with district candidates but no party-list entry
                extra += 1
                code = f"x{extra}"
                name_to_code[pname_party] = code
                parties[code] = pname_party
            cands.append({"p": code, "n": c["name"], "v": int(c.get("votes") or 0)})
        cands.sort(key=lambda c: -c["v"])
        districts[key] = {"c": cands, "s": d["summary"]}

    for key, v in pl.items():
        pc = key.split("_")[0]
        if pc not in provinces:
            provinces[pc] = None

    out_d = []
    for key in sorted(set(districts) | set(pl), key=lambda k: (int(k.split("_")[0]), int(k.split("_")[1]))):
        pc, n = key.split("_")
        cs = districts.get(key)
        pv = pl.get(key)
        s = (cs or pv)["s"]
        out_d.append({
            "id": key, "pc": pc, "n": int(n),
            "elig": s.get("eligible_voters"), "came": s.get("voters_came"),
            "good": s.get("good_votes"), "bad": s.get("invalid_votes"), "no": s.get("no_votes"),
            "cand": cs["c"] if cs else None,
            "pl": pv["v"] if pv else None,
            "plGood": pv["s"].get("good_votes") if pv else None,
            "plBad": pv["s"].get("invalid_votes") if pv else None,
            "plNo": pv["s"].get("no_votes") if pv else None,
        })

    prov_list = []
    for pc in sorted(provinces, key=int):
        nm = provinces[pc]
        prov_list.append({"pc": pc, "name": nm, "region": region(pc), "pr2550": PROV_TO_PR.get(nm)})

    missing_group = [p["name"] for p in prov_list if p["pr2550"] is None]
    if missing_group:
        print("WARN no 2550 group:", missing_group)

    json.dump({
        "parties": parties,
        "provinces": prov_list,
        "districts": out_d,
        "missing": {"constituency": ["10_15", "25_2", "55_1"], "party_list": ["10_15", "25_2", "41_6"]},
    }, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("districts", len(out_d), "parties", len(parties), "provinces", len(prov_list))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
