# Modelling & Simulation — Final Project (Lab 9)

## Topic
Research-backed stochastic SEIR disease spread model (agent-based) using SimPy.

## External resources used (with citations)
1) Lauer, S. A., Grantz, K. H., Bi, Q., Jones, F. K., Zheng, Q., Meredith, H. R., Azman, A. S., Reich, N. G., & Lessler, J. (2020).
   *The Incubation Period of Coronavirus Disease 2019 (COVID-19) From Publicly Reported Confirmed Cases: Estimation and Application.*
   Annals of Internal Medicine, 172(9), 577–582.
   - Used to parameterize the incubation period distribution (E → I), approximated as LogNormal using median ≈ 5.1 days and 97.5th percentile ≈ 11.5 days.
    - Links:
        Lauer et al. (2020) “The Incubation Period of Coronavirus Disease 2019 (COVID-19)…”
        DOI: https://doi.org/10.7326/M20-0504
        PubMed: https://pubmed.ncbi.nlm.nih.gov/32150748/
   
2) Li, Q., Guan, X., Wu, P., Wang, X., Zhou, L., Tong, Y., Ren, R., Leung, K. S. M., Lau, E. H. Y., Wong, J. Y., Xing, X., Xiang, N., Wu, Y., Li, C., Chen, Q., Li, D., Liu, T., Zhao, J., Liu, M., ... Feng, Z. (2020).
   *Early Transmission Dynamics in Wuhan, China, of Novel Coronavirus–Infected Pneumonia.*
   The New England Journal of Medicine, 382, 1199–1207.
   - Used to justify a baseline reproduction number in the ~2–3 range (we simulate R0 ≈ 2.2 as a baseline scenario).
   - Links:
        Li et al. (2020) “Early Transmission Dynamics in Wuhan, China, of Novel Coronavirus–Infected Pneumonia.”
        DOI: https://doi.org/10.1056/NEJMoa2001316
        NEJM page: https://www.nejm.org/doi/full/10.1056/NEJMoa2001316
        PubMed: https://pubmed.ncbi.nlm.nih.gov/31995857/
    
3) He, X., Lau, E. H. Y., Wu, P., Deng, X., Wang, J., Hao, X., Lau, Y. C., Wong, J. Y., Guan, Y., Tan, X., Mo, X., Chen, Y., Liao, B., Chen, W., Hu, F., Zhang, Q., Zhong, M., Wu, Y., Zhao, L., ... Leung, G. M. (2020).
   *Temporal dynamics in viral shedding and transmissibility of COVID-19.*
   Nature Medicine, 26, 672–675.
   - Used as qualitative support to set an infectious period on the order of about a week in the simplified model.
   - Links:
        He et al. (2020) “Temporal dynamics in viral shedding and transmissibility of COVID-19.”
        DOI: https://doi.org/10.1038/s41591-020-0869-5
        Nature Medicine page: https://www.nature.com/articles/s41591-020-0869-5
        PubMed: https://pubmed.ncbi.nlm.nih.gov/32296168/
        
## What was extracted and how it is used in the model
- Incubation time (E → I): LogNormal distribution fit from Lauer et al. (median and 97.5% quantile).
- Target baseline R0: chosen around 2.2, consistent with Li et al.
- Infectious duration (I → R): Gamma distribution with mean ~7 days (simplified), supported qualitatively by He et al. (optional extra).

## Scenarios simulated
A) Baseline: constant contacts and transmission probability producing target R0.
B) Intervention: a contact-reduction policy after a chosen day (e.g., day 20), reducing contact rate by a fixed fraction.

## Visual outputs
- Plot 1: SEIR curves over time for Scenario A.
- Plot 2: Comparison of infected curve I(t) and cumulative infected for Scenario A vs B.

## Notes / limitations
- Random mixing (no spatial network), no births/deaths, no vaccination.
- Parameters are simplified and intended for course demonstration.