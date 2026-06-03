# Capacity Sweep Summary

This report aggregates Top 1%, 2%, 5%, and 10% review-capacity results across public/proxy benchmarks.

## Capacity-specific Winners

| dataset | capacity_pct | metric | winner | value |
|---|---|---|---|---|
| paysim | 1 | precision_at_capacity | mechanism_informed_enhanced | 0.126523 |
| paysim | 1 | recall_at_capacity | mechanism_informed_enhanced | 0.378467 |
| paysim | 1 | fraud_loss_capture_rate | logistic_regression | 0.840845 |
| paysim | 2 | precision_at_capacity | mechanism_informed_enhanced | 0.103026 |
| paysim | 2 | recall_at_capacity | mechanism_informed_enhanced | 0.616361 |
| paysim | 2 | fraud_loss_capture_rate | logistic_regression | 0.867829 |
| paysim | 5 | precision_at_capacity | mechanism_informed_enhanced | 0.041210 |
| paysim | 5 | recall_at_capacity | mechanism_informed_enhanced | 0.616361 |
| paysim | 5 | fraud_loss_capture_rate | logistic_regression | 0.889707 |
| paysim | 10 | precision_at_capacity | logistic_regression | 0.026577 |
| paysim | 10 | recall_at_capacity | logistic_regression | 0.795016 |
| paysim | 10 | fraud_loss_capture_rate | mechanism_informed_enhanced | 0.976522 |
| baf | 1 | precision_at_capacity | logistic_regression | 0.079000 |
| baf | 1 | recall_at_capacity | logistic_regression | 0.087680 |
| baf | 1 | fraud_loss_capture_rate | logistic_regression | 0.174354 |
| baf | 2 | precision_at_capacity | mechanism_informed_enhanced | 0.054500 |
| baf | 2 | recall_at_capacity | mechanism_informed_enhanced | 0.120977 |
| baf | 2 | fraud_loss_capture_rate | mechanism_informed_enhanced | 0.233542 |
| baf | 5 | precision_at_capacity | mechanism_informed_enhanced | 0.046600 |
| baf | 5 | recall_at_capacity | mechanism_informed_enhanced | 0.258602 |
| baf | 5 | fraud_loss_capture_rate | mechanism_informed_enhanced | 0.450797 |
| baf | 10 | precision_at_capacity | mechanism_informed_enhanced | 0.035600 |
| baf | 10 | recall_at_capacity | mechanism_informed_enhanced | 0.395117 |
| baf | 10 | fraud_loss_capture_rate | mechanism_informed_enhanced | 0.662430 |
| ieee | 1 | precision_at_capacity | hist_gradient_boosting | 0.253333 |
| ieee | 1 | recall_at_capacity | hist_gradient_boosting | 0.065236 |
| ieee | 1 | fraud_loss_capture_rate | hist_gradient_boosting | 0.118128 |
| ieee | 2 | precision_at_capacity | hist_gradient_boosting | 0.204167 |
| ieee | 2 | recall_at_capacity | hist_gradient_boosting | 0.105150 |
| ieee | 2 | fraud_loss_capture_rate | mechanism_informed_enhanced | 0.167939 |
| ieee | 5 | precision_at_capacity | hist_gradient_boosting | 0.171333 |
| ieee | 5 | recall_at_capacity | hist_gradient_boosting | 0.220601 |
| ieee | 5 | fraud_loss_capture_rate | mechanism_informed_enhanced | 0.243432 |
| ieee | 10 | precision_at_capacity | hist_gradient_boosting | 0.138833 |
| ieee | 10 | recall_at_capacity | hist_gradient_boosting | 0.357511 |
| ieee | 10 | fraud_loss_capture_rate | mechanism_informed_enhanced | 0.363769 |

## Full Capacity Sweep Table

