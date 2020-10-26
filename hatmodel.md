# Notes on the HAT Model

- Humans: S-E-I1-I2-R
- Tsetse: S-E-I, with a non-susceptible compartment that flies transition into if not infected in their first bloodmeal or within their first 24 hours after expupation
- Non-reservoir animal hosts (tsetse hosts, not tryps reservoirs): R 
- Reservoir animal hosts (tsetse hosts and tryps reservoirs): S-E-I-R

Humans and cattle are infected by infected flies, flies are infected by stage 1 (I1) infected humans and infected reservoir animals. Flies can take bloodmeals from humans, reservoir animals, and non-reservoir animals.

5% of bloodmeals are taken from humans, 23% from reservoir hosts (assuming pigs could possibly be reservoirs), and 72% from non-reservoir hosts

| Animal Species |  Kamuli  |  Mukono  |  Tororo  |   Total   | +_T. brucei_ |
|----------------|:--------:|:--------:|:--------:|:---------:|-------------:|
| Avian          |  2 (2%)  |     0    |     0    |   2 (1%)  |              |
| Cattle         | 19 (18%) | 30 (32%) | 55 (54%) | 104 (35%) | 15/104 (14%) |
| Dog            |  9 (9%)  |  1 (1%)  |  3 (3%)  |  13 (4%)  |              |
| Human          |  2 (2%)  |  6 (6%)  |  6 (6%)  |  14 (5%)  |              |
| M. lizard      | 23 (22%) | 32 (34%) | 26 (26%) |  81 (27%) |   8/81 (10%) |
| Pig            | 41 (40%) | 17 (18%) | 11 (11%) |  69 (23%) |  13/69 (19%) |
| Rat            |     0    |     0    |     0    |     0     |              |
| Sheep/goat     |  7 (7%)  |  8 (9%)  |     0    |  15 (5%)  |              |
| **Total**      |    103   |    94    |    101   |    298    | 36/254 (14%) |

## Tsetse Fly Infection:

`p-feed` - probability that a fly feeds within 24 hours after expupation  
'1 - p-feed` - probability that a fly does not feed and goes directly to non-susceptible (S->N)  

`p-human-feed` - probability (0.05) that a feeding fly feeds on a human  
`p-feed * p-human-feed` - total probability that a fly feeds on a human  
`p-feed * p-human-feed * infectious-humans / total-humans` - probability that a fly feeds on an infectious human  
`beta-v * p-feed * p-human-feed * infectious-humans / total-humans` - probability that a fly feeds on an infectious human and is, in turn, infected (S->E)  
`(1 - beta-v) * p-feed * p-human-feed * infectious-humans / total-humans` - probability that a fly feeds on an infectious human but is not infected (S->N)  
`p-feed * p-human-feed * (1 - (infectious-humans / total-humans))` - probability that a fly feeds on an non-infectious human (S->N)  

`p-reservoir-feed` - probability (0.23) that a feeding fly feeds on a reservoir host  
`p-feed * p-reservoir-feed` - total probability that a fly feeds on a reservoir host  
`p-feed * p-reservoir-feed * infectious-reservoir / total-reservoir` - probability that a fly feeds on an infectious reservoir host  
`beta-v * p-feed * p-reservoir-feed * infectious-reservoir / total-reservoir` - probability that a fly feeds on an infectious reservoir host and is, int turn, infected (S->E)  
`(1 - beta-v) * p-feed * p-reservoir-feed * infectious-reservoir / total-reservoir` - probability that a fly feeds on an infectious reservoir host but is not infected (S->N)  
`p-feed * p-reservoir-feed * (1 - (infectious-reservoir / total-reservoir))` - probability that a fly feeds on a non-infectious reservoir host (S->N)  

`p-feed * (1 - (p-human-feed + p-reservoir-feed))` - probability that a fly feeds on a non-reservoir host (S->N)  

### Sample Values to Check Math

|parameter       |value|
|----------------|-----|
|p-feed          |0.375|
|p-human-feed    |0.05 |
|beta-v          |0.065|
|p-reservoir-feed|0.23 |

----

Assume 0.0625 (6.25%) infectious human population.
Assume 0.375  (37.5%) infectious reservoir population.

|reaction                                   |equation                                                       |probability|
|-------------------------------------------|---------------------------------------------------------------|:----------|
|feed-infectious-human-infected       (S->E)|p_feed · p_human_feed · infectious_humans · beta_v             |7.61719E-05|
|feed-infectious-human-uninfected     (S->N)|p_feed · p_human_feed · infectious_humans · (1 - beta_v)       |0.001095703|
|feed-uninfectious-human              (S->N)|p_feed · p_human_feed · (1 - infectious_humans)                |0.017578125|
|feed-infectious-reservoir-infected   (S->E)|p_feed · p_reservoir_feed · infectious_reservoir · beta_v      |0.002102344|
|feed-infectious-reservoir-uninfected (S->N)|p_feed · p_reservoir_feed · infectious_reservoir · (1 - beta_v)|0.030241406|
|feed-uninfectious-reservoir          (S->N)|p_feed · p_reservoir_feed · (1 - infectious_reservoir)         |0.05390625 |
|feed-non-infectious-host             (S->N)|p_feed · (1 - (p_human_feed + p_reservoir_feed)                |0.27       |
|dont-feed                            (S->N)|1 - p_feed                                                     |0.625      |
|total probability                          |∑(above)                                                       |1.0        |
