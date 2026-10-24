# คะแนนเท่าเดิม สภาไม่เหมือนเดิม (Same Votes, Different House)

Visual analytics prototype: re-count the seats of the 2026 (2569) Thai general election under the party-list
formulas Thailand used in 2540, 2550, 2554 and 2562, and compare with the actual 2569 rule.

**Users & goal:** electoral-system researchers / civil-society groups / legislators reviewing election law —
*how does the seat formula change the composition of the House?*

This is a mathematical simulation for education; it is not a forecast and does not support any party.

## Run
Static site — open via any web server (GitHub Pages works as-is):
```
python3 -m http.server 8000   # then open http://localhost:8000
```

## Views & interactions
| View | Technique | Analytic task |
|---|---|---|
| Rule switcher + knobs | presets, sliders, selects (dynamic query) | define a counterfactual rule |
| Two hemicycles | parliament chart, juxtaposed comparison, click-legend highlight | compare House composition, majority line |
| KPI row | summary numbers | largest party, single-party majority, Gallagher index, # parties |
| Dumbbell chart | actual → scenario seats, tooltip | how many seats change per party |
| Disproportionality bars | diverging bars (seat% − vote%), actual vs scenario | how proportional each formula is |
| Seat-grouping simulator | drag/tap party cards into group A / B, stacked bar vs majority line | does a group of parties reach a majority under each formula |
| 400-district unit chart | grouped by region, margin filter, party highlight, tooltip | where district seats come from; marginal seats |
| Table | details-on-demand / accessible fallback | exact numbers |

## Data
- `data/election2569.json` built by `scripts/build_data.py` from
  [election-69-OCR-result](https://github.com/killernay/election-69-OCR-result) (OCR of ECT Form สส.6/1, by Chanon Ngernthongdee)
- Official source: Election Commission of Thailand, https://www.ect.go.th/ect_th/th/election-2026/
- 2550 PR areas: 8 province groups as used in the 2007 election (บึงกาฬ placed with หนองคาย)

## Limitations
- 397/400 districts (missing กทม.15, ปราจีนบุรี 2, น่าน 1 constituency; อุดรธานี 6 party list); some OCR vote sums don't match.
- District results are held fixed and voters are assumed to vote the same under every rule.
- 2562 used one ballot, so that preset uses district votes summed by party.
