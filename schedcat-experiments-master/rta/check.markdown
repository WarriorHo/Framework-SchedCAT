# check rta_omnilog bound_response_times_omnilog
## $\tau_1$:
e = 2

p = 10

s = 1

preemption_level = 0

## $\tau_2$:
e = 3

p = 15

s = 2

preemption_level = 1

## consumer:
$q_\sigma = min(p) = 10$

preemption_level = -1

## $Delta$ and $beta$
$Delta = 0.3$

$beta = 0.05$

$$
r_i=E_i+b_i+\sum_{\tau_k\in hp_i}\left\lceil\frac{r_i}{p_k}\right\rceil \times E_k+I(\sigma)_{i}
$$

## calculate
$E_1 = 2 + 1 \times 0.3 = 2.3$

$E_2 = 3 + 2 \times 0.3 = 3.6$

$r_1 = 0, r_2 = 0, r_\sigma = 0$

### 1
$S(10) = (10 + 0) / 10 \times 1 + (10 + 0) / 15 \times 2 = 1 + 2 = 3$

$A^* = S(10 + r_\sigma) = S(10) = 3$

$I(\sigma)_1 = r_1 / q_\sigma \times \beta \times A^* = 0 / 10 \times 0.05 \times 3 = 0.15$

$r_1 = 2.3$

$r_2 = 3.6$

### 2
$S(10 + 0.15) = (10.15 + 2.3) / 10 \times 1 + (10.15 + 3.6) / 15 \times 2 = 4$

$A^* = 4$

$r_\sigma = 0.05 \times 4 = 0.2$

$r_1 = 2.5$

$r_2 = 6.1$

### 3
$S(10 + 0.2) = (10.2 + 2.5) / 10 \times 1 + (10.2 + 6.1) / 15 \times 2 = 6$

$A^* = 6$

$r_1 = 2.6$

$r_2 = 6.2$

# check event_residence_time