| dataset | model | capacity_pct | precision_at_capacity | recall_at_capacity | fraud_loss_capture_rate | false_negative_loss |
|---|---|---|---|---|---|---|
| paysim | logistic_regression | 1 | 0.114263 | 0.341796 | 0.840845 | 1063906423.370000 |
| paysim | logistic_regression | 2 | 0.065658 | 0.392807 | 0.867829 | 883529190.159999 |
| paysim | logistic_regression | 5 | 0.031528 | 0.471556 | 0.889707 | 737278533.640000 |
| paysim | logistic_regression | 10 | 0.026577 | 0.795016 | 0.971099 | 193195463.989999 |
| paysim | hist_gradient_boosting | 1 | 0.122043 | 0.365068 | 0.109373 | 5953602293.670000 |
| paysim | hist_gradient_boosting | 2 | 0.079764 | 0.477198 | 0.154393 | 5652655276.270000 |
| paysim | hist_gradient_boosting | 5 | 0.035033 | 0.523977 | 0.162470 | 5598663303.330000 |
| paysim | hist_gradient_boosting | 10 | 0.018695 | 0.559238 | 0.165845 | 5576102232.209999 |
| paysim | mechanism_informed_enhanced | 1 | 0.126523 | 0.378467 | 0.637139 | 2425631912.740000 |
| paysim | mechanism_informed_enhanced | 2 | 0.103026 | 0.616361 | 0.667706 | 2221296192.170000 |
| paysim | mechanism_informed_enhanced | 5 | 0.041210 | 0.616361 | 0.667706 | 2221296192.170000 |
| paysim | mechanism_informed_enhanced | 10 | 0.026239 | 0.784908 | 0.976522 | 156942752.650000 |
| baf | logistic_regression | 1 | 0.079000 | 0.087680 | 0.174354 | 719790.000000 |
| baf | logistic_regression | 2 | 0.054000 | 0.119867 | 0.227692 | 673290.000000 |
| baf | logistic_regression | 5 | 0.027400 | 0.152053 | 0.261531 | 643790.000000 |
| baf | logistic_regression | 10 | 0.025400 | 0.281909 | 0.433361 | 493990.000000 |
| baf | hist_gradient_boosting | 1 | 0.026000 | 0.028857 | 0.047030 | 830790.000000 |
| baf | hist_gradient_boosting | 2 | 0.018500 | 0.041065 | 0.060565 | 818990.000000 |
| baf | hist_gradient_boosting | 5 | 0.012200 | 0.067703 | 0.068480 | 812090.000000 |
| baf | hist_gradient_boosting | 10 | 0.016600 | 0.184240 | 0.277131 | 630190.000000 |
| baf | mechanism_informed_enhanced | 1 | 0.079000 | 0.087680 | 0.174354 | 719790.000000 |
| baf | mechanism_informed_enhanced | 2 | 0.054500 | 0.120977 | 0.233542 | 668190.000000 |
| baf | mechanism_informed_enhanced | 5 | 0.046600 | 0.258602 | 0.450797 | 478790.000000 |
| baf | mechanism_informed_enhanced | 10 | 0.035600 | 0.395117 | 0.662430 | 294290.000000 |
| ieee | logistic_regression | 1 | 0.120000 | 0.030901 | 0.029337 | 304574.312000 |
| ieee | logistic_regression | 2 | 0.090833 | 0.046781 | 0.037615 | 301976.730000 |
| ieee | logistic_regression | 5 | 0.101333 | 0.130472 | 0.069939 | 291834.100000 |
| ieee | logistic_regression | 10 | 0.118667 | 0.305579 | 0.127535 | 273761.792000 |
| ieee | hist_gradient_boosting | 1 | 0.253333 | 0.065236 | 0.118128 | 276713.553000 |
| ieee | hist_gradient_boosting | 2 | 0.204167 | 0.105150 | 0.166785 | 261445.949000 |
| ieee | hist_gradient_boosting | 5 | 0.171333 | 0.220601 | 0.229351 | 241813.991000 |
| ieee | hist_gradient_boosting | 10 | 0.138833 | 0.357511 | 0.349823 | 204012.205000 |
| ieee | mechanism_informed_enhanced | 1 | 0.248333 | 0.063948 | 0.116693 | 277163.553000 |
| ieee | mechanism_informed_enhanced | 2 | 0.204167 | 0.105150 | 0.167939 | 261083.854000 |
| ieee | mechanism_informed_enhanced | 5 | 0.169333 | 0.218026 | 0.243432 | 237395.695000 |
| ieee | mechanism_informed_enhanced | 10 | 0.136333 | 0.351073 | 0.363769 | 199636.384000 |

## Interpretation

- This is the most operationally relevant comparison because analyst capacity changes the best model choice.
- Use metric-specific claims rather than claiming one method dominates every dataset and capacity.
- This is public/proxy benchmark evidence only, not JPMC or proprietary bank production evidence.
