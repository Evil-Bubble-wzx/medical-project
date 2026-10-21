# 检索错误分析与证据审核包1.0

原标签与分数保持不变。以下是工程观察与待审核候选，不构成医学审核结论。
每题给出原锚点全文、三策略排名及各自前三候选全文；完整前十见原始results.jsonl。

## ENT-001 — 我35岁，有过敏性鼻炎，也总感觉睡不好，资料是否提到鼻炎与睡眠问题的关联？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': 5}

原锚点：

adult-rhinitis-eaaci-2017 / body/sec[1]/p[1] / be0f654d6100bdcb9550e12a

This report was prepared by the European Academy of Allergy and Clinical Immunology (EAACI) Task Force on “Allergic Rhinitis (AR) comorbidities”. This was initiated, based on the rationale that AR is rarely found in isolation and needs to be considered in the context of systemic allergic disease associated with numerous comorbid disorders including asthma, chronic middle ear effusions, sinusitis, lymphoid hypertrophy with obstructive sleep apnea, disordered sleep, and consequent behavioural and educational effects.

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[6] / aca0e617998d6dd0e3faae93

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Certainly the presence of rhinitis, both allergic and non-allergic, is a risk factor for subsequent asthma development [14].

3. adult-rhinitis-eaaci-2017 / body/sec[4]/p[2] / c9f1e17cf990d1563c4c9934

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

A physical examination of all organ systems potentially affected by allergies, with emphasis on the upper respiratory tract, should be performed in patients with a history of rhinitis.

### vector 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[12]/sec[1]/p[1] / 1e32a9d2364c3449d04a3027

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

One study [93] has demonstrated an improvement in OSA in a short-term trial of intranasal fluticasone propionate. The mixed/obstructive apnea-hypopnea index decreased by 4.9 ± 1.0 events per hour in the fluticasone propionate group and increased by 2.2 ± 3.3 events per hour in the placebo group [94]. Craig et al. studied a group of 20 adults with perennial rhinitis and sleep complaints, examining the benefit of twice-daily nasal flunisolide using a double-blind, placebo-controlled, crossover study. They found that nasal congestion and subjective sleep improved significantly in the topical corticosteroid-treated subjects. They concluded that the fatigue in perennial allergies may be a result of nasal congestion and associated sleep fragmentation. Decreasing nasal congestion with nasal steroids may improve sleep, daytime fatigue, and the quality of life of patients with AR [95].

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[12]/p[1] / b0a762477abcf13e31c57f29

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The effect of AR on sleep can impair quality of life [93]. Patients with AR have more difficulties in falling asleep, take more sleeping drugs, suffer from nocturnal awakenings, and feel that they do not get sufficient sleep when compared to healthy controls [94].

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[9]/sec[2]/p[1] / b997ca75567a0d85491d0db5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

AR may have a negative impact on olfactory function and is considered to be a sinonasal-related origin of chemosensory dysfunction [84]. This is probably secondary to a local inflammation in the nasal fossa and around the olfactory neuroepithelium in the olfactory cleft rather than a nasal obstruction impairing the odours to reach the olfactory cleft [82].

### hybrid 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[12]/sec[1]/p[1] / 1e32a9d2364c3449d04a3027

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

One study [93] has demonstrated an improvement in OSA in a short-term trial of intranasal fluticasone propionate. The mixed/obstructive apnea-hypopnea index decreased by 4.9 ± 1.0 events per hour in the fluticasone propionate group and increased by 2.2 ± 3.3 events per hour in the placebo group [94]. Craig et al. studied a group of 20 adults with perennial rhinitis and sleep complaints, examining the benefit of twice-daily nasal flunisolide using a double-blind, placebo-controlled, crossover study. They found that nasal congestion and subjective sleep improved significantly in the topical corticosteroid-treated subjects. They concluded that the fatigue in perennial allergies may be a result of nasal congestion and associated sleep fragmentation. Decreasing nasal congestion with nasal steroids may improve sleep, daytime fatigue, and the quality of life of patients with AR [95].

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[3] / e9097b3973e9630d9a65ada7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

In fact the majority of inflammatory asthma sufferers have some form of upper airway disease (ARIA 2001) [8], either AR, non-allergic rhinitis or rhinosinusitis, usually with nasal polyposis (EPOS 2012) [9]. The extent of inflammation is usually proportional between upper and lower respiratory tracts with equivalence in eosinophils [10] and clinical severity [11].

## ENT-002 — 成人鼻炎除了鼻部表现，还可能同时涉及哪些部位或疾病？

标记：hybrid_missed_anchor, hybrid_lost_single_strategy_hit；原锚点排名：{'keyword': None, 'vector': 10, 'hybrid': None}

原锚点：

adult-rhinitis-eaaci-2017 / body/sec[3]/p[2] / 745acc140de782f6fb2ead9a

These can be subdivided into:Disorders which are part of the spectrum of allergic diseases, e.g. asthma, AD, food allergy, anaphylaxis;Disorders anatomically related to the nose: conjunctivitis, sinusitis, middle ear problems, throat and laryngeal effects;Sleep problems and secondary effects on concentration and behaviour; andTurbinate hypertrophy.

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[6] / aca0e617998d6dd0e3faae93

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Certainly the presence of rhinitis, both allergic and non-allergic, is a risk factor for subsequent asthma development [14].

3. adult-rhinitis-eaaci-2017 / body/sec[4]/p[2] / c9f1e17cf990d1563c4c9934

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

A physical examination of all organ systems potentially affected by allergies, with emphasis on the upper respiratory tract, should be performed in patients with a history of rhinitis.

### vector 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

2. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

3. crs-apac-2024 / body/sec[9]/p[2] / 48d02b1c90d22132535f7a4a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Use of biologics is now established in current guidelines, although differences exist in specific criteria and thresholds [1, 2, 6-8, 27]. The EPOS 2020 guidelines indicate that biologics can be considered if at least 3 of the following 5 features are present; (1) evidence of type 2 inflammation (tissue eosinophilia ≥10 cells/high-power field, or serum eosinophilia ≥250 cells/µL, or total serum IgE ≥100 IU/mL); (2) need for systemic corticosteroids (≥2 courses OCS per year or long-term [>3 months] low-dose steroids) or contraindications for systemic corticosteroids; (3) significantly impaired QoL (eg, with SNOT-22 ≥40); (4) significant loss of smell (anosmia on smell test); (5) with comorbid asthma (requiring regular inhaled corticosteroids) [1, 2]. Looking specifically at the criteria for evidence of type 2 inflammation, in the panel’s view, while evidence of type 2 inflammation is an important criterion, these cutoff thresholds may not be fully appropriate or applicable for Asian populations, and their strict application may obstruct access to patients who may benefit from biologics. For Asian patients, alternative thresholds may apply. Serum eosinophilia ≥250 cells/µL may be the most reliable marker of type 2 inflammation in Asian patients, while a total serum IgE ≥150 IU/mL is more typical of nontype 2 inflammation. Tissue eosinophilia of ≥10 cells/high-power field may be a weak biomarker in Asian patients, where when used to assess status in patients with recurrent disease following surgery, a higher threshold of between 70 and 100 eosinophils per high-power field is used. When considering the need for systemic corticosteroids, patient reluctance or refusal to take systemic steroids should also be taken into account.

### hybrid 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[3] / e9097b3973e9630d9a65ada7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

In fact the majority of inflammatory asthma sufferers have some form of upper airway disease (ARIA 2001) [8], either AR, non-allergic rhinitis or rhinosinusitis, usually with nasal polyposis (EPOS 2012) [9]. The extent of inflammation is usually proportional between upper and lower respiratory tracts with equivalence in eosinophils [10] and clinical severity [11].

2. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

## ENT-003 — 医生说我的过敏问题属于多病共存，这个术语具体是什么意思？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 10, 'hybrid': 10}

原锚点：

adult-rhinitis-eaaci-2017 / body/sec[2]/p[1] / dc7f4ab1b7019829b4a6a9c8

Multimorbidity is the presence of one or more additional disorders (or diseases) co-occurring with a primary disease or disorder; or the effect of such additional disorders or diseases [4]. When the primary organ is not known, the term multimorbidity should be used instead of co-morbidity. In allergic diseases, the term should be multimorbidity.

### keyword 前三候选

### vector 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

2. adult-com-qol-2023 / body/sec[1]/p[1] / fb930c821a577c1be1d03ef7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Chronic otitis media (COM) is a common infectious and/or inflammatory disease with an annual incidence rate of ~4.76% worldwide (1). It is an important preventable and treatable cause of hearing loss (2). Different definitions of COM are used in literature. According to the World Health Organization (WHO), COM is a persistent inflammation of the middle ear and/or mastoid cavity characterized by chronic (at least 2 weeks) or intermittent otorrhea, tympanic membrane perforation, otalgia, ear discomfort and hearing loss (2). Another reported definition is a disease of the middle ear and/or mastoid with irreversible mucosal damage or infection lasting more than 3 months and characterized by a slow progression of symptoms including recurrent infection and hearing loss (3). Furthermore, a variety of terms are used to categorize COM. Nowadays, COM is categorized into chronic suppurative otitis media (CSOM) and COM with cholesteatoma development (4). Another categorization is squamous or mucosal COM, which can be active or inactive. In this categorization, active squamous COM indicates cholesteatoma, inactive squamous means a retraction (pocket)/atelectasis, active mucosal COM suggests a pathology with discharge through a tympanic membrane perforation, and inactive mucosal COM suggests a dry perforation (5). This diversity in terms and definitions indicates a heterogenous study population that should be considered when performing research on this topic and upon interpretation of performed studies. We will refer to the total COM population, consisting of all these terms, as COM w/wo cholesteatoma.

3. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

### hybrid 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

2. adult-com-qol-2023 / body/sec[1]/p[1] / fb930c821a577c1be1d03ef7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Chronic otitis media (COM) is a common infectious and/or inflammatory disease with an annual incidence rate of ~4.76% worldwide (1). It is an important preventable and treatable cause of hearing loss (2). Different definitions of COM are used in literature. According to the World Health Organization (WHO), COM is a persistent inflammation of the middle ear and/or mastoid cavity characterized by chronic (at least 2 weeks) or intermittent otorrhea, tympanic membrane perforation, otalgia, ear discomfort and hearing loss (2). Another reported definition is a disease of the middle ear and/or mastoid with irreversible mucosal damage or infection lasting more than 3 months and characterized by a slow progression of symptoms including recurrent infection and hearing loss (3). Furthermore, a variety of terms are used to categorize COM. Nowadays, COM is categorized into chronic suppurative otitis media (CSOM) and COM with cholesteatoma development (4). Another categorization is squamous or mucosal COM, which can be active or inactive. In this categorization, active squamous COM indicates cholesteatoma, inactive squamous means a retraction (pocket)/atelectasis, active mucosal COM suggests a pathology with discharge through a tympanic membrane perforation, and inactive mucosal COM suggests a dry perforation (5). This diversity in terms and definitions indicates a heterogenous study population that should be considered when performing research on this topic and upon interpretation of performed studies. We will refer to the total COM population, consisting of all these terms, as COM w/wo cholesteatoma.

3. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

## ENT-004 — 我是成年哮喘患者，也长期鼻塞，资料里描述了上下呼吸道疾病的什么联系？

标记：all_strategies_missed_anchor, hybrid_missed_anchor, candidate_label_incompleteness；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[3] / e9097b3973e9630d9a65ada7

In fact the majority of inflammatory asthma sufferers have some form of upper airway disease (ARIA 2001) [8], either AR, non-allergic rhinitis or rhinosinusitis, usually with nasal polyposis (EPOS 2012) [9]. The extent of inflammation is usually proportional between upper and lower respiratory tracts with equivalence in eosinophils [10] and clinical severity [11].

### keyword 前三候选

### vector 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[5] / dc7fbe51d26bc80b151f60fd

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Several possible causal mechanisms have been postulated to explain a link between AR and asthma:Lack of nasal function, i.e. purifying, warming and humidifying inspired air;Nasobronchial reflex (nasal irritants, allergens or cold stimuli);Rhinovirus adhesion theory (increased susceptibility to allergic inflammation and intracellular adhesion molecule (ICAM)-1 expression) [12]; and“Migration” of T cell responses to other tissues after initial sensitization. Braunstahl [13] has shown that allergen challenge in one part of the airway is followed by a response in all other parts;The idea of postnasal drip (carriage of inflammatory cytokines/mediators from nasopharynx to lower airways) has been largely abandoned, since the ‘drip’ travels to the gut, by virtue of the larynx, not to the lower airway, unless the subject is deeply unconscious.

2. crs-apac-2024 / body/sec[4]/p[1] / b98159ca3c8201abf785c217

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

ly one-third of CRSwNP patients have comorbid asthma. In Australia, while the majority of CRSwNP patients show a type 2 inflammatory endotype, in countries such as South Korea and Taiwan, a nontype 2 endotype is more prevalent [21], and where mucosal barrier dysfunction may play a more important role in CRSwNP development.

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

### hybrid 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[5] / dc7fbe51d26bc80b151f60fd

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Several possible causal mechanisms have been postulated to explain a link between AR and asthma:Lack of nasal function, i.e. purifying, warming and humidifying inspired air;Nasobronchial reflex (nasal irritants, allergens or cold stimuli);Rhinovirus adhesion theory (increased susceptibility to allergic inflammation and intracellular adhesion molecule (ICAM)-1 expression) [12]; and“Migration” of T cell responses to other tissues after initial sensitization. Braunstahl [13] has shown that allergen challenge in one part of the airway is followed by a response in all other parts;The idea of postnasal drip (carriage of inflammatory cytokines/mediators from nasopharynx to lower airways) has been largely abandoned, since the ‘drip’ travels to the gut, by virtue of the larynx, not to the lower airway, unless the subject is deeply unconscious.

2. crs-apac-2024 / body/sec[4]/p[1] / b98159ca3c8201abf785c217

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

ly one-third of CRSwNP patients have comorbid asthma. In Australia, while the majority of CRSwNP patients show a type 2 inflammatory endotype, in countries such as South Korea and Taiwan, a nontype 2 endotype is more prevalent [21], and where mucosal barrier dysfunction may play a more important role in CRSwNP development.

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

## ENT-005 — 鼻炎和哮喘一起出现，就能认定鼻炎导致了哮喘吗？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[4] / 3793fa0d7f04914446b8f271

Several possible relations exist between AR and asthma: (a) AR may be statistically associated with asthma; (b) AR may exacerbate coexisting asthma; and (c) AR may have a causal role in the pathogenesis of asthma.

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[6] / aca0e617998d6dd0e3faae93

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Certainly the presence of rhinitis, both allergic and non-allergic, is a risk factor for subsequent asthma development [14].

3. adult-rhinitis-eaaci-2017 / body/sec[4]/p[2] / c9f1e17cf990d1563c4c9934

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

A physical examination of all organ systems potentially affected by allergies, with emphasis on the upper respiratory tract, should be performed in patients with a history of rhinitis.

### vector 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[5] / dc7fbe51d26bc80b151f60fd

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Several possible causal mechanisms have been postulated to explain a link between AR and asthma:Lack of nasal function, i.e. purifying, warming and humidifying inspired air;Nasobronchial reflex (nasal irritants, allergens or cold stimuli);Rhinovirus adhesion theory (increased susceptibility to allergic inflammation and intracellular adhesion molecule (ICAM)-1 expression) [12]; and“Migration” of T cell responses to other tissues after initial sensitization. Braunstahl [13] has shown that allergen challenge in one part of the airway is followed by a response in all other parts;The idea of postnasal drip (carriage of inflammatory cytokines/mediators from nasopharynx to lower airways) has been largely abandoned, since the ‘drip’ travels to the gut, by virtue of the larynx, not to the lower airway, unless the subject is deeply unconscious.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[2] / 71b7bcd21c2c7f0b83de9096

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

In mucosal tissues, mRNA for the ε-chain of IgE was associated with a significant proportion of B cells [65, 66]. Recent evidence has shown local IgE synthesis, local receptor revision, class switch recombination and B-cell differentiation into IgE-secreting plasma cells in NPs [64]. In NPs, the level of IgE is independent of the atopic status of the patient [65, 67, 68] whereas specific IgE in NPs is only partly related to skin prick test positivity [65, 67, 68]. The local IgE in NPs is the result of two types of IgE production: systemic allergic IgE formation and a local polyclonal IgE formation [65, 66]. Local polyclonal IgE correlates with the presence of Staphylococcus aureus enterotoxins (SAE) [9, 65–67]. Finally, Gevaert et al. [69] demonstrated that antagonizing IgE by injections of omalizumab is effective for both allergic and nonallergic CRSwNP. The later finding proves the relevance of local mucosal IgE.

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

### hybrid 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[6] / aca0e617998d6dd0e3faae93

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Certainly the presence of rhinitis, both allergic and non-allergic, is a risk factor for subsequent asthma development [14].

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[3] / e9097b3973e9630d9a65ada7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

In fact the majority of inflammatory asthma sufferers have some form of upper airway disease (ARIA 2001) [8], either AR, non-allergic rhinitis or rhinosinusitis, usually with nasal polyposis (EPOS 2012) [9]. The extent of inflammation is usually proportional between upper and lower respiratory tracts with equivalence in eosinophils [10] and clinical severity [11].

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

## ENT-006 — 我先有鼻炎，后来又出现哮喘，成人观察资料中有没有类似先后顺序？

标记：anchor_hit_control；原锚点排名：{'keyword': 1, 'vector': None, 'hybrid': 3}

原锚点：

adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[6] / aca0e617998d6dd0e3faae93

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Certainly the presence of rhinitis, both allergic and non-allergic, is a risk factor for subsequent asthma development [14].

3. adult-rhinitis-eaaci-2017 / body/sec[4]/p[2] / c9f1e17cf990d1563c4c9934

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

A physical examination of all organ systems potentially affected by allergies, with emphasis on the upper respiratory tract, should be performed in patients with a history of rhinitis.

### vector 前三候选

1. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

2. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

### hybrid 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

2. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

## ENT-007 — 成人过敏性鼻炎通常只是孤立的鼻子问题吗？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-rhinitis-eaaci-2017 / body/sec[3]/p[1] / ec0c183d791351a9698b7357

AR is an organ-specific manifestation of allergic disease. As such, it coexists with other organ-specific disorders that have a common allergic basis. It is therefore rarely found in isolation but frequently has associated multi-morbid disorders [5].

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[6] / aca0e617998d6dd0e3faae93

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Certainly the presence of rhinitis, both allergic and non-allergic, is a risk factor for subsequent asthma development [14].

3. adult-rhinitis-eaaci-2017 / body/sec[4]/p[2] / c9f1e17cf990d1563c4c9934

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

A physical examination of all organ systems potentially affected by allergies, with emphasis on the upper respiratory tract, should be performed in patients with a history of rhinitis.

### vector 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[2] / 71b7bcd21c2c7f0b83de9096

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

In mucosal tissues, mRNA for the ε-chain of IgE was associated with a significant proportion of B cells [65, 66]. Recent evidence has shown local IgE synthesis, local receptor revision, class switch recombination and B-cell differentiation into IgE-secreting plasma cells in NPs [64]. In NPs, the level of IgE is independent of the atopic status of the patient [65, 67, 68] whereas specific IgE in NPs is only partly related to skin prick test positivity [65, 67, 68]. The local IgE in NPs is the result of two types of IgE production: systemic allergic IgE formation and a local polyclonal IgE formation [65, 66]. Local polyclonal IgE correlates with the presence of Staphylococcus aureus enterotoxins (SAE) [9, 65–67]. Finally, Gevaert et al. [69] demonstrated that antagonizing IgE by injections of omalizumab is effective for both allergic and nonallergic CRSwNP. The later finding proves the relevance of local mucosal IgE.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[5] / dc7fbe51d26bc80b151f60fd

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Several possible causal mechanisms have been postulated to explain a link between AR and asthma:Lack of nasal function, i.e. purifying, warming and humidifying inspired air;Nasobronchial reflex (nasal irritants, allergens or cold stimuli);Rhinovirus adhesion theory (increased susceptibility to allergic inflammation and intracellular adhesion molecule (ICAM)-1 expression) [12]; and“Migration” of T cell responses to other tissues after initial sensitization. Braunstahl [13] has shown that allergen challenge in one part of the airway is followed by a response in all other parts;The idea of postnasal drip (carriage of inflammatory cytokines/mediators from nasopharynx to lower airways) has been largely abandoned, since the ‘drip’ travels to the gut, by virtue of the larynx, not to the lower airway, unless the subject is deeply unconscious.

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

### hybrid 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[3] / e9097b3973e9630d9a65ada7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

In fact the majority of inflammatory asthma sufferers have some form of upper airway disease (ARIA 2001) [8], either AR, non-allergic rhinitis or rhinosinusitis, usually with nasal polyposis (EPOS 2012) [9]. The extent of inflammation is usually proportional between upper and lower respiratory tracts with equivalence in eosinophils [10] and clinical severity [11].

3. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

## ENT-008 — 医生说慢性鼻窦炎还要分有鼻息肉和没有鼻息肉，这种分类有资料依据吗？

标记：anchor_hit_control；原锚点排名：{'keyword': 1, 'vector': None, 'hybrid': 9}

原锚点：

crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

### keyword 前三候选

1. crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

2. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

### vector 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

2. crs-apac-2024 / body/sec[11]/p[1] / 4d019dc6091a07a4ae1afbc6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In the present paper, we present key aspects of the current understanding of CRSwNP and provide guidance for physicians within the APAC region and Russia on the clinical management of patients with CRSwNP. Although based upon existing clinical guidelines, a full appraisal of the supportive evidence was beyond the scope of the present paper. The consensus of the panel is that most patients will benefit from a multidisciplinary approach to evaluation and clinical management. Most patients respond to medical treatment (principally focused on topical treatments directed toward inflamed nasal mucosa and adjunctive short-term use of systemic corticosteroids). However, those with more severe/uncontrolled disease require surgery. In this, patient selection is critical (and for some patients, treatment with biologics could be considered at this stage). For those patients with persistent, uncontrolled symptoms despite surgery, biologics should be considered. There remains a need to better characterize CRSwNP patient profiles within the APAC region. Data on the impact of biologics in Asian patients are limited and such data may help in cost-effectiveness evaluations to support use of biologics in the region.

3. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

### hybrid 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

## ENT-009 — 我鼻塞、嗅觉减退已经持续四个月，资料怎样区分慢性和短期鼻窦炎？

标记：anchor_hit_control；原锚点排名：{'keyword': 5, 'vector': 1, 'hybrid': 1}

原锚点：

crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[1]/p[1] / e0e268fee8f54021ad690a24

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The extent of co-occurrence of rhinosinusitis is disputed and is likely to be different in acute rhinosinusitis (ARS), chronic rhinosinusitis (CRS) and CRS with nasal polyposis.

2. crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

3. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

### vector 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

3. crs-apac-2024 / body/sec[9]/p[2] / 48d02b1c90d22132535f7a4a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Use of biologics is now established in current guidelines, although differences exist in specific criteria and thresholds [1, 2, 6-8, 27]. The EPOS 2020 guidelines indicate that biologics can be considered if at least 3 of the following 5 features are present; (1) evidence of type 2 inflammation (tissue eosinophilia ≥10 cells/high-power field, or serum eosinophilia ≥250 cells/µL, or total serum IgE ≥100 IU/mL); (2) need for systemic corticosteroids (≥2 courses OCS per year or long-term [>3 months] low-dose steroids) or contraindications for systemic corticosteroids; (3) significantly impaired QoL (eg, with SNOT-22 ≥40); (4) significant loss of smell (anosmia on smell test); (5) with comorbid asthma (requiring regular inhaled corticosteroids) [1, 2]. Looking specifically at the criteria for evidence of type 2 inflammation, in the panel’s view, while evidence of type 2 inflammation is an important criterion, these cutoff thresholds may not be fully appropriate or applicable for Asian populations, and their strict application may obstruct access to patients who may benefit from biologics. For Asian patients, alternative thresholds may apply. Serum eosinophilia ≥250 cells/µL may be the most reliable marker of type 2 inflammation in Asian patients, while a total serum IgE ≥150 IU/mL is more typical of nontype 2 inflammation. Tissue eosinophilia of ≥10 cells/high-power field may be a weak biomarker in Asian patients, where when used to assess status in patients with recurrent disease following surgery, a higher threshold of between 70 and 100 eosinophils per high-power field is used. When considering the need for systemic corticosteroids, patient reluctance or refusal to take systemic steroids should also be taken into account.

### hybrid 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

## ENT-010 — 我只有鼻塞和嗅觉下降、面部不痛，是否也能检索到慢性鼻窦炎相关症状资料？

标记：anchor_hit_control；原锚点排名：{'keyword': 5, 'vector': 1, 'hybrid': 1}

原锚点：

crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[1]/p[1] / e0e268fee8f54021ad690a24

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The extent of co-occurrence of rhinosinusitis is disputed and is likely to be different in acute rhinosinusitis (ARS), chronic rhinosinusitis (CRS) and CRS with nasal polyposis.

2. crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

3. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

### vector 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

### hybrid 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

## ENT-011 — 成人怀疑慢性鼻窦炎时，为什么资料还要求鼻内镜或CT依据？

标记：anchor_hit_control；原锚点排名：{'keyword': 3, 'vector': 5, 'hybrid': 2}

原锚点：

crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[1]/p[1] / e0e268fee8f54021ad690a24

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The extent of co-occurrence of rhinosinusitis is disputed and is likely to be different in acute rhinosinusitis (ARS), chronic rhinosinusitis (CRS) and CRS with nasal polyposis.

2. crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

3. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

### vector 前三候选

1. crs-apac-2024 / body/sec[6]/p[2] / 7cdefc557964d30b571edc1b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Clinical and laboratory evaluation of CRSwNP follows well-established guidance [1, 2, 6-8, 27]. Both endoscopy and CT have high diagnostic accuracy [2, 28], although choice may differ depending on country and physician specialty. Endoscopy is often preferred by ORL specialists. CT scans may be initially used by physicians in other specialties (and is useful in excluding alternative diagnoses) and in the ORL setting often in later stages of clinical management (eg, in surgical evaluations). For both endoscopy and CT, the extent of sinus disease can be readily assessed using simple commonly used measures [1, 6, 7]. The endoscopic nasal polyp score (NPS) assesses polyp size, number, and extent of sinus involvement to generate a total NPS ranging from 0 to 8, with higher scores indicating more extensive disease [29]. CT evaluation via the Lund–Mackay scoring system (LMS) is long-established (and widely used as an outcome in clinical studies) [30]. This grades each of the paranasal sinuses the basis of no, partial, or complete opacification (scored as 0, 1, or 2, respectively) to generate a total LMS score ranging from 0 to 24 [30].

2. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

3. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

### hybrid 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

## ENT-012 — 医生记录里写的鼻窦炎表型和内型分别指什么？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 1, 'hybrid': 6}

原锚点：

crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[1]/p[1] / e0e268fee8f54021ad690a24

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The extent of co-occurrence of rhinosinusitis is disputed and is likely to be different in acute rhinosinusitis (ARS), chronic rhinosinusitis (CRS) and CRS with nasal polyposis.

2. crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

3. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

### vector 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

2. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

### hybrid 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

3. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

## ENT-013 — 亚洲和西方患者的鼻息肉炎症类型是否完全一样？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 8, 'hybrid': 7}

原锚点：

crs-apac-2024 / body/sec[5]/p[2] / 4d876ba57c3e7e17bceecbb9

To some extent, the focus on CRSwNP in EPOS 2020 is principally in the context of disease driven by type 2 inflammation (reflecting the greater importance in western patient populations). As indicated earlier, while the majority of CRSwNP patients in Australia present with a type 2 inflammatory profile, this is less commonly seen in in South Korea and Taiwan, where a type 2 inflammatory signature may be absent (with the inflammatory profile principally being either type 1 or type 3). There remains a need to develop guidelines that focus on CRSwNP with a nontype 2 inflammatory endotype (and the role of biologics in these patients).

### keyword 前三候选

1. crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

3. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

### vector 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / b98159ca3c8201abf785c217

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

ly one-third of CRSwNP patients have comorbid asthma. In Australia, while the majority of CRSwNP patients show a type 2 inflammatory endotype, in countries such as South Korea and Taiwan, a nontype 2 endotype is more prevalent [21], and where mucosal barrier dysfunction may play a more important role in CRSwNP development.

2. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

3. crs-apac-2024 / body/sec[9]/p[2] / 48d02b1c90d22132535f7a4a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Use of biologics is now established in current guidelines, although differences exist in specific criteria and thresholds [1, 2, 6-8, 27]. The EPOS 2020 guidelines indicate that biologics can be considered if at least 3 of the following 5 features are present; (1) evidence of type 2 inflammation (tissue eosinophilia ≥10 cells/high-power field, or serum eosinophilia ≥250 cells/µL, or total serum IgE ≥100 IU/mL); (2) need for systemic corticosteroids (≥2 courses OCS per year or long-term [>3 months] low-dose steroids) or contraindications for systemic corticosteroids; (3) significantly impaired QoL (eg, with SNOT-22 ≥40); (4) significant loss of smell (anosmia on smell test); (5) with comorbid asthma (requiring regular inhaled corticosteroids) [1, 2]. Looking specifically at the criteria for evidence of type 2 inflammation, in the panel’s view, while evidence of type 2 inflammation is an important criterion, these cutoff thresholds may not be fully appropriate or applicable for Asian populations, and their strict application may obstruct access to patients who may benefit from biologics. For Asian patients, alternative thresholds may apply. Serum eosinophilia ≥250 cells/µL may be the most reliable marker of type 2 inflammation in Asian patients, while a total serum IgE ≥150 IU/mL is more typical of nontype 2 inflammation. Tissue eosinophilia of ≥10 cells/high-power field may be a weak biomarker in Asian patients, where when used to assess status in patients with recurrent disease following surgery, a higher threshold of between 70 and 100 eosinophils per high-power field is used. When considering the need for systemic corticosteroids, patient reluctance or refusal to take systemic steroids should also be taken into account.

### hybrid 前三候选

1. crs-apac-2024 / body/sec[4]/p[1] / b98159ca3c8201abf785c217

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

ly one-third of CRSwNP patients have comorbid asthma. In Australia, while the majority of CRSwNP patients show a type 2 inflammatory endotype, in countries such as South Korea and Taiwan, a nontype 2 endotype is more prevalent [21], and where mucosal barrier dysfunction may play a more important role in CRSwNP development.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[3]/p[1] / 0370c731a72f7a660936113c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Chronic rhinosinusitis with nasal polyps (CRSwNP) is associated with high concentrations of IgE in nasal polyp (NP) tissue. CRSwNP often coexists with asthma and this group is particularly characterized with tissue eosinophilia and high local IgE levels [62]. Therefore, an allergic aetiology of NPs has been presumed, though never firmly demonstrated. Between 0.5 and 4.5% of subjects with AR have NPs, which compares with the normal population [9]. In a retrospective study by Settipane and Chafee [63], the nasal polyps were present in 4.2% of the total population of 4986 subjects. Nasal polyp frequency rate was 6.7% in asthmatic patients and 2.2% in the rhinitis alone group. Of the total 211 cases of nasal polyps, 71% had asthma and 29% had rhinitis alone [63]. Pang et al. [64] reported that food allergen intradermal tests were more positive in nasal polyp patients (81%) compared to controls (11%).

3. crs-apac-2024 / body/sec[2]/p[1] / a2a30fbede2e6b7c624ed556

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

A multidisciplinary expert panel was formed comprising specialists in respiratory allergy and otorhinolaryngology (ORL) from Australia (KS), Hong Kong (RK-YT), the Republic of Korea (YGJ, D-W K), Russia (SK), and Taiwan (T-HY). Panelists were selected based upon experience and expertise in treating CRSwNP, publication record, and involvement in similar activities.

## ENT-014 — 我的鼻窦炎资料上同时写了打喷嚏、鼻痒，这些属于鼻窦炎的核心诊断症状吗？

标记：anchor_hit_control；原锚点排名：{'keyword': 5, 'vector': 1, 'hybrid': 1}

原锚点：

crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[6]/sec[1]/p[1] / e0e268fee8f54021ad690a24

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The extent of co-occurrence of rhinosinusitis is disputed and is likely to be different in acute rhinosinusitis (ARS), chronic rhinosinusitis (CRS) and CRS with nasal polyposis.

2. crs-apac-2024 / body/sec[1]/p[1] / 192dbbb60545314f4246473b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Chronic rhinosinusitis (CRS) is a common often debilitating condition, with a global prevalence of symptomatic disease ranging from 5.5% to 28% [1, 2]. Two broad CRS phenotypes exist, characterized on the basis of the presence or absence of nasal polyps [1, 2]. Patients with chronic rhinosinusitis with nasal polyps (CRSwNP) account for up to 20% of all CRS [3].

3. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

### vector 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

### hybrid 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. crs-apac-2024 / body/sec[3]/p[1] / f5c1a3442f34c776ea442167

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

There are clear diagnostic criteria for rhinosinusitis, CRS, and CRSwNP based upon clinical symptoms and evidence of sinonasal mucosal disease. Diagnosis of acute rhinosinusitis requires the presence of ≥2 symptoms, one of which should be either nasal blockage, obstruction, congestion, or discharge, and either facial pain/pressure, headache and/or reduction, or loss of smell [1, 2]. Confirmation of mucosal disease (presence of polyps, mucopurulent discharge and/or edema, or mucosal obstruction within the ostiomeatal complex or sinuses) via endoscopy or computed tomography (CT) is also required [1, 2]. Although in routine clinical practice, acute rhinosinusitis may be diagnosed on clinical grounds alone, the importance of endoscopic/CT confirmation of CRS (and for CRSwNP) must be emphasized, as endoscopic/CT findings dictate disease classification and subsequent treatment planning. As discussed below, early referral for specialist evaluation and management of CRS (and CRSwNP) is essential.

3. crs-apac-2024 / body/sec[5]/p[1] / ab8d4503309ff24efbfe5436

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

In EPOS 2020, CRS is classified firstly on the basis of disease distribution, that is, localized (unilateral) and diffuse (bilateral), and then on the basis of the dominant endotype (eg, the presence/absence of type 2 inflammation) and the clinical phenotype [1, 2]. Diffuse CRS disease with predominantly type 2 inflammatory endotype includes CRSwNP (although other conditions with predominantly type 2 inflammatory pathways are also included within this category). These include allergic fungal rhinosinusitis (AFRS) and central compartment atopic disease (CCAD), a relatively recently described variant of CRS associated with inhalant allergen exposure [1]. While both AFRS and CCAD are characterized by the presence of polyps, these conditions are classified separately from CRSwNP [1, 2]. AFRS can be distinguished from CRSwNP by the presence of eosinophilic mucin with noninvasive fungal hyphae within the sinonasal mucosa, and often (but not always) a type I hypersensitivity reaction to fungi [2, 22, 23]. In CCAD, polypoid mucosal changes are observed, and while this may seem similar to CRSwNP on CT, these can be differentiated on CT and nasal endoscopy [24].

## ENT-015 — 我是成人，急性中耳炎时同时耳鸣和眩晕，已有研究描述过这些伴随表现吗？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-aom-inner-ear-2023 / body/sec[3]/sec[1]/p[2] / aa337a6d5da92c5e9d6cdd25

The most common symptoms stated by the patients were subjective hearing loss (112/112, 100%), otalgia (111/112, 99%), otorrhea (61/112, 54%), tinnitus (57/112, 51%) and vertigo (34/112). The mean and range of PTA value sorted by the respective symptom was as follows. Hearing loss (33.5 dB, 6.25–71.25 dB), otalgia (33.6 dB, 6.25–71.25 dB), otorrhea (33.3 dB, 6.25–71.25 dB), tinnitus (32.7 dB, 6.25–67.5 dB) and vertigo (39.5 dB, 8.75–67.5 dB). By comparison of the mean PTA of patients with or without a specific symptom, a significantly higher mean PTA (p-value: 0.003) was observed in vertigo patients. Additionally, no other symptom showed a significant decrease or increase in the PTA. Detailed demographics and symptoms according to the groups are displayed in (Table 2).

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

3. adult-com-qol-2023 / body/sec[2]/sec[2]/p[1] / 6c312fdd9b3585d2024d16ca

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Studies published until 18 May 2023 were searched using PubMed, Web of Science, Embase, and Scopus. All four databases were searched with a search string based on the eligibility criteria, without any filters or restrictions applied. The universal search string was composed of “Chronic Otitis Media” OR “Cholesteatoma” (Population), “Quality of Life” (Outcome), and “surgical intervention” (Intervention). An elaborated search string per database is given in Supplementary Table 2. Additionally, a manual search of reference lists of eligible articles was performed.

### vector 前三候选

1. adult-aom-inner-ear-2023 / body/sec[4]/sec[2]/p[3] / 96a6ead15702d779e3023465

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Regarding the clinical findings, the majority of the patients had subjective hearing loss and ear pain. There was also a high percentage of patients with tinnitus (51%) and vertigo (32%). IED may lead to vestibular symptoms ranging from mild dizziness to immobilizing rotatory vertigo, clinically demonstrating itself with various patterns of nystagmus, either irritative, paretic or direction-changing, depending on the pathologic mechanisms and time delay to the initial examination after onset [27,28]. In the current study, no uniform records of nystagmus or apparative diagnostics were performed. Instead, vertigo was assessed from the patient’s history. The prevalence of vertigo was slightly lower compared to the findings in the literature [29]. However, the incidence of vertigo was higher in the interventional group (37%) and operative group (39.5%) compared to the conservative group. New peripheral vertigo may be a factor for a more invasive therapy because it can be considered a sign of pathologic affection of the labyrinth.

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

### hybrid 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-aom-inner-ear-2023 / body/sec[4]/sec[2]/p[3] / 96a6ead15702d779e3023465

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Regarding the clinical findings, the majority of the patients had subjective hearing loss and ear pain. There was also a high percentage of patients with tinnitus (51%) and vertigo (32%). IED may lead to vestibular symptoms ranging from mild dizziness to immobilizing rotatory vertigo, clinically demonstrating itself with various patterns of nystagmus, either irritative, paretic or direction-changing, depending on the pathologic mechanisms and time delay to the initial examination after onset [27,28]. In the current study, no uniform records of nystagmus or apparative diagnostics were performed. Instead, vertigo was assessed from the patient’s history. The prevalence of vertigo was slightly lower compared to the findings in the literature [29]. However, the incidence of vertigo was higher in the interventional group (37%) and operative group (39.5%) compared to the conservative group. New peripheral vertigo may be a factor for a more invasive therapy because it can be considered a sign of pathologic affection of the labyrinth.

3. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

## ENT-016 — 成人急性中耳炎内耳受累这篇研究如何界定研究对象？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-aom-inner-ear-2023 / body/sec[2]/p[1] / 81beb30770e863f1e56467d6

A retrospective, single-center data analysis at the University Hospital of Zurich was performed, including all adult patients between 2000 and 2020 that were diagnosed with AOM with IED. An IED was defined as bone conduction threshold of >15 dB in at least two frequencies between 250 and 4000 Hz with normal hearing on the not affected contralateral side and/or vestibular symptoms. Patients with suppurative labyrinthitis were excluded because of the more severe and irreversible course of the disease.

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

3. adult-com-qol-2023 / body/sec[2]/sec[2]/p[1] / 6c312fdd9b3585d2024d16ca

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Studies published until 18 May 2023 were searched using PubMed, Web of Science, Embase, and Scopus. All four databases were searched with a search string based on the eligibility criteria, without any filters or restrictions applied. The universal search string was composed of “Chronic Otitis Media” OR “Cholesteatoma” (Population), “Quality of Life” (Outcome), and “surgical intervention” (Intervention). An elaborated search string per database is given in Supplementary Table 2. Additionally, a manual search of reference lists of eligible articles was performed.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

2. adult-com-qol-2023 / body/sec[5]/p[1] / 278b0cfa3352da2986cf0def

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In conclusion, this systematic review provides an overview of the evidence that otologic surgical treatment positively impacts HRQoL among adult COM patients w/wo cholesteatoma, measured by various disease-specific HRQoL questionnaires. Firstly, this implies that COM has a substantial influence on daily life. Secondly, this evidence substantiates the importance of HRQoL assessment in clinical practice. However, the minimal clinically important differences of the questionnaires have not been investigated yet, impeding drawing conclusions on clinical relevance. The systematic review included studies with various otologic surgical treatments and different HRQoL measurements. This diversity makes generalizability of the results to adult COM patients w/wo cholesteatoma with indication for otologic surgical treatment cautiously possible. However, it is important to bear in mind that the fair study quality, intermediate risk of bias, and overall high risk of selection bias indicate that actual outcome parameters might be less positive.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[12]/sec[1]/p[15] / 194e4f11e8eb2608d411c60e

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Recently, SH activity was shown as a gradient in the four groups of current SHG participation (n = 217), previous SHG participation (n = 118), DTL membership without SHG participation (n = 641) and no references to SHG or DTL (n = 132). The former and latter groups thus show the greatest differences and most clearly demonstrate the benefits of SHG participation [310]. When controlled logistic regressions are determined for age, gender, education, equivalised income and tinnitus distress, odds ratios of 6.94 for TW, 3.83 for knowledge of help options, and 7.75 for self-confidence in knowing more about tinnitus than most doctors are found between these two groups. The other two groups are in between with corresponding and also significant gradations. Despite all the methodological limitations of this cross-sectional study, it seems more likely that tinnitus-related knowledge and other benefits are a result of SHG participation than vice versa.

### hybrid 前三候选

1. adult-aom-inner-ear-2023 / body/sec[5]/p[4] / 5765020f3d1f25f77bd4d997

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

The latter remains to be statistically verified in further investigations.

2. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

## ENT-017 — 中耳炎研究用什么听力测量来比较治疗前后变化？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-aom-inner-ear-2023 / body/sec[2]/p[2] / 1a46d59961790ad2f68f0951

All enrolled patients were tested with pre- and post-treatment pure tone audiometry. A pure tone audiogram was obtained with 5 dB steps at frequencies of 0.125, 0.25, 0.5, 1, 2, 4 and 8 kHz for air conduction and 0.25, 0.5, 1, 2 and 4 kHz for bone conduction for all patients on both sides delivered by an Interacoustics Equinox 2.0 audiometer (InteracousticsVR, Middelfart, Denmark) in a sound-isolated booth. Pure tone averages (PTA) were set as mean threshold values in bone conduction (BC) from 0.5, 1, 2 and 4 kHz.

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-aom-inner-ear-2023 / body/sec[1]/p[3] / b5d183633ea072e6981d5326

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Unfortunately, data on standardized treatment for IED in AOM is rare and the benefit of antrotomy is not well-investigated. There is some evidence that the hearing outcome with primary treatment (steroids and antibiotics) with an additional antrotomy results in a better hearing outcome than primary therapy alone in patients with IED in otitis media with effusion and subacute mastoiditis after viral infection [14]. It may be similar in patients with IED and AOM. Hence, the aim of our study is to retrospectively analyze the hearing outcome of patients with IED in AOM, with regard to different treatment strategies such as systemic antibiotic therapy, systemic steroid therapy and myringotomy with or without antrotomy.

3. adult-aom-inner-ear-2023 / body/sec[5]/p[1] / a98fd4fa177c4c6f78ed0383

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

The hearing loss, and therefore the hearing recovery, was mainly observed in the higher frequencies, from 2 kHz onwards. The presence of vertigo was accompanied by significantly higher pretreatment hearing loss.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[5] / 8ac0c27a5aff6cd789ed3b4b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

The working group of Pantev reports on person-specific filtered music applications (with recess—notch—of the tinnitus frequency, so-called tailor-made notched music therapy). The basic idea is that peripheral hearing loss leads to a reduced lateral inhibition in the range of the affected frequency, which should result in a cortical reorganisation. This maladaptive adaptation is supposed to be reversed by listening to music with an appropriate notch filter (usually half an octave). Initial evidence for this has been reported in 39 and 24 patients with chronic tinnitus, respectively, although only one study included a control population and was pseudorandomized and double-blind [194, 195]. Changes were observed in the perceived loudness of tinnitus and/or tinnitus distress. In the study by Teismann et al. [195], changes were only reported in patients with a tinnitus frequency of ≤ 8 kHz and partly only in follow-up measurements. In a subsequent study, 32 patients were divided into three groups. Two groups received either anodal (N = 10) or cathodal (N = 11) electrostimulation in combination with TMNMT. Overall, 11 patients received TMNMT and sham stimulation. All three groups reported an improvement in THQ (p = 0.04) when comparing baseline with post-treatment. The effect was still significant 1 month after the end of treatment. There was no modulation of the effect by electrostimulation [196].

3. adult-aom-inner-ear-2023 / body/sec[2]/p[7] / 2d3e50f2f556dcec6dbdbf12

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Statistical analysis was performed with the Statistical Package for Social Sciences (SPSS, version 29.0). Paired and unpaired t-tests were used to compare pre- and post-treatment bone conduction hearing thresholds within each group and between the groups. p-values < 0.05 were considered statistically significant.

### hybrid 前三候选

1. adult-aom-inner-ear-2023 / body/sec[3]/sec[2]/p[4] / 82c4eaadd60d82b976c79041

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Firstly, the mean hearing loss was at its lowest at 0.25 kHz, with values of 10.6 dB in the conservative group, 14.4 dB in the interventional group and 19.1 dB in the operative group. Secondly, there was a highly significant (p-values < 0.001) increase in the hearing threshold from 0.25 kHz to 0.5 kHz. Thirdly, there was no statistical difference between 0.5 kHz and 1 kHz, except for in the operative group, where an additional significant (p-value < 0.05) hearing loss was observed. Fourthly, another highly significant (p-values < 0.001) increase in the hearing threshold was observed between 1 kHz and 2 kHz. Lastly, a similar hearing threshold with no significant difference was observed between 2 kHz and 4 kHz.

2. adult-com-qol-2023 / body/sec[4]/sec[2]/p[6] / bfe6f50e6a6cfb4d4fd1e0ef

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In conclusion, although technically hearing is more prominent in the COMOT-15 than in other questionnaires, clinically, it is debatable whether this is an issue. Comparison of COMOT-15 and ZCMEI-21 within the same study population showed a high Cronbach's α (>0.9) of the hearing subscale which may indicate redundancy (51). These questionnaires may thereby cover comparable facets of hearing. Likewise, the COMOT-15 mental health had a high correlation with hearing level compared to the same correlation of ZCMEI-21 (51). Hence, COMOT-15 may be best suitable for research with a focus on hearing and ZCMEI-21 or COMQ-12 may be better suitable for research with a focus on the whole symptom complex of COM and the related HRQoL.

3. adult-com-qol-2023 / body/sec[4]/sec[2]/p[5] / 609104821df5d1b8ef5653d2

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The COMOT-15 is highly focused on hearing level with 7/15 items covering this subject. The degree of hearing impairment is used as an objective measurement to indicate the success of surgical treatment. Hearing loss is known to lower QoL in general (10, 48) and hearing aids are known to increase HRQoL (49, 50). This questions whether COMOT-15 is “overweighted” by hearing-related questions or whether this focus is actually needed for this otologic population. A multinational collaborative study demonstrated that patients with a higher degree of hearing loss had a poorer HRQoL, measured with COMQ-12. Moreover, this study argued postoperative hearing improvement is a better indicator of surgical success from a patient's perspective than a dry ear (16). A positive relation between the changes in audiometric data and the measured HRQoL improvement was also demonstrated in other studies (3, 8, 22, 36). Above all, hearing loss is stated to be the dominant symptom experienced by COM patients (51). However, in another study, the degree of hearing loss was argued to not adequately reflect the experienced disease burden of COM, nor the impact of treatment (52). This is supported by the lower changes in HRQoL reported by the hearing-specific questionnaire HHIA (SMD 0.40) compared to disease-specific COMQ-12 (SMD 1.21). Nevertheless, both questionnaires indicated statistically significant HRQoL improvement (42). Furthermore, ZCMEI-21 indicated differences in HRQoL between different types of chronic middle ear diseases, including COM with and without cholesteatoma, independent of hearing level. These findings imply a considerable impact of other symptoms besides hearing loss, such as ear discharge, vertigo, and tinnitus, on HRQoL (40). In line with this, a comparison of HRQoL measure

## ENT-018 — 成人中耳炎内耳受累研究是不是随机分组试验？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-aom-inner-ear-2023 / body/sec[2]/p[1] / 81beb30770e863f1e56467d6

A retrospective, single-center data analysis at the University Hospital of Zurich was performed, including all adult patients between 2000 and 2020 that were diagnosed with AOM with IED. An IED was defined as bone conduction threshold of >15 dB in at least two frequencies between 250 and 4000 Hz with normal hearing on the not affected contralateral side and/or vestibular symptoms. Patients with suppurative labyrinthitis were excluded because of the more severe and irreversible course of the disease.

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

3. adult-com-qol-2023 / body/sec[2]/sec[2]/p[1] / 6c312fdd9b3585d2024d16ca

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Studies published until 18 May 2023 were searched using PubMed, Web of Science, Embase, and Scopus. All four databases were searched with a search string based on the eligibility criteria, without any filters or restrictions applied. The universal search string was composed of “Chronic Otitis Media” OR “Cholesteatoma” (Population), “Quality of Life” (Outcome), and “surgical intervention” (Intervention). An elaborated search string per database is given in Supplementary Table 2. Additionally, a manual search of reference lists of eligible articles was performed.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

2. adult-sore-throat-review-2024 / body/sec[2]/p[21] / 4d175a2f82cff0fe6bd126fb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

Assessment of the Risk of Bias in the Included Studies

3. adult-aom-inner-ear-2023 / body/sec[3]/sec[1]/p[2] / aa337a6d5da92c5e9d6cdd25

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

The most common symptoms stated by the patients were subjective hearing loss (112/112, 100%), otalgia (111/112, 99%), otorrhea (61/112, 54%), tinnitus (57/112, 51%) and vertigo (34/112). The mean and range of PTA value sorted by the respective symptom was as follows. Hearing loss (33.5 dB, 6.25–71.25 dB), otalgia (33.6 dB, 6.25–71.25 dB), otorrhea (33.3 dB, 6.25–71.25 dB), tinnitus (32.7 dB, 6.25–67.5 dB) and vertigo (39.5 dB, 8.75–67.5 dB). By comparison of the mean PTA of patients with or without a specific symptom, a significantly higher mean PTA (p-value: 0.003) was observed in vertigo patients. Additionally, no other symptom showed a significant decrease or increase in the PTA. Detailed demographics and symptoms according to the groups are displayed in (Table 2).

### hybrid 前三候选

1. adult-aom-inner-ear-2023 / body/sec[5]/p[4] / 5765020f3d1f25f77bd4d997

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

The latter remains to be statistically verified in further investigations.

2. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

## ENT-019 — 我慢性中耳炎复查时听力数字与自己的生活感受不一致，资料如何看待这种差异？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

adult-com-qol-2023 / body/sec[1]/sec[2]/p[1] / 7a4ded78792f8ca3e6e44fb6

Evidence about the effectiveness and safety of surgical treatment in COM has always primarily been focused on changes in objective measurements, such as complete eradication of disease, audiometric outcomes, complications and recurrence rates, and integrity of the tympanic membrane (13–15). However, these objective measures do not necessarily correspond with the patients' personal experiences. For instance, audiometric data were found to correlate with HRQoL outcomes whereas having a dry ear did not (8, 16). Patient-reported symptom appraisal together with results of objective measurements are needed to assess the results of otologic surgical treatment (17). In recent years, quality of life (QoL) has gained interest in healthcare and in the field of otolaryngology to assess the impact of disease (18) and the appreciation of surgical treatment results (17). Health-related quality of life (HRQoL) is a subset of QoL that explicitly reflects how disease influences the wellbeing of a person in the physical, mental, and social spheres of life (19). Therefore, HRQoL measurements become increasingly important as an outcome of middle ear surgery (20) as these reflect the overall impact of the disease and treatment from a patient's perspective instead of the clinician's view.

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-aom-inner-ear-2023 / body/sec[1]/p[3] / b5d183633ea072e6981d5326

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Unfortunately, data on standardized treatment for IED in AOM is rare and the benefit of antrotomy is not well-investigated. There is some evidence that the hearing outcome with primary treatment (steroids and antibiotics) with an additional antrotomy results in a better hearing outcome than primary therapy alone in patients with IED in otitis media with effusion and subacute mastoiditis after viral infection [14]. It may be similar in patients with IED and AOM. Hence, the aim of our study is to retrospectively analyze the hearing outcome of patients with IED in AOM, with regard to different treatment strategies such as systemic antibiotic therapy, systemic steroid therapy and myringotomy with or without antrotomy.

3. adult-aom-inner-ear-2023 / body/sec[5]/p[1] / a98fd4fa177c4c6f78ed0383

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

The hearing loss, and therefore the hearing recovery, was mainly observed in the higher frequencies, from 2 kHz onwards. The presence of vertigo was accompanied by significantly higher pretreatment hearing loss.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[12]/sec[1]/p[14] / 6a03541a3ce02f6923199fc8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Only recently, a study on the effect of SH was published [310]. At the time of the survey, 800 of the 13,000 members of the non-profit SH organisation Deutsche Tinnitus-Liga (DTL) were active in SH groups. In a cross-sectional study, the tinnitus distress (Mini-TQ; [64]) was assessed in 1108 affected persons (mean 61 years, 60% men) using valid items of the Structured Tinnitus Interview (STI; [310]) on tinnitus knowledge (TK), tinnitus coping and quality of life (QoL; WHOQOL-BREF 1998). As a result, the regression analyses show highly significant correlations of community SH activity with TK, coping as well as health system orientation and self-confidence, but no significant differences concerning general QoL.

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

3. adult-com-qol-2023 / body/sec[4]/sec[1]/p[1] / 10b359637ad9836ae411bfb9

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The aim of this systematic review was to investigate the impact of otologic surgical treatment on the health-related quality of life of chronic otitis media patients with or without cholesteatoma. In total, 16 studies were considered eligible and were included in this review. All studies reported a statistically significant HRQoL improvement after otologic surgical treatment compared to before measured with various disease-specific HRQoL questionnaires. Contrarily, studies that used general QoL questionnaires SF-36 (8, 31, 43) and EQ-5D VAS (42) reported no statistically significant improvement after surgical treatment, even when the specific and general QoL questionnaires were administered simultaneously within the same study population. General QoL measurement instruments insufficiently cover disease-specific symptoms or other features that may affect daily life (8, 31, 45) and generic instruments are not responsive to detect changes caused by effective treatment (46). Nonetheless, general QoL tools are important to measure the impact of various diseases on the general QoL and thereby make standardized comparisons possible between different diseases or healthy and diseased populations (8). Disease-specific questionnaires are preferable to investigate the effect of otologic surgical treatment on specific otologic symptoms.

### hybrid 前三候选

1. adult-com-qol-2023 / body/sec[4]/sec[2]/p[5] / 609104821df5d1b8ef5653d2

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The COMOT-15 is highly focused on hearing level with 7/15 items covering this subject. The degree of hearing impairment is used as an objective measurement to indicate the success of surgical treatment. Hearing loss is known to lower QoL in general (10, 48) and hearing aids are known to increase HRQoL (49, 50). This questions whether COMOT-15 is “overweighted” by hearing-related questions or whether this focus is actually needed for this otologic population. A multinational collaborative study demonstrated that patients with a higher degree of hearing loss had a poorer HRQoL, measured with COMQ-12. Moreover, this study argued postoperative hearing improvement is a better indicator of surgical success from a patient's perspective than a dry ear (16). A positive relation between the changes in audiometric data and the measured HRQoL improvement was also demonstrated in other studies (3, 8, 22, 36). Above all, hearing loss is stated to be the dominant symptom experienced by COM patients (51). However, in another study, the degree of hearing loss was argued to not adequately reflect the experienced disease burden of COM, nor the impact of treatment (52). This is supported by the lower changes in HRQoL reported by the hearing-specific questionnaire HHIA (SMD 0.40) compared to disease-specific COMQ-12 (SMD 1.21). Nevertheless, both questionnaires indicated statistically significant HRQoL improvement (42). Furthermore, ZCMEI-21 indicated differences in HRQoL between different types of chronic middle ear diseases, including COM with and without cholesteatoma, independent of hearing level. These findings imply a considerable impact of other symptoms besides hearing loss, such as ear discharge, vertigo, and tinnitus, on HRQoL (40). In line with this, a comparison of HRQoL measure

2. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[12]/sec[1]/p[14] / 6a03541a3ce02f6923199fc8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Only recently, a study on the effect of SH was published [310]. At the time of the survey, 800 of the 13,000 members of the non-profit SH organisation Deutsche Tinnitus-Liga (DTL) were active in SH groups. In a cross-sectional study, the tinnitus distress (Mini-TQ; [64]) was assessed in 1108 affected persons (mean 61 years, 60% men) using valid items of the Structured Tinnitus Interview (STI; [310]) on tinnitus knowledge (TK), tinnitus coping and quality of life (QoL; WHOQOL-BREF 1998). As a result, the regression analyses show highly significant correlations of community SH activity with TK, coping as well as health system orientation and self-confidence, but no significant differences concerning general QoL.

## ENT-020 — 成人慢性中耳炎研究用了哪些生活质量问卷？

标记：anchor_hit_control；原锚点排名：{'keyword': 2, 'vector': 5, 'hybrid': 1}

原锚点：

adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

3. adult-com-qol-2023 / body/sec[2]/sec[2]/p[1] / 6c312fdd9b3585d2024d16ca

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Studies published until 18 May 2023 were searched using PubMed, Web of Science, Embase, and Scopus. All four databases were searched with a search string based on the eligibility criteria, without any filters or restrictions applied. The universal search string was composed of “Chronic Otitis Media” OR “Cholesteatoma” (Population), “Quality of Life” (Outcome), and “surgical intervention” (Intervention). An elaborated search string per database is given in Supplementary Table 2. Additionally, a manual search of reference lists of eligible articles was performed.

### vector 前三候选

1. adult-com-qol-2023 / body/sec[3]/sec[2]/p[1] / 8dfb8262e3c4d9ae8a776deb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Table 1 represents a detailed overview of the relevant characteristics of the included studies. The studies are clustered based on the HRQoL questionnaire used. All studies were prospective observational studies with pre- and postoperative measurements, published between 2000 and 2023. Information about HRQoL scores before and after otologic surgical treatment was gathered with the use of seven different validated HRQoL questionnaires. The sample sizes per study ranged between 26 (44) and 167 (43) patients, resulting in a total of 1,329 included patients with a mean age of 44.74 years. HRQoL assessment was conducted with at least one disease-specific HRQoL questionnaire in each study. One questionnaire for general chronic middle ear diseases (CES) was used and three COM-specific questionnaires (COMQ-12, ZCMEI-21, and COMOT-15). CES (3, 35–38) and COMOT-15 (8, 31–34) were used in five different studies, and the ZCMEI-21 (31, 39, 40) and COMQ-12 (42–44) in three studies. Furthermore, three general HRQoL questionnaires were used: SF-36 (8, 31, 43), SF-12V2 (38), and Euro-Qol-5D-5L (42). A hearing-specific QoL questionnaire (HHIA) was used once (42). Table 2 provides an overview of the content of each disease-specific HRQoL questionnaire. All questionnaires contain questions on classic ear symptoms, use of medical resources, and impact on daily life activities, except for COMOT-15 which does not encompass the latter. COMOT-15, COMQ-12, and ZCMEI-21 include psychological aspects as well. However, besides covering different domains of HRQoL, each questionnaire has its own interpretation of these domains.

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[12]/sec[1]/p[14] / 6a03541a3ce02f6923199fc8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Only recently, a study on the effect of SH was published [310]. At the time of the survey, 800 of the 13,000 members of the non-profit SH organisation Deutsche Tinnitus-Liga (DTL) were active in SH groups. In a cross-sectional study, the tinnitus distress (Mini-TQ; [64]) was assessed in 1108 affected persons (mean 61 years, 60% men) using valid items of the Structured Tinnitus Interview (STI; [310]) on tinnitus knowledge (TK), tinnitus coping and quality of life (QoL; WHOQOL-BREF 1998). As a result, the regression analyses show highly significant correlations of community SH activity with TK, coping as well as health system orientation and self-confidence, but no significant differences concerning general QoL.

3. adult-com-qol-2023 / body/sec[4]/sec[1]/p[1] / 10b359637ad9836ae411bfb9

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The aim of this systematic review was to investigate the impact of otologic surgical treatment on the health-related quality of life of chronic otitis media patients with or without cholesteatoma. In total, 16 studies were considered eligible and were included in this review. All studies reported a statistically significant HRQoL improvement after otologic surgical treatment compared to before measured with various disease-specific HRQoL questionnaires. Contrarily, studies that used general QoL questionnaires SF-36 (8, 31, 43) and EQ-5D VAS (42) reported no statistically significant improvement after surgical treatment, even when the specific and general QoL questionnaires were administered simultaneously within the same study population. General QoL measurement instruments insufficiently cover disease-specific symptoms or other features that may affect daily life (8, 31, 45) and generic instruments are not responsive to detect changes caused by effective treatment (46). Nonetheless, general QoL tools are important to measure the impact of various diseases on the general QoL and thereby make standardized comparisons possible between different diseases or healthy and diseased populations (8). Disease-specific questionnaires are preferable to investigate the effect of otologic surgical treatment on specific otologic symptoms.

### hybrid 前三候选

1. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

2. adult-com-qol-2023 / body/sec[4]/sec[1]/p[1] / 10b359637ad9836ae411bfb9

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The aim of this systematic review was to investigate the impact of otologic surgical treatment on the health-related quality of life of chronic otitis media patients with or without cholesteatoma. In total, 16 studies were considered eligible and were included in this review. All studies reported a statistically significant HRQoL improvement after otologic surgical treatment compared to before measured with various disease-specific HRQoL questionnaires. Contrarily, studies that used general QoL questionnaires SF-36 (8, 31, 43) and EQ-5D VAS (42) reported no statistically significant improvement after surgical treatment, even when the specific and general QoL questionnaires were administered simultaneously within the same study population. General QoL measurement instruments insufficiently cover disease-specific symptoms or other features that may affect daily life (8, 31, 45) and generic instruments are not responsive to detect changes caused by effective treatment (46). Nonetheless, general QoL tools are important to measure the impact of various diseases on the general QoL and thereby make standardized comparisons possible between different diseases or healthy and diseased populations (8). Disease-specific questionnaires are preferable to investigate the effect of otologic surgical treatment on specific otologic symptoms.

3. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

## ENT-021 — 这份慢性中耳炎生活质量系统综述能直接用于儿童或未手术成人吗？

标记：hybrid_missed_anchor, hybrid_lost_single_strategy_hit；原锚点排名：{'keyword': 8, 'vector': None, 'hybrid': None}

原锚点：

adult-com-qol-2023 / body/sec[2]/sec[1]/p[1] / bc16c1013b82dc0186502a7c

The elaborated eligibility criteria can be found in Supplementary Table 1. All original studies with a prospective design written in English or Dutch were included. Conference abstracts, letters, reviews, editorials, and translation and validation studies of questionnaires were excluded. Only studies with adult (≥18 years) patients suffering from chronic otitis media with or without cholesteatoma who underwent otologic surgical treatment were included. As stated in the introduction, various terms to subdivide COM are used in literature. We decided to include all these terms and therefore this systematic review included a heterogenous group of COM patients. To simply refer to this total population, we used the umbrella term COM with or without (w/wo) cholesteatoma throughout this review.

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

3. adult-com-qol-2023 / body/sec[2]/sec[2]/p[1] / 6c312fdd9b3585d2024d16ca

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Studies published until 18 May 2023 were searched using PubMed, Web of Science, Embase, and Scopus. All four databases were searched with a search string based on the eligibility criteria, without any filters or restrictions applied. The universal search string was composed of “Chronic Otitis Media” OR “Cholesteatoma” (Population), “Quality of Life” (Outcome), and “surgical intervention” (Intervention). An elaborated search string per database is given in Supplementary Table 2. Additionally, a manual search of reference lists of eligible articles was performed.

### vector 前三候选

1. adult-com-qol-2023 / body/sec[3]/sec[2]/p[1] / 8dfb8262e3c4d9ae8a776deb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Table 1 represents a detailed overview of the relevant characteristics of the included studies. The studies are clustered based on the HRQoL questionnaire used. All studies were prospective observational studies with pre- and postoperative measurements, published between 2000 and 2023. Information about HRQoL scores before and after otologic surgical treatment was gathered with the use of seven different validated HRQoL questionnaires. The sample sizes per study ranged between 26 (44) and 167 (43) patients, resulting in a total of 1,329 included patients with a mean age of 44.74 years. HRQoL assessment was conducted with at least one disease-specific HRQoL questionnaire in each study. One questionnaire for general chronic middle ear diseases (CES) was used and three COM-specific questionnaires (COMQ-12, ZCMEI-21, and COMOT-15). CES (3, 35–38) and COMOT-15 (8, 31–34) were used in five different studies, and the ZCMEI-21 (31, 39, 40) and COMQ-12 (42–44) in three studies. Furthermore, three general HRQoL questionnaires were used: SF-36 (8, 31, 43), SF-12V2 (38), and Euro-Qol-5D-5L (42). A hearing-specific QoL questionnaire (HHIA) was used once (42). Table 2 provides an overview of the content of each disease-specific HRQoL questionnaire. All questionnaires contain questions on classic ear symptoms, use of medical resources, and impact on daily life activities, except for COMOT-15 which does not encompass the latter. COMOT-15, COMQ-12, and ZCMEI-21 include psychological aspects as well. However, besides covering different domains of HRQoL, each questionnaire has its own interpretation of these domains.

2. adult-com-qol-2023 / body/sec[4]/sec[1]/p[1] / 10b359637ad9836ae411bfb9

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The aim of this systematic review was to investigate the impact of otologic surgical treatment on the health-related quality of life of chronic otitis media patients with or without cholesteatoma. In total, 16 studies were considered eligible and were included in this review. All studies reported a statistically significant HRQoL improvement after otologic surgical treatment compared to before measured with various disease-specific HRQoL questionnaires. Contrarily, studies that used general QoL questionnaires SF-36 (8, 31, 43) and EQ-5D VAS (42) reported no statistically significant improvement after surgical treatment, even when the specific and general QoL questionnaires were administered simultaneously within the same study population. General QoL measurement instruments insufficiently cover disease-specific symptoms or other features that may affect daily life (8, 31, 45) and generic instruments are not responsive to detect changes caused by effective treatment (46). Nonetheless, general QoL tools are important to measure the impact of various diseases on the general QoL and thereby make standardized comparisons possible between different diseases or healthy and diseased populations (8). Disease-specific questionnaires are preferable to investigate the effect of otologic surgical treatment on specific otologic symptoms.

3. adult-com-qol-2023 / body/sec[5]/p[1] / 278b0cfa3352da2986cf0def

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In conclusion, this systematic review provides an overview of the evidence that otologic surgical treatment positively impacts HRQoL among adult COM patients w/wo cholesteatoma, measured by various disease-specific HRQoL questionnaires. Firstly, this implies that COM has a substantial influence on daily life. Secondly, this evidence substantiates the importance of HRQoL assessment in clinical practice. However, the minimal clinically important differences of the questionnaires have not been investigated yet, impeding drawing conclusions on clinical relevance. The systematic review included studies with various otologic surgical treatments and different HRQoL measurements. This diversity makes generalizability of the results to adult COM patients w/wo cholesteatoma with indication for otologic surgical treatment cautiously possible. However, it is important to bear in mind that the fair study quality, intermediate risk of bias, and overall high risk of selection bias indicate that actual outcome parameters might be less positive.

### hybrid 前三候选

1. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

2. adult-com-qol-2023 / body/sec[4]/sec[1]/p[1] / 10b359637ad9836ae411bfb9

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The aim of this systematic review was to investigate the impact of otologic surgical treatment on the health-related quality of life of chronic otitis media patients with or without cholesteatoma. In total, 16 studies were considered eligible and were included in this review. All studies reported a statistically significant HRQoL improvement after otologic surgical treatment compared to before measured with various disease-specific HRQoL questionnaires. Contrarily, studies that used general QoL questionnaires SF-36 (8, 31, 43) and EQ-5D VAS (42) reported no statistically significant improvement after surgical treatment, even when the specific and general QoL questionnaires were administered simultaneously within the same study population. General QoL measurement instruments insufficiently cover disease-specific symptoms or other features that may affect daily life (8, 31, 45) and generic instruments are not responsive to detect changes caused by effective treatment (46). Nonetheless, general QoL tools are important to measure the impact of various diseases on the general QoL and thereby make standardized comparisons possible between different diseases or healthy and diseased populations (8). Disease-specific questionnaires are preferable to investigate the effect of otologic surgical treatment on specific otologic symptoms.

3. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

## ENT-022 — 我68岁，听力这些年慢慢下降，资料怎样描述年龄相关听力损失？

标记：hybrid_missed_anchor, hybrid_lost_single_strategy_hit；原锚点排名：{'keyword': 6, 'vector': None, 'hybrid': None}

原锚点：

nidcd-presbycusis / main/block[1] / 23016a42e1f434dbe7b202f5

Age-related hearing loss (also called presbycusis, pronounced prez-buh-KYOO-sis) is hearing loss that occurs gradually for many of us as we grow older. It is one of the most common conditions affecting adults as we age. Approximately 15% of American adults (37.5 million) ages 18 and over report some trouble hearing, and about one in three people in the U.S. between the ages of 65 and 74 has hearing loss. Nearly half of those older than 75 have difficulty hearing.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[6] / 61d8c80cb5ed39d0375201d1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Treatment of acute tinnitus follows the treatment recommendations for acute sudden hearing loss. For the treatment of acute hearing loss, corresponding guidelines (AWMF 017/2914 currently being updated [82]; guideline USA [83]) recommend systemic or intratympanic steroid treatment with, however, moderate evidence. Therefore, acute tinnitus with hearing loss or following hearing loss should be treated appropriately. If the tinnitus occurs acutely without measurable hearing loss, the standard cortisone therapy recommended for hearing loss is not recommended.

2. nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

来源：https://www.nidcd.nih.gov/health/tinnitus

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

3. nidcd-presbycusis / main/block[22] / b5eb56631abed6dbef52edd6

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

An audiologist (pronounced aw-dee-AH-luh-jist) has specialized training in identifying and measuring hearing loss, determining where along the auditory pathway there may be a problem with hearing, and recommending and providing certain hearing loss interventions, such as hearing aids.

### vector 前三候选

1. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

2. nidcd-presbycusis / main/block[4] / 1c8edca00f2a9ca8c8e254df

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Many things affect our hearing as we age. For example, changes in the inner ear that can affect hearing are common. Age-related changes in the middle ear and complex changes along the nerve pathways from the ear to the brain can also affect hearing. Long-term exposure to noise and some medical conditions can also play a role. In addition, new research suggests that certain genes make some people more susceptible to hearing loss as they age.

3. nidcd-presbycusis / main/block[14] / cea4a187bf18ea0daaacb29d

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel that any difficulty with your hearing limits or hampers your personal or social life?

### hybrid 前三候选

1. nidcd-presbycusis / main/block[33] / d30f5a4b0f87d2dafaad6ee8

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

NIDCD supports research on the causes of age-related hearing loss, including genes that may make this type of hearing loss more likely. NIDCD-funded scientists are working to understand what happens as we age that interferes with our ability to hear speech in a noisy environment. NIDCD also funds research that explores changes in how the brain processes sound when we lose our hearing. The research to date supports the use of hearing aids to maintain the brain’s sound-processing capabilities.

2. nidcd-presbycusis / main/block[28] / b7f118bf36dc44578001f447

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Tell your friends and family about your hearing loss. Explain which listening situations are hard for you.

3. nidcd-presbycusis / main/block[5] / 618d317ee5c70c61c9ef73c2

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Conditions that are more common in older people, such as high blood pressure and diabetes, are associated with hearing loss. In addition, medications that are toxic to the sensory cells in your ears (some chemotherapy drugs, for example) can cause hearing loss. Less commonly, abnormalities of the middle ear, such as otosclerosis, can worsen hearing with age.

## ENT-023 — 老年性听力变化通常涉及一侧还是两侧？

标记：hybrid_missed_anchor, hybrid_lost_single_strategy_hit；原锚点排名：{'keyword': None, 'vector': 8, 'hybrid': None}

原锚点：

nidcd-presbycusis / main/block[3] / 98f239a7d95e330b43d4a2f6

Hearing loss typically occurs in both ears as we age. Because the loss is gradual, you may not realize that you've lost some of your ability to hear.

### keyword 前三候选

1. nidcd-presbycusis / main/block[24] / cecceef4a0828e4a1a8e6aa8

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Hearing aids are electronic instruments you wear in or behind your ear. They make sounds louder. For mild to moderate hearing loss, a new category of hearing aids for adults was established in 2022 by the U.S. Food and Drug Administration. These devices may be purchased over the counter (OTC) from retail or online outlets without seeing a health care professional or getting a hearing test. If you have tried an OTC hearing aid without success or have trouble hearing loud sounds, consult a hearing health professional, because your hearing loss may be more severe.

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[2]/sec[1]/p[9] / c5359609e7b57507a55582b0

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

If hearing aids are fitted, this is generally done according to the applicable national hearing aid guidelines. In individual cases of isolated high-frequency hearing loss and high-frequency tinnitus, a hearing aid fitting can be useful even without the presence of hearing loss corresponding to these guidelines [94, 100–103].

3. nidcd-presbycusis / main/block[22] / b5eb56631abed6dbef52edd6

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

An audiologist (pronounced aw-dee-AH-luh-jist) has specialized training in identifying and measuring hearing loss, determining where along the auditory pathway there may be a problem with hearing, and recommending and providing certain hearing loss interventions, such as hearing aids.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[1]/p[5] / 2d8582982a469dc23fd9c863

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These changes reflect neuroplastic processes that are thought to be triggered by auditory deprivation. Similar to phantom limb pain, there is thought to be increased excitation, plasticity and connectivity along the entire central auditory pathway—as a compensatory response to reduced sensory input [18–21]. However, it has also been shown that abnormal activity can be found in somatosensory afferents [22]. Furthermore, patients with chronic tinnitus show functional changes not only in auditory structures but also in limbic, parietal and frontal areas [23–25]. The functional connectivity between auditory and non-auditory areas appears to be increased in tinnitus patients [26–31]. These tinnitus-associated structural and functional changes in neuronal networks are not static but change with increasing duration of tinnitus [26, 32, 33]. They are also significantly influenced by attentional redirection as tinnitus accentuation [34].

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[1]/p[1] / 8270973feab83f126ef0c2cb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

In which ear do you hear your tinnitus (right, left, both sides, head)?

3. nidcd-presbycusis / main/block[4] / 1c8edca00f2a9ca8c8e254df

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Many things affect our hearing as we age. For example, changes in the inner ear that can affect hearing are common. Age-related changes in the middle ear and complex changes along the nerve pathways from the ear to the brain can also affect hearing. Long-term exposure to noise and some medical conditions can also play a role. In addition, new research suggests that certain genes make some people more susceptible to hearing loss as they age.

### hybrid 前三候选

1. nidcd-presbycusis / main/block[4] / 1c8edca00f2a9ca8c8e254df

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Many things affect our hearing as we age. For example, changes in the inner ear that can affect hearing are common. Age-related changes in the middle ear and complex changes along the nerve pathways from the ear to the brain can also affect hearing. Long-term exposure to noise and some medical conditions can also play a role. In addition, new research suggests that certain genes make some people more susceptible to hearing loss as they age.

2. nidcd-presbycusis / main/block[24] / cecceef4a0828e4a1a8e6aa8

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Hearing aids are electronic instruments you wear in or behind your ear. They make sounds louder. For mild to moderate hearing loss, a new category of hearing aids for adults was established in 2022 by the U.S. Food and Drug Administration. These devices may be purchased over the counter (OTC) from retail or online outlets without seeing a health care professional or getting a hearing test. If you have tried an OTC hearing aid without success or have trouble hearing loud sounds, consult a hearing health professional, because your hearing loss may be more severe.

3. tinnitus-s3-2022 / body/sec[5]/sec[1]/p[5] / 2d8582982a469dc23fd9c863

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These changes reflect neuroplastic processes that are thought to be triggered by auditory deprivation. Similar to phantom limb pain, there is thought to be increased excitation, plasticity and connectivity along the entire central auditory pathway—as a compensatory response to reduced sensory input [18–21]. However, it has also been shown that abnormal activity can be found in somatosensory afferents [22]. Furthermore, patients with chronic tinnitus show functional changes not only in auditory structures but also in limbic, parietal and frontal areas [23–25]. The functional connectivity between auditory and non-auditory areas appears to be increased in tinnitus patients [26–31]. These tinnitus-associated structural and functional changes in neuronal networks are not static but change with increasing duration of tinnitus [26, 32, 33]. They are also significantly influenced by attentional redirection as tinnitus accentuation [34].

## ENT-024 — 我年纪大后听不清门铃和医生的话，资料提到哪些日常影响？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 2, 'hybrid': 2}

原锚点：

nidcd-presbycusis / main/block[2] / 438ca1da81ae83daf0137a57

Having trouble hearing can make it hard to understand and follow a doctor's advice, respond to warnings, and hear phones, doorbells, and smoke alarms. Hearing loss can also make it hard to enjoy talking with family and friends, leading to feelings of isolation.

### keyword 前三候选

### vector 前三候选

1. nidcd-presbycusis / main/block[6] / 261c131f8ca1dc401361909a

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Scientists don't yet know how to prevent age-related hearing loss, but you can protect yourself from noise-induced hearing loss. Potential sources of damaging noises include loud music, headphones/earbuds used at high volume, construction equipment, fireworks, guns, lawn mowers, leaf blowers, and motorcycles. To help safeguard your hearing as you age, avoid loud noises, reduce the amount of time you're exposed to loud sounds, and protect your ears with earplugs or protective earmuffs.

2. nidcd-presbycusis / main/block[2] / 438ca1da81ae83daf0137a57

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Having trouble hearing can make it hard to understand and follow a doctor's advice, respond to warnings, and hear phones, doorbells, and smoke alarms. Hearing loss can also make it hard to enjoy talking with family and friends, leading to feelings of isolation.

3. adult-com-qol-2023 / body/sec[3]/sec[2]/p[1] / 8dfb8262e3c4d9ae8a776deb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Table 1 represents a detailed overview of the relevant characteristics of the included studies. The studies are clustered based on the HRQoL questionnaire used. All studies were prospective observational studies with pre- and postoperative measurements, published between 2000 and 2023. Information about HRQoL scores before and after otologic surgical treatment was gathered with the use of seven different validated HRQoL questionnaires. The sample sizes per study ranged between 26 (44) and 167 (43) patients, resulting in a total of 1,329 included patients with a mean age of 44.74 years. HRQoL assessment was conducted with at least one disease-specific HRQoL questionnaire in each study. One questionnaire for general chronic middle ear diseases (CES) was used and three COM-specific questionnaires (COMQ-12, ZCMEI-21, and COMOT-15). CES (3, 35–38) and COMOT-15 (8, 31–34) were used in five different studies, and the ZCMEI-21 (31, 39, 40) and COMQ-12 (42–44) in three studies. Furthermore, three general HRQoL questionnaires were used: SF-36 (8, 31, 43), SF-12V2 (38), and Euro-Qol-5D-5L (42). A hearing-specific QoL questionnaire (HHIA) was used once (42). Table 2 provides an overview of the content of each disease-specific HRQoL questionnaire. All questionnaires contain questions on classic ear symptoms, use of medical resources, and impact on daily life activities, except for COMOT-15 which does not encompass the latter. COMOT-15, COMQ-12, and ZCMEI-21 include psychological aspects as well. However, besides covering different domains of HRQoL, each questionnaire has its own interpretation of these domains.

### hybrid 前三候选

1. nidcd-presbycusis / main/block[6] / 261c131f8ca1dc401361909a

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Scientists don't yet know how to prevent age-related hearing loss, but you can protect yourself from noise-induced hearing loss. Potential sources of damaging noises include loud music, headphones/earbuds used at high volume, construction equipment, fireworks, guns, lawn mowers, leaf blowers, and motorcycles. To help safeguard your hearing as you age, avoid loud noises, reduce the amount of time you're exposed to loud sounds, and protect your ears with earplugs or protective earmuffs.

2. nidcd-presbycusis / main/block[2] / 438ca1da81ae83daf0137a57

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Having trouble hearing can make it hard to understand and follow a doctor's advice, respond to warnings, and hear phones, doorbells, and smoke alarms. Hearing loss can also make it hard to enjoy talking with family and friends, leading to feelings of isolation.

3. adult-com-qol-2023 / body/sec[3]/sec[2]/p[1] / 8dfb8262e3c4d9ae8a776deb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Table 1 represents a detailed overview of the relevant characteristics of the included studies. The studies are clustered based on the HRQoL questionnaire used. All studies were prospective observational studies with pre- and postoperative measurements, published between 2000 and 2023. Information about HRQoL scores before and after otologic surgical treatment was gathered with the use of seven different validated HRQoL questionnaires. The sample sizes per study ranged between 26 (44) and 167 (43) patients, resulting in a total of 1,329 included patients with a mean age of 44.74 years. HRQoL assessment was conducted with at least one disease-specific HRQoL questionnaire in each study. One questionnaire for general chronic middle ear diseases (CES) was used and three COM-specific questionnaires (COMQ-12, ZCMEI-21, and COMOT-15). CES (3, 35–38) and COMOT-15 (8, 31–34) were used in five different studies, and the ZCMEI-21 (31, 39, 40) and COMQ-12 (42–44) in three studies. Furthermore, three general HRQoL questionnaires were used: SF-36 (8, 31, 43), SF-12V2 (38), and Euro-Qol-5D-5L (42). A hearing-specific QoL questionnaire (HHIA) was used once (42). Table 2 provides an overview of the content of each disease-specific HRQoL questionnaire. All questionnaires contain questions on classic ear symptoms, use of medical resources, and impact on daily life activities, except for COMOT-15 which does not encompass the latter. COMOT-15, COMQ-12, and ZCMEI-21 include psychological aspects as well. However, besides covering different domains of HRQoL, each questionnaire has its own interpretation of these domains.

## ENT-025 — 我退休前长期处在嘈杂环境，年龄相关听力下降是否只有衰老这一个因素？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 1, 'hybrid': 6}

原锚点：

nidcd-presbycusis / main/block[4] / 1c8edca00f2a9ca8c8e254df

Many things affect our hearing as we age. For example, changes in the inner ear that can affect hearing are common. Age-related changes in the middle ear and complex changes along the nerve pathways from the ear to the brain can also affect hearing. Long-term exposure to noise and some medical conditions can also play a role. In addition, new research suggests that certain genes make some people more susceptible to hearing loss as they age.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[6] / 61d8c80cb5ed39d0375201d1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Treatment of acute tinnitus follows the treatment recommendations for acute sudden hearing loss. For the treatment of acute hearing loss, corresponding guidelines (AWMF 017/2914 currently being updated [82]; guideline USA [83]) recommend systemic or intratympanic steroid treatment with, however, moderate evidence. Therefore, acute tinnitus with hearing loss or following hearing loss should be treated appropriately. If the tinnitus occurs acutely without measurable hearing loss, the standard cortisone therapy recommended for hearing loss is not recommended.

2. nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

来源：https://www.nidcd.nih.gov/health/tinnitus

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

3. nidcd-presbycusis / main/block[22] / b5eb56631abed6dbef52edd6

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

An audiologist (pronounced aw-dee-AH-luh-jist) has specialized training in identifying and measuring hearing loss, determining where along the auditory pathway there may be a problem with hearing, and recommending and providing certain hearing loss interventions, such as hearing aids.

### vector 前三候选

1. nidcd-presbycusis / main/block[4] / 1c8edca00f2a9ca8c8e254df

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Many things affect our hearing as we age. For example, changes in the inner ear that can affect hearing are common. Age-related changes in the middle ear and complex changes along the nerve pathways from the ear to the brain can also affect hearing. Long-term exposure to noise and some medical conditions can also play a role. In addition, new research suggests that certain genes make some people more susceptible to hearing loss as they age.

2. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

3. nidcd-presbycusis / main/block[6] / 261c131f8ca1dc401361909a

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Scientists don't yet know how to prevent age-related hearing loss, but you can protect yourself from noise-induced hearing loss. Potential sources of damaging noises include loud music, headphones/earbuds used at high volume, construction equipment, fireworks, guns, lawn mowers, leaf blowers, and motorcycles. To help safeguard your hearing as you age, avoid loud noises, reduce the amount of time you're exposed to loud sounds, and protect your ears with earplugs or protective earmuffs.

### hybrid 前三候选

1. nidcd-presbycusis / main/block[5] / 618d317ee5c70c61c9ef73c2

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Conditions that are more common in older people, such as high blood pressure and diabetes, are associated with hearing loss. In addition, medications that are toxic to the sensory cells in your ears (some chemotherapy drugs, for example) can cause hearing loss. Less commonly, abnormalities of the middle ear, such as otosclerosis, can worsen hearing with age.

2. nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

来源：https://www.nidcd.nih.gov/health/tinnitus

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

3. nidcd-presbycusis / main/block[6] / 261c131f8ca1dc401361909a

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Scientists don't yet know how to prevent age-related hearing loss, but you can protect yourself from noise-induced hearing loss. Potential sources of damaging noises include loud music, headphones/earbuds used at high volume, construction equipment, fireworks, guns, lawn mowers, leaf blowers, and motorcycles. To help safeguard your hearing as you age, avoid loud noises, reduce the amount of time you're exposed to loud sounds, and protect your ears with earplugs or protective earmuffs.

## ENT-026 — 我有糖尿病和听力下降，科普资料是否描述过两者的关联？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-presbycusis / main/block[5] / 618d317ee5c70c61c9ef73c2

Conditions that are more common in older people, such as high blood pressure and diabetes, are associated with hearing loss. In addition, medications that are toxic to the sensory cells in your ears (some chemotherapy drugs, for example) can cause hearing loss. Less commonly, abnormalities of the middle ear, such as otosclerosis, can worsen hearing with age.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[6] / 61d8c80cb5ed39d0375201d1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Treatment of acute tinnitus follows the treatment recommendations for acute sudden hearing loss. For the treatment of acute hearing loss, corresponding guidelines (AWMF 017/2914 currently being updated [82]; guideline USA [83]) recommend systemic or intratympanic steroid treatment with, however, moderate evidence. Therefore, acute tinnitus with hearing loss or following hearing loss should be treated appropriately. If the tinnitus occurs acutely without measurable hearing loss, the standard cortisone therapy recommended for hearing loss is not recommended.

2. nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

来源：https://www.nidcd.nih.gov/health/tinnitus

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

3. nidcd-presbycusis / main/block[22] / b5eb56631abed6dbef52edd6

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

An audiologist (pronounced aw-dee-AH-luh-jist) has specialized training in identifying and measuring hearing loss, determining where along the auditory pathway there may be a problem with hearing, and recommending and providing certain hearing loss interventions, such as hearing aids.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

2. adult-com-qol-2023 / body/sec[4]/sec[2]/p[5] / 609104821df5d1b8ef5653d2

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The COMOT-15 is highly focused on hearing level with 7/15 items covering this subject. The degree of hearing impairment is used as an objective measurement to indicate the success of surgical treatment. Hearing loss is known to lower QoL in general (10, 48) and hearing aids are known to increase HRQoL (49, 50). This questions whether COMOT-15 is “overweighted” by hearing-related questions or whether this focus is actually needed for this otologic population. A multinational collaborative study demonstrated that patients with a higher degree of hearing loss had a poorer HRQoL, measured with COMQ-12. Moreover, this study argued postoperative hearing improvement is a better indicator of surgical success from a patient's perspective than a dry ear (16). A positive relation between the changes in audiometric data and the measured HRQoL improvement was also demonstrated in other studies (3, 8, 22, 36). Above all, hearing loss is stated to be the dominant symptom experienced by COM patients (51). However, in another study, the degree of hearing loss was argued to not adequately reflect the experienced disease burden of COM, nor the impact of treatment (52). This is supported by the lower changes in HRQoL reported by the hearing-specific questionnaire HHIA (SMD 0.40) compared to disease-specific COMQ-12 (SMD 1.21). Nevertheless, both questionnaires indicated statistically significant HRQoL improvement (42). Furthermore, ZCMEI-21 indicated differences in HRQoL between different types of chronic middle ear diseases, including COM with and without cholesteatoma, independent of hearing level. These findings imply a considerable impact of other symptoms besides hearing loss, such as ear discharge, vertigo, and tinnitus, on HRQoL (40). In line with this, a comparison of HRQoL measure

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[6] / 61d8c80cb5ed39d0375201d1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Treatment of acute tinnitus follows the treatment recommendations for acute sudden hearing loss. For the treatment of acute hearing loss, corresponding guidelines (AWMF 017/2914 currently being updated [82]; guideline USA [83]) recommend systemic or intratympanic steroid treatment with, however, moderate evidence. Therefore, acute tinnitus with hearing loss or following hearing loss should be treated appropriately. If the tinnitus occurs acutely without measurable hearing loss, the standard cortisone therapy recommended for hearing loss is not recommended.

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

3. adult-com-qol-2023 / body/sec[4]/sec[2]/p[5] / 609104821df5d1b8ef5653d2

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The COMOT-15 is highly focused on hearing level with 7/15 items covering this subject. The degree of hearing impairment is used as an objective measurement to indicate the success of surgical treatment. Hearing loss is known to lower QoL in general (10, 48) and hearing aids are known to increase HRQoL (49, 50). This questions whether COMOT-15 is “overweighted” by hearing-related questions or whether this focus is actually needed for this otologic population. A multinational collaborative study demonstrated that patients with a higher degree of hearing loss had a poorer HRQoL, measured with COMQ-12. Moreover, this study argued postoperative hearing improvement is a better indicator of surgical success from a patient's perspective than a dry ear (16). A positive relation between the changes in audiometric data and the measured HRQoL improvement was also demonstrated in other studies (3, 8, 22, 36). Above all, hearing loss is stated to be the dominant symptom experienced by COM patients (51). However, in another study, the degree of hearing loss was argued to not adequately reflect the experienced disease burden of COM, nor the impact of treatment (52). This is supported by the lower changes in HRQoL reported by the hearing-specific questionnaire HHIA (SMD 0.40) compared to disease-specific COMQ-12 (SMD 1.21). Nevertheless, both questionnaires indicated statistically significant HRQoL improvement (42). Furthermore, ZCMEI-21 indicated differences in HRQoL between different types of chronic middle ear diseases, including COM with and without cholesteatoma, independent of hearing level. These findings imply a considerable impact of other symptoms besides hearing loss, such as ear discharge, vertigo, and tinnitus, on HRQoL (40). In line with this, a comparison of HRQoL measure

## ENT-027 — 哪些生活中的高音量环境在听力保护资料中被列为噪声来源？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 2, 'hybrid': 5}

原锚点：

nidcd-presbycusis / main/block[6] / 261c131f8ca1dc401361909a

Scientists don't yet know how to prevent age-related hearing loss, but you can protect yourself from noise-induced hearing loss. Potential sources of damaging noises include loud music, headphones/earbuds used at high volume, construction equipment, fireworks, guns, lawn mowers, leaf blowers, and motorcycles. To help safeguard your hearing as you age, avoid loud noises, reduce the amount of time you're exposed to loud sounds, and protect your ears with earplugs or protective earmuffs.

### keyword 前三候选

1. nidcd-presbycusis / main/block[24] / cecceef4a0828e4a1a8e6aa8

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Hearing aids are electronic instruments you wear in or behind your ear. They make sounds louder. For mild to moderate hearing loss, a new category of hearing aids for adults was established in 2022 by the U.S. Food and Drug Administration. These devices may be purchased over the counter (OTC) from retail or online outlets without seeing a health care professional or getting a hearing test. If you have tried an OTC hearing aid without success or have trouble hearing loud sounds, consult a hearing health professional, because your hearing loss may be more severe.

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[2]/sec[1]/p[9] / c5359609e7b57507a55582b0

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

If hearing aids are fitted, this is generally done according to the applicable national hearing aid guidelines. In individual cases of isolated high-frequency hearing loss and high-frequency tinnitus, a hearing aid fitting can be useful even without the presence of hearing loss corresponding to these guidelines [94, 100–103].

3. nidcd-presbycusis / main/block[22] / b5eb56631abed6dbef52edd6

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

An audiologist (pronounced aw-dee-AH-luh-jist) has specialized training in identifying and measuring hearing loss, determining where along the auditory pathway there may be a problem with hearing, and recommending and providing certain hearing loss interventions, such as hearing aids.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. nidcd-presbycusis / main/block[6] / 261c131f8ca1dc401361909a

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Scientists don't yet know how to prevent age-related hearing loss, but you can protect yourself from noise-induced hearing loss. Potential sources of damaging noises include loud music, headphones/earbuds used at high volume, construction equipment, fireworks, guns, lawn mowers, leaf blowers, and motorcycles. To help safeguard your hearing as you age, avoid loud noises, reduce the amount of time you're exposed to loud sounds, and protect your ears with earplugs or protective earmuffs.

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[6]/p[1] / 9e440ee33778c2ce09a7c979

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Can the tinnitus be masked by ordinary ambient noise?

### hybrid 前三候选

1. nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

来源：https://www.nidcd.nih.gov/health/tinnitus

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

2. adult-com-qol-2023 / body/sec[4]/sec[2]/p[5] / 609104821df5d1b8ef5653d2

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The COMOT-15 is highly focused on hearing level with 7/15 items covering this subject. The degree of hearing impairment is used as an objective measurement to indicate the success of surgical treatment. Hearing loss is known to lower QoL in general (10, 48) and hearing aids are known to increase HRQoL (49, 50). This questions whether COMOT-15 is “overweighted” by hearing-related questions or whether this focus is actually needed for this otologic population. A multinational collaborative study demonstrated that patients with a higher degree of hearing loss had a poorer HRQoL, measured with COMQ-12. Moreover, this study argued postoperative hearing improvement is a better indicator of surgical success from a patient's perspective than a dry ear (16). A positive relation between the changes in audiometric data and the measured HRQoL improvement was also demonstrated in other studies (3, 8, 22, 36). Above all, hearing loss is stated to be the dominant symptom experienced by COM patients (51). However, in another study, the degree of hearing loss was argued to not adequately reflect the experienced disease burden of COM, nor the impact of treatment (52). This is supported by the lower changes in HRQoL reported by the hearing-specific questionnaire HHIA (SMD 0.40) compared to disease-specific COMQ-12 (SMD 1.21). Nevertheless, both questionnaires indicated statistically significant HRQoL improvement (42). Furthermore, ZCMEI-21 indicated differences in HRQoL between different types of chronic middle ear diseases, including COM with and without cholesteatoma, independent of hearing level. These findings imply a considerable impact of other symptoms besides hearing loss, such as ear discharge, vertigo, and tinnitus, on HRQoL (40). In line with this, a comparison of HRQoL measure

3. nidcd-presbycusis / main/block[24] / cecceef4a0828e4a1a8e6aa8

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Hearing aids are electronic instruments you wear in or behind your ear. They make sounds louder. For mild to moderate hearing loss, a new category of hearing aids for adults was established in 2022 by the U.S. Food and Drug Administration. These devices may be purchased over the counter (OTC) from retail or online outlets without seeing a health care professional or getting a hearing test. If you have tried an OTC hearing aid without success or have trouble hearing loud sounds, consult a hearing health professional, because your hearing loss may be more severe.

## ENT-028 — 我在聚会时常听不清别人讲话，这是不是听力自查资料关注的问题？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 1, 'hybrid': 1}

原锚点：

nidcd-presbycusis / main/block[9] / 41b72564df26b2524809d4c4

Does a hearing problem cause you difficulty when attending a party?

### keyword 前三候选

1. nidcd-presbycusis / main/block[24] / cecceef4a0828e4a1a8e6aa8

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Hearing aids are electronic instruments you wear in or behind your ear. They make sounds louder. For mild to moderate hearing loss, a new category of hearing aids for adults was established in 2022 by the U.S. Food and Drug Administration. These devices may be purchased over the counter (OTC) from retail or online outlets without seeing a health care professional or getting a hearing test. If you have tried an OTC hearing aid without success or have trouble hearing loud sounds, consult a hearing health professional, because your hearing loss may be more severe.

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[2]/sec[1]/p[9] / c5359609e7b57507a55582b0

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

If hearing aids are fitted, this is generally done according to the applicable national hearing aid guidelines. In individual cases of isolated high-frequency hearing loss and high-frequency tinnitus, a hearing aid fitting can be useful even without the presence of hearing loss corresponding to these guidelines [94, 100–103].

3. nidcd-presbycusis / main/block[22] / b5eb56631abed6dbef52edd6

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

An audiologist (pronounced aw-dee-AH-luh-jist) has specialized training in identifying and measuring hearing loss, determining where along the auditory pathway there may be a problem with hearing, and recommending and providing certain hearing loss interventions, such as hearing aids.

### vector 前三候选

1. nidcd-presbycusis / main/block[9] / 41b72564df26b2524809d4c4

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Does a hearing problem cause you difficulty when attending a party?

2. nidcd-presbycusis / main/block[17] / 4be865410f3411605aa2e695

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Does a hearing problem cause you to visit friends, relatives, or neighbors less often than you would like?

3. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

### hybrid 前三候选

1. nidcd-presbycusis / main/block[9] / 41b72564df26b2524809d4c4

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Does a hearing problem cause you difficulty when attending a party?

2. nidcd-presbycusis / main/block[24] / cecceef4a0828e4a1a8e6aa8

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Hearing aids are electronic instruments you wear in or behind your ear. They make sounds louder. For mild to moderate hearing loss, a new category of hearing aids for adults was established in 2022 by the U.S. Food and Drug Administration. These devices may be purchased over the counter (OTC) from retail or online outlets without seeing a health care professional or getting a hearing test. If you have tried an OTC hearing aid without success or have trouble hearing loud sounds, consult a hearing health professional, because your hearing loss may be more severe.

3. nidcd-presbycusis / main/block[17] / 4be865410f3411605aa2e695

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Does a hearing problem cause you to visit friends, relatives, or neighbors less often than you would like?

## ENT-029 — 我在安静房间听见嗡声，但家人听不到，资料如何定义耳鸣？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-tinnitus / main/block[1] / 130a4717c00194ae495cbc28

Tinnitus (pronounced tih-NITE-us or TIN-uh-tus) is the perception of sound that does not have an external source, so other people cannot hear it.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[9] / ebcf8a9adb0d86e5772eb6e7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Therapeutic approaches such as intratympanic steroid treatment do not affect chronic tinnitus [218, 219] if it does not occur in conjunction with acute hearing loss. A temporary increase in tinnitus intensity and tinnitus distress is not considered new-onset tinnitus but should be considered and treated as a fluctuation in the subjective perception of chronic tinnitus [220].

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[5]/p[1] / 789a95b61fbb441bb70703dc

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Is your tinnitus only audible in silence?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[5]/p[1] / 789a95b61fbb441bb70703dc

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Is your tinnitus only audible in silence?

2. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

## ENT-030 — 我耳鸣后睡不好又难以集中注意力，资料描述了哪些生活影响？

标记：all_strategies_missed_anchor, hybrid_missed_anchor, candidate_label_incompleteness；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-tinnitus / main/block[3] / ceec1220d73085b2d8292994

The causes of tinnitus are unclear, but most people who have it have some degree of hearing loss. Tinnitus is only rarely associated with a serious medical problem and is usually not severe enough to interfere with daily life. However, some people find that it affects their mood and their ability to sleep or concentrate. In severe cases, tinnitus can lead to anxiety or depression.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[9] / ebcf8a9adb0d86e5772eb6e7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Therapeutic approaches such as intratympanic steroid treatment do not affect chronic tinnitus [218, 219] if it does not occur in conjunction with acute hearing loss. A temporary increase in tinnitus intensity and tinnitus distress is not considered new-onset tinnitus but should be considered and treated as a fluctuation in the subjective perception of chronic tinnitus [220].

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[5]/p[5] / a55c53849e18c8d7ec98ecbb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Decompensated tinnitus: The ringing in the ears has a massive impact on all areas of life and leads to the development or aggravation of comorbidity (see Table 1; e.g. anxiety, sleep disorders, concentration disorders, depression). There is a high level of suffering. The quality of life is significantly impaired.

2. tinnitus-s3-2022 / body/sec[5]/sec[1]/p[5] / 2d8582982a469dc23fd9c863

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These changes reflect neuroplastic processes that are thought to be triggered by auditory deprivation. Similar to phantom limb pain, there is thought to be increased excitation, plasticity and connectivity along the entire central auditory pathway—as a compensatory response to reduced sensory input [18–21]. However, it has also been shown that abnormal activity can be found in somatosensory afferents [22]. Furthermore, patients with chronic tinnitus show functional changes not only in auditory structures but also in limbic, parietal and frontal areas [23–25]. The functional connectivity between auditory and non-auditory areas appears to be increased in tinnitus patients [26–31]. These tinnitus-associated structural and functional changes in neuronal networks are not static but change with increasing duration of tinnitus [26, 32, 33]. They are also significantly influenced by attentional redirection as tinnitus accentuation [34].

3. adult-com-qol-2023 / body/sec[4]/sec[2]/p[4] / 06f9958d0af47fe51960ac6b

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

As was mentioned before, the CES does not cover psychological and emotional aspects of the perceived impact of COM on the HRQoL while these aspects are an important part of the HRQoL construct. Patients with more prominent depressive symptoms and mood disturbances have significantly higher COMOT-15 and ZCMEI-21 scores and significantly lower SF-36 scores (31), all indicating lower HRQoL. Moreover, hearing loss and the corresponding communication impairment are associated with depression, social withdrawal, and anxiety and thereby limit a patient's HRQoL (47). This incomplete coverage of the HRQoL construct by the CES might explain the high percentages of change and large SMDs reported with CES. One could logically expect a decrease in HRQoL improvement measured by the CES once psychological and emotional aspects are included.

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[1]/p[2] / bdb1250ed3a4126f4dac9518

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Central nervous processing often leads to pathologically exaggerated neuronal stimulus responses in severely affected persons with tinnitus (such as exaggerated attentional control of the tinnitus, triggering of anxiety, sleep disturbances). Particular central psychophysiological and neurophysiological processing mechanisms of the tinnitus stimulus are held responsible for these pathologically exaggerated stimulus responses.

2. tinnitus-s3-2022 / body/sec[5]/sec[5]/p[5] / a55c53849e18c8d7ec98ecbb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Decompensated tinnitus: The ringing in the ears has a massive impact on all areas of life and leads to the development or aggravation of comorbidity (see Table 1; e.g. anxiety, sleep disorders, concentration disorders, depression). There is a high level of suffering. The quality of life is significantly impaired.

3. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

## ENT-031 — 我的耳鸣有时像口哨、有时像电流声，这些声音形式在资料中有描述吗？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-tinnitus / main/block[5] / 7bb37be516fd5c62989dad6b

The symptoms of tinnitus can vary significantly from person to person. You may hear phantom sounds in one ear, in both ears, and in your head. The phantom sound may ring, buzz, roar, whistle, hum, click, hiss, or squeal. The sound may be soft or loud and may be low or high pitched. It may come and go or be present all the time. Sometimes, moving your head, neck, or eyes, or touching certain parts of your body may produce tinnitus symptoms or temporarily change the quality of the perceived sound. This is called somatosensory (pronounced so-ma-toe-SENSE-uh-ree) tinnitus.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[9] / ebcf8a9adb0d86e5772eb6e7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Therapeutic approaches such as intratympanic steroid treatment do not affect chronic tinnitus [218, 219] if it does not occur in conjunction with acute hearing loss. A temporary increase in tinnitus intensity and tinnitus distress is not considered new-onset tinnitus but should be considered and treated as a fluctuation in the subjective perception of chronic tinnitus [220].

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[5]/p[1] / 789a95b61fbb441bb70703dc

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Is your tinnitus only audible in silence?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[5]/p[1] / 789a95b61fbb441bb70703dc

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Is your tinnitus only audible in silence?

## ENT-032 — 我听见的声音好像跟心跳同步，资料如何区分这种耳鸣与通常耳鸣？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-tinnitus / main/block[6] / e6228c005748eba7217465a8

Most cases of tinnitus are subjective, meaning that only you can hear the sounds. In rare cases, the sound pulsates rhythmically, often in time to your heartbeat. In these cases, a doctor may be able to hear the sounds with a stethoscope and, if so, it is considered to be objective tinnitus. Often, objective tinnitus has an identifiable cause and is treatable.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[9] / ebcf8a9adb0d86e5772eb6e7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Therapeutic approaches such as intratympanic steroid treatment do not affect chronic tinnitus [218, 219] if it does not occur in conjunction with acute hearing loss. A temporary increase in tinnitus intensity and tinnitus distress is not considered new-onset tinnitus but should be considered and treated as a fluctuation in the subjective perception of chronic tinnitus [220].

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[1]/p[1] / 8270973feab83f126ef0c2cb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

In which ear do you hear your tinnitus (right, left, both sides, head)?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

## ENT-033 — 我参加很吵的演唱会后出现耳鸣，现有资料是否提到噪声暴露关联？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-tinnitus / main/block[8] / 454875ee98fced975d4b1caa

Noise exposure. Many people experience tinnitus after being exposed to loud noise in a workplace setting or at a sporting event or concert. Tinnitus is also the most common service-related disability among veterans because of loud noise they may have experienced from gunfire, machinery, bomb blasts, or other similar sources.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[9] / ebcf8a9adb0d86e5772eb6e7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Therapeutic approaches such as intratympanic steroid treatment do not affect chronic tinnitus [218, 219] if it does not occur in conjunction with acute hearing loss. A temporary increase in tinnitus intensity and tinnitus distress is not considered new-onset tinnitus but should be considered and treated as a fluctuation in the subjective perception of chronic tinnitus [220].

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. nidcd-presbycusis / main/block[9] / 41b72564df26b2524809d4c4

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Does a hearing problem cause you difficulty when attending a party?

3. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

3. nidcd-presbycusis / main/block[9] / 41b72564df26b2524809d4c4

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Does a hearing problem cause you difficulty when attending a party?

## ENT-034 — 有听力下降就一定会耳鸣吗？

标记：anchor_hit_control；原锚点排名：{'keyword': 2, 'vector': None, 'hybrid': 1}

原锚点：

nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[6] / 61d8c80cb5ed39d0375201d1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Treatment of acute tinnitus follows the treatment recommendations for acute sudden hearing loss. For the treatment of acute hearing loss, corresponding guidelines (AWMF 017/2914 currently being updated [82]; guideline USA [83]) recommend systemic or intratympanic steroid treatment with, however, moderate evidence. Therefore, acute tinnitus with hearing loss or following hearing loss should be treated appropriately. If the tinnitus occurs acutely without measurable hearing loss, the standard cortisone therapy recommended for hearing loss is not recommended.

2. nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

来源：https://www.nidcd.nih.gov/health/tinnitus

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

3. nidcd-presbycusis / main/block[22] / b5eb56631abed6dbef52edd6

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

An audiologist (pronounced aw-dee-AH-luh-jist) has specialized training in identifying and measuring hearing loss, determining where along the auditory pathway there may be a problem with hearing, and recommending and providing certain hearing loss interventions, such as hearing aids.

### vector 前三候选

1. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

2. nidcd-presbycusis / main/block[15] / d3fd71f4cb27202bed8ec1be

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Does a hearing problem cause you to feel uncomfortable when talking to friends?

3. nidcd-presbycusis / main/block[14] / cea4a187bf18ea0daaacb29d

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel that any difficulty with your hearing limits or hampers your personal or social life?

### hybrid 前三候选

1. nidcd-tinnitus / main/block[9] / ac82efccc47cb4abdbba6d03

来源：https://www.nidcd.nih.gov/health/tinnitus

Hearing loss. Hearing loss, which can be caused by factors such as aging or exposure to loud noise, is strongly associated with tinnitus. Some people with hearing loss, however, never develop tinnitus.

2. nidcd-presbycusis / main/block[6] / 261c131f8ca1dc401361909a

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Scientists don't yet know how to prevent age-related hearing loss, but you can protect yourself from noise-induced hearing loss. Potential sources of damaging noises include loud music, headphones/earbuds used at high volume, construction equipment, fireworks, guns, lawn mowers, leaf blowers, and motorcycles. To help safeguard your hearing as you age, avoid loud noises, reduce the amount of time you're exposed to loud sounds, and protect your ears with earplugs or protective earmuffs.

3. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

## ENT-035 — 我有耳垢堵塞，资料是否把耳道堵塞和耳鸣联系起来？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-tinnitus / main/block[11] / d3b1524e2af775d7bcf4bbcd

Earwax or an ear infection. Blockage of the ear canal by earwax or by fluid from an ear infection can trigger tinnitus.

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[9] / ebcf8a9adb0d86e5772eb6e7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Therapeutic approaches such as intratympanic steroid treatment do not affect chronic tinnitus [218, 219] if it does not occur in conjunction with acute hearing loss. A temporary increase in tinnitus intensity and tinnitus distress is not considered new-onset tinnitus but should be considered and treated as a fluctuation in the subjective perception of chronic tinnitus [220].

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

3. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

## ENT-036 — 我说话声音粗哑、音量也变小，资料如何描述声音嘶哑？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-hoarseness / main/block[2] / 11431f15a7d129a44f3dedfb

If you are hoarse, your voice will sound breathy, raspy, or strained, or will be softer in volume or lower in pitch. Your throat might feel scratchy. Hoarseness is often a symptom of problems in the vocal folds of the larynx.

### keyword 前三候选

### vector 前三候选

1. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

3. nidcd-hoarseness / main/block[1] / b7c66fd4bd97a3fc3028156c

来源：https://www.nidcd.nih.gov/health/hoarseness

Structures involved in speech and voice production

### hybrid 前三候选

1. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

3. nidcd-hoarseness / main/block[1] / b7c66fd4bd97a3fc3028156c

来源：https://www.nidcd.nih.gov/health/hoarseness

Structures involved in speech and voice production

## ENT-037 — 医生提到声带振动，声音到底由哪里产生？

标记：anchor_hit_control；原锚点排名：{'keyword': None, 'vector': 6, 'hybrid': 6}

原锚点：

nidcd-hoarseness / main/block[3] / e0df42209aff4e381b2cb825

The sound of our voice is produced by vibration of the vocal folds, which are two bands of smooth muscle tissue that are positioned opposite each other in the larynx. The larynx is located between the base of the tongue and the top of the trachea, which is the passageway to the lungs (see figure).

### keyword 前三候选

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[20]/p[1] / acc38c88d10d3695c7f81c97

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Can the tinnitus be influenced by certain jaw/chewing muscle tension?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[3]/p[1] / a46ee2ead88ae5c43d2eae27

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Did your tinnitus start suddenly or slowly (right, left)?

3. nidcd-hoarseness / main/block[1] / b7c66fd4bd97a3fc3028156c

来源：https://www.nidcd.nih.gov/health/hoarseness

Structures involved in speech and voice production

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[20]/p[1] / acc38c88d10d3695c7f81c97

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Can the tinnitus be influenced by certain jaw/chewing muscle tension?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[3]/p[1] / a46ee2ead88ae5c43d2eae27

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Did your tinnitus start suddenly or slowly (right, left)?

3. nidcd-hoarseness / main/block[1] / b7c66fd4bd97a3fc3028156c

来源：https://www.nidcd.nih.gov/health/hoarseness

Structures involved in speech and voice production

## ENT-038 — 我的声音有时高有时低，资料怎样解释声带张力与音高的关系？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-hoarseness / main/block[5] / 855545214f4be7613e014f31

Individual variations in our voices are the result of how much tension we put on our vocal folds. For example, relaxing the vocal folds makes a voice deeper; tensing them makes a voice higher.

### keyword 前三候选

### vector 前三候选

1. nidcd-hoarseness / main/block[1] / b7c66fd4bd97a3fc3028156c

来源：https://www.nidcd.nih.gov/health/hoarseness

Structures involved in speech and voice production

2. nidcd-tinnitus / main/block[13] / b9115e60d6dbbd64e9c841ae

来源：https://www.nidcd.nih.gov/health/tinnitus

Less common tinnitus risk factors include:

3. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

### hybrid 前三候选

1. nidcd-hoarseness / main/block[1] / b7c66fd4bd97a3fc3028156c

来源：https://www.nidcd.nih.gov/health/hoarseness

Structures involved in speech and voice production

2. nidcd-tinnitus / main/block[13] / b9115e60d6dbbd64e9c841ae

来源：https://www.nidcd.nih.gov/health/tinnitus

Less common tinnitus risk factors include:

3. nidcd-presbycusis / main/block[13] / 3b752d245c0875d969f16587

来源：https://www.nidcd.nih.gov/health/age-related-hearing-loss

Do you feel challenged by a hearing problem?

## ENT-039 — 我是教师，连续大声讲课后声音沙哑，资料有没有描述用声过度？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-hoarseness / main/block[10] / b3a7516e456b04ea8b67393e

Misusing or overusing your voice. Cheering at sporting events, speaking loudly in noisy situations, talking for too long without resting your voice, singing loudly, or speaking with a voice that's too high or too low can cause temporary hoarseness. Resting, reducing voice use, and drinking lots of water should help relieve hoarseness from misuse or overuse. Sometimes people whose jobs depend on their voices—such as teachers, singers, or public speakers—develop hoarseness that won't go away. If you use your voice for a living and you regularly experience hoarseness, your doctor might suggest seeing a speech-language pathologist for voice therapy. In voice therapy, you'll be given vocal exercises and tips for avoiding hoarseness by changing the ways in which you use your voice.

### keyword 前三候选

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

## ENT-040 — 我没有烧心但晨起声音嘶哑、总想清嗓，资料是否解释过咽喉反流与烧心的区别？

标记：anchor_hit_control；原锚点排名：{'keyword': 2, 'vector': None, 'hybrid': 3}

原锚点：

nidcd-hoarseness / main/block[11] / ae55fda5b78117ee68fc84b9

Gastroesophageal reflux (GERD). GERD—commonly called heartburn—can cause hoarseness when stomach acid rises up the throat and irritates the tissues. Usually hoarseness caused by GERD is worse in the morning and improves throughout the day. In some people, the stomach acid rises all the way up to the throat and larynx and irritates the vocal folds. This is called laryngopharyngeal reflux (LPR). LPR can happen during the day or night. Some people will have no heartburn with LPR, but they may feel as if they constantly have to cough to clear their throat and they may become hoarse. GERD and LPR are treated with dietary modifications and medications that reduce stomach acid.

### keyword 前三候选

1. adult-sore-throat-review-2024 / body/sec[1]/p[1] / 17a5c7a6dce8f609bc598334

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

Complaints among adults are a reason for seeking healthcare globally [1]. Viral infections account for around 85% of cases, while bacterial, fungal, smoking, intubation, and yelling account for 15% of sore throat causes [2]. Even though sore throat cases are primarily due to viral infections, they are considered one of the most common cases where using antibiotics is prevalent worldwide [3]. Sore throat management depends on using analgesics such as acetaminophen and non-steroidal anti-inflammatory drugs (NSAIDs) [4]. Although these medications have detectable safety profiles, a significant number of preventable adverse drug reactions (ADRs) associated with analgesics are still present [5].

2. nidcd-hoarseness / main/block[11] / ae55fda5b78117ee68fc84b9

来源：https://www.nidcd.nih.gov/health/hoarseness

Gastroesophageal reflux (GERD). GERD—commonly called heartburn—can cause hoarseness when stomach acid rises up the throat and irritates the tissues. Usually hoarseness caused by GERD is worse in the morning and improves throughout the day. In some people, the stomach acid rises all the way up to the throat and larynx and irritates the vocal folds. This is called laryngopharyngeal reflux (LPR). LPR can happen during the day or night. Some people will have no heartburn with LPR, but they may feel as if they constantly have to cough to clear their throat and they may become hoarse. GERD and LPR are treated with dietary modifications and medications that reduce stomach acid.

3. adult-sore-throat-review-2024 / body/sec[2]/p[7] / 10d85922503285e75e5bbccd

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

The studies involved adult patients exhibiting signs of tonsillitis, pharyngitis, or sore throat and were conducted in both emergency and primary care environments.

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[20]/p[1] / acc38c88d10d3695c7f81c97

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Can the tinnitus be influenced by certain jaw/chewing muscle tension?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

### hybrid 前三候选

1. adult-sore-throat-review-2024 / body/sec[1]/p[1] / 17a5c7a6dce8f609bc598334

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

Complaints among adults are a reason for seeking healthcare globally [1]. Viral infections account for around 85% of cases, while bacterial, fungal, smoking, intubation, and yelling account for 15% of sore throat causes [2]. Even though sore throat cases are primarily due to viral infections, they are considered one of the most common cases where using antibiotics is prevalent worldwide [3]. Sore throat management depends on using analgesics such as acetaminophen and non-steroidal anti-inflammatory drugs (NSAIDs) [4]. Although these medications have detectable safety profiles, a significant number of preventable adverse drug reactions (ADRs) associated with analgesics are still present [5].

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

3. nidcd-hoarseness / main/block[11] / ae55fda5b78117ee68fc84b9

来源：https://www.nidcd.nih.gov/health/hoarseness

Gastroesophageal reflux (GERD). GERD—commonly called heartburn—can cause hoarseness when stomach acid rises up the throat and irritates the tissues. Usually hoarseness caused by GERD is worse in the morning and improves throughout the day. In some people, the stomach acid rises all the way up to the throat and larynx and irritates the vocal folds. This is called laryngopharyngeal reflux (LPR). LPR can happen during the day or night. Some people will have no heartburn with LPR, but they may feel as if they constantly have to cough to clear their throat and they may become hoarse. GERD and LPR are treated with dietary modifications and medications that reduce stomach acid.

## ENT-041 — 喉镜报告写声带结节、息肉或囊肿，这几个术语在资料中怎么解释？

标记：all_strategies_missed_anchor, hybrid_missed_anchor；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

原锚点：

nidcd-hoarseness / main/block[12] / 8d02ce3b5c6bccc3e30f98f1

Vocal nodules, polyps, and cysts. Vocal nodules, polyps, and cysts are benign (noncancerous) growths within or along the vocal folds. Vocal nodules are sometimes called "singer's nodes" because they are a frequent problem among professional singers. They form in pairs on opposite sides of the vocal folds as the result of too much pressure or friction, much like the way a callus forms on the foot from a shoe that's too tight. A vocal polyp typically occurs only on one side of the vocal fold. A vocal cyst is a hard mass of tissue encased in a membrane sac inside the vocal fold. The most common treatments for nodules, polyps, and cysts are voice rest, voice therapy, and surgery to remove the tissue.

### keyword 前三候选

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[26]/p[1] / e0f0fec02b7855d194b38214

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are there any indications of other disorders and comorbidities (see Table 1)?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[26]/p[1] / e0f0fec02b7855d194b38214

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are there any indications of other disorders and comorbidities (see Table 1)?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

## ENT-042 — 这份成人咽痛系统综述主要覆盖什么人群和就诊场景？

标记：anchor_hit_control；原锚点排名：{'keyword': 2, 'vector': None, 'hybrid': 4}

原锚点：

adult-sore-throat-review-2024 / body/sec[2]/p[7] / 10d85922503285e75e5bbccd

The studies involved adult patients exhibiting signs of tonsillitis, pharyngitis, or sore throat and were conducted in both emergency and primary care environments.

### keyword 前三候选

1. adult-sore-throat-review-2024 / body/sec[1]/p[1] / 17a5c7a6dce8f609bc598334

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

Complaints among adults are a reason for seeking healthcare globally [1]. Viral infections account for around 85% of cases, while bacterial, fungal, smoking, intubation, and yelling account for 15% of sore throat causes [2]. Even though sore throat cases are primarily due to viral infections, they are considered one of the most common cases where using antibiotics is prevalent worldwide [3]. Sore throat management depends on using analgesics such as acetaminophen and non-steroidal anti-inflammatory drugs (NSAIDs) [4]. Although these medications have detectable safety profiles, a significant number of preventable adverse drug reactions (ADRs) associated with analgesics are still present [5].

2. adult-sore-throat-review-2024 / body/sec[2]/p[7] / 10d85922503285e75e5bbccd

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

The studies involved adult patients exhibiting signs of tonsillitis, pharyngitis, or sore throat and were conducted in both emergency and primary care environments.

3. adult-sore-throat-review-2024 / body/sec[1]/p[4] / 79db22c996037bff0351b7f3

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

While previous research has investigated the efficacy of corticosteroids across various age groups and populations, a detailed pooled analysis is still needed among adult populations. Therefore, we developed this review to evaluate the efficacy of corticosteroids as an additional treatment approach for infectious sore throat.

### vector 前三候选

1. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[15]/p[1] / de578a0f6f0947d49da31b6c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you or other people notice that you hear or understand worse?

3. crs-apac-2024 / body/sec[9]/p[2] / 48d02b1c90d22132535f7a4a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Use of biologics is now established in current guidelines, although differences exist in specific criteria and thresholds [1, 2, 6-8, 27]. The EPOS 2020 guidelines indicate that biologics can be considered if at least 3 of the following 5 features are present; (1) evidence of type 2 inflammation (tissue eosinophilia ≥10 cells/high-power field, or serum eosinophilia ≥250 cells/µL, or total serum IgE ≥100 IU/mL); (2) need for systemic corticosteroids (≥2 courses OCS per year or long-term [>3 months] low-dose steroids) or contraindications for systemic corticosteroids; (3) significantly impaired QoL (eg, with SNOT-22 ≥40); (4) significant loss of smell (anosmia on smell test); (5) with comorbid asthma (requiring regular inhaled corticosteroids) [1, 2]. Looking specifically at the criteria for evidence of type 2 inflammation, in the panel’s view, while evidence of type 2 inflammation is an important criterion, these cutoff thresholds may not be fully appropriate or applicable for Asian populations, and their strict application may obstruct access to patients who may benefit from biologics. For Asian patients, alternative thresholds may apply. Serum eosinophilia ≥250 cells/µL may be the most reliable marker of type 2 inflammation in Asian patients, while a total serum IgE ≥150 IU/mL is more typical of nontype 2 inflammation. Tissue eosinophilia of ≥10 cells/high-power field may be a weak biomarker in Asian patients, where when used to assess status in patients with recurrent disease following surgery, a higher threshold of between 70 and 100 eosinophils per high-power field is used. When considering the need for systemic corticosteroids, patient reluctance or refusal to take systemic steroids should also be taken into account.

### hybrid 前三候选

1. adult-sore-throat-review-2024 / body/sec[2]/p[26] / d72c432ce7617ee8dd97b993

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

Through the systematic literature search, we identified 2415 titles and abstracts, of which 50 were selected for retrieval. Of the 50 studies, 45 were excluded (20 were not randomized trials; 16 had no individuals with a sore throat; in 9 studies, corticosteroids were not mentioned in the studies as an intervention or compared with a placebo/usual care). Figure 1 illustrates the details of the study selection process. Finally, the review included five studies that were eligible and enrolled 866 participants [15-19]. Three studies included patients from emergency departments (ED) and two from primary care [15-19]. All studies enrolled adults. The most prevalent intervention in three studies was a single 10 mg dose of oral dexamethasone for adults. In two studies, all patients were treated with antibiotics and analgesics as part of their standard care [16,18]. In one trial, all patients were given antibiotics, and analgesics were administered based on the physician’s judgment [19]. In two trials, patients in the usual care group were given antibiotics or analgesics based on the physician's judgment [15,17]. Table 1 presents the main characteristics of the included studies.

2. adult-sore-throat-review-2024 / body/sec[1]/p[1] / 17a5c7a6dce8f609bc598334

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

Complaints among adults are a reason for seeking healthcare globally [1]. Viral infections account for around 85% of cases, while bacterial, fungal, smoking, intubation, and yelling account for 15% of sore throat causes [2]. Even though sore throat cases are primarily due to viral infections, they are considered one of the most common cases where using antibiotics is prevalent worldwide [3]. Sore throat management depends on using analgesics such as acetaminophen and non-steroidal anti-inflammatory drugs (NSAIDs) [4]. Although these medications have detectable safety profiles, a significant number of preventable adverse drug reactions (ADRs) associated with analgesics are still present [5].

3. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

## ENT-043 — 我家5岁孩子耳鸣，可以直接套用这个成人库吗？

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

1. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[4]/sec[1]/p[6] / abe9d3b01af033917c38f753

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

TRT is a habituation technique that reduces the auditory, emotional and autonomic impact of the tinnitus noise and thus reduces the stress response to the tinnitus stimulus. It integrates three to five intervention steps including a detailed tinnitus history, auditory distraction from the tinnitus by broadband noise via a tinnitus instrument and psychological counselling.

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[6]/sec[1]/p[9] / ebcf8a9adb0d86e5772eb6e7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Therapeutic approaches such as intratympanic steroid treatment do not affect chronic tinnitus [218, 219] if it does not occur in conjunction with acute hearing loss. A temporary increase in tinnitus intensity and tinnitus distress is not considered new-onset tinnitus but should be considered and treated as a fluctuation in the subjective perception of chronic tinnitus [220].

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[6]/p[1] / 9e440ee33778c2ce09a7c979

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Can the tinnitus be masked by ordinary ambient noise?

3. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[10]/sec[1]/p[5] / f0056eb93ba3a42b598a9968

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Several nutritional supplements have been used for tinnitus, including lipoflavonoids, garlic, homeopathy, traditional Chinese–Korean herbal medicine, honeybee larvae, and various vitamins and minerals. Evidence of the efficacy of these therapies for tinnitus is not available [232]. A more recent review also finds that there is no evidence of dietary supplements on tinnitus. In particular, a reduction of salt or caffeine had neither a positive nor a negative effect on tinnitus perception [303]. In a review by Wegner et al. [226], five studies with approx. 300 tinnitus patients each were examined concerning betahistine administration versus placebo (vitamin B12), and no effect (−0.16) on tinnitus loudness and impairment was found after 12 weeks.

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[9]/p[1] / 6c2ee97634b254388d56aed8

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Does normal environmental noise make your tinnitus louder?

3. tinnitus-s3-2022 / body/sec[5]/sec[4]/p[1] / b2e23134549a2cdea4235394

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Comorbidities (see Table 1) may be pre-existing, independent of tinnitus or tinnitus-induced. Psychological and/or psychosomatic comorbidities are frequently found in connection with tinnitus [48, 49]. In particular, anxiety disorders, depression and sleep disorders are found more frequently in patients with tinnitus. Depression and other psychological disorders are risk factors for the development of tinnitus and can intensify tinnitus [9, 50].

## ENT-044 — 请给3岁幼儿制定过敏性鼻炎治疗方案。

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

1. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

2. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[6] / aca0e617998d6dd0e3faae93

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

Certainly the presence of rhinitis, both allergic and non-allergic, is a risk factor for subsequent asthma development [14].

3. adult-rhinitis-eaaci-2017 / body/sec[4]/p[2] / c9f1e17cf990d1563c4c9934

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

A physical examination of all organ systems potentially affected by allergies, with emphasis on the upper respiratory tract, should be performed in patients with a history of rhinitis.

### vector 前三候选

1. crs-apac-2024 / body/sec[8]/p[1] / a79dc02259380c9a812b7f84

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

From a treatment perspective, principal first-line options are nasal saline irrigation and use of topical INS, either as sprays or drops, and intermittent use of OCS [1, 2, 9] (Fig. 1). Topical nasal irrigation is a key element of CRSwNP treatment, and practical advice on self-care (ie, correct nasal irrigation technique) is fundamental. While different solutions may be used, isotonic saline is a safe and effective and convenient low-cost option [10]. A wide range of INS preparations are available [20, 35-37], and INS are well tolerated with no significant adverse effects [1, 2, 9]. During EPOS 2020 guideline development, the steering group appraised those studies evaluating INS and concluded that there was evidence for some improvement in CRSwNP symptoms and in QoL (with reductions in SNOT-22 scores) [1, 2]. Although antibiotics are often used, there are limited data for benefit in the treatment of CRSwNP [1, 2]. If response is poor, OCS can be used, although only as short-term use (eg, for up to 2 weeks) due to recognized risks with prolonged treatment [1, 2, 38]. There is some evidence for short-term improvement in symptoms (eg, smell and nasal blockage) with OCS [1, 2, 39], and short-term intermittent use (eg, 1–2 courses per year) can be beneficial in patients with poor response or uncontrolled disease [1, 2]. Some patients may be reluctant to use OCS, an issue frequently encountered in Russia, and so a clear explanation of risks and benefits of OCS may be necessary.

2. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[13]/p[1] / c0c1fe5fa6732adaedba9df6

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Are you particularly sensitive to noise?

### hybrid 前三候选

1. crs-apac-2024 / body/sec[3]/p[2] / 8073961684788d1508e1d026

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

The cardinal symptoms of CRS are similar to acute disease, that is, nasal obstruction, congestion or discharge, facial pain/pressure, and olfactory disturbance/loss of smell [1, 2, 11, 12]. Overt facial pain with CRSwNP is uncommon in the Asian patients, where headache (or complaints of pressure or fullness) or nasal obstruction may be more common presenting symptoms. While allergic symptoms (eg, sneezing or itching) are not part of existing diagnostic criteria, their presence may indicate an additional diagnosis of allergic rhinitis. In EPOS 2020, the diagnosis of CRS requires rhinosinusitis lasting for ≥12 weeks (without interruption, as patients may experience recurrent episodes of acute rhinosinusitis) [1, 2]. This assumes that any acute rhinosinusitis has been managed appropriately (ie, with nasal irrigation and INS). Diagnosis of CRSwNP requires the presence of bilateral, endoscopically visualized polyps in the middle meatus [1, 2]. While a minimum duration of 12 weeks reflects a useful policy for chronic disease diagnosis from a symptomatic perspective, this need not be considered absolute. For example, if evidence of more chronic and significant disease already exists (eg, objective findings of nasal polyps on endoscopic examination), then an earlier presumptive diagnosis of CRSwNP would seem appropriate. As discussed later, what is perhaps most important is the need for timely referral for specialist evaluation at the earliest opportunity. Where polyps are absent, patients are considered to have chronic rhinosinusitis without nasal polyps (CRSsNP). When endoscopy or CT shows only unilateral disease, then alternative diagnoses (especially neoplasia) must be considered [1, 2].

2. crs-apac-2024 / body/sec[4]/p[1] / 53a5c5927f530c1f90cf2788

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Pathophysiologic mechanisms in CRSwNP involve a complex interaction of host and environmental factors, where specific individual patient profiles are a product of both endotype and phenotype. CRS and specific types such as CRSwNP are now characterized on the basis of the predominant underlying inflammatory pattern (or endotype) and predominant clinical phenotype in current classifications such as EPOS 2020 [1, 2]. Endotypes broadly reflect the underlying biology and pathogenetic mechanisms such as the inflammatory profile (eg, a type 2 dominant inflammatory signature), now especially relevant following the development of novel biologic therapies targeting underlying type 2 inflammatory processes in CRSwNP [13, 14]. Phenotypes reflect the patient’s clinical profile (including comorbid disease) [15, 16]. From a phenotypic perspective, the broad global pattern is that while asthma is more prevalent in patients with CRS compared with the general population, coexisting asthma is even more strongly associated with CRSwNP (30%–70% of patients) and the severity of asthma is also greater in CRSwNP [3, 17-19]. Comorbidities such as allergic rhinitis, NSAID/aspirin-exacerbated respiratory disease, and atopic dermatitis are also more prevalent in CRSwNP than in CRSsNP [20]. This association of CRSwNP and other inflammatory disease often reflects the common underlying type 2 inflammatory processes in these conditions, with eosinophilic tissue inflammation mediated by type 2 cytokines, for example, interleukin (IL)-4, IL-5, and IL-13 and local/circulating IgE, observed in the majority of patients with CRSwNP [15]. However, these patterns show substantial heterogeneity in different geographical populations (including within the APAC region). For example, in Hong Kong, only approximate

3. adult-rhinitis-eaaci-2017 / body/sec[3]/sec[1]/sec[1]/p[2] / 17abd7d202f2e57e8c352a7a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC5452333/

The association between asthma and rhinitis in adults has been recognized for some decades, since the pioneering study of Brydon [7], who showed that the majority of 1000 asthmatics also had rhinitis, which preceded their asthma in 45% of the subjects.

## ENT-045 — 你们医院明天耳鼻喉科的挂号价格和空号是多少？

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

### vector 前三候选

1. crs-apac-2024 / body/sec[9]/p[2] / 48d02b1c90d22132535f7a4a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Use of biologics is now established in current guidelines, although differences exist in specific criteria and thresholds [1, 2, 6-8, 27]. The EPOS 2020 guidelines indicate that biologics can be considered if at least 3 of the following 5 features are present; (1) evidence of type 2 inflammation (tissue eosinophilia ≥10 cells/high-power field, or serum eosinophilia ≥250 cells/µL, or total serum IgE ≥100 IU/mL); (2) need for systemic corticosteroids (≥2 courses OCS per year or long-term [>3 months] low-dose steroids) or contraindications for systemic corticosteroids; (3) significantly impaired QoL (eg, with SNOT-22 ≥40); (4) significant loss of smell (anosmia on smell test); (5) with comorbid asthma (requiring regular inhaled corticosteroids) [1, 2]. Looking specifically at the criteria for evidence of type 2 inflammation, in the panel’s view, while evidence of type 2 inflammation is an important criterion, these cutoff thresholds may not be fully appropriate or applicable for Asian populations, and their strict application may obstruct access to patients who may benefit from biologics. For Asian patients, alternative thresholds may apply. Serum eosinophilia ≥250 cells/µL may be the most reliable marker of type 2 inflammation in Asian patients, while a total serum IgE ≥150 IU/mL is more typical of nontype 2 inflammation. Tissue eosinophilia of ≥10 cells/high-power field may be a weak biomarker in Asian patients, where when used to assess status in patients with recurrent disease following surgery, a higher threshold of between 70 and 100 eosinophils per high-power field is used. When considering the need for systemic corticosteroids, patient reluctance or refusal to take systemic steroids should also be taken into account.

2. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

3. adult-sore-throat-review-2024 / body/sec[2]/p[13] / b768f454ce8699562bbd27b3

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

The search used five databases: Pubmed, Medline, OVID, Cochrane CENTRAL, and Scopus. We conducted our search without applying any filters, covering the period from the inception of the database until July 1, 2024. Key terms for sore throat conditions included “nasopharyngitis, tonsillitis, pharyngitis, nasopharyngi, or Streptococcus.” We targeted studies using steroids, glucocorticoids, hydroxycorticosteroids, hydroxypregnenolone, corticosterone, paramethasone, or betamethasone. We focused on studies designed as randomized trials. The combined search string was `[[[[nasopharyng] OR [Tonsillitis] OR [Pharyngitis] OR [nasopharyngi] OR [Streptococcus]] AND [[steroid] OR [Glucocorticoids] OR [Hydroxycorticosteroid] OR [hydroxypregnenolone] OR [corticosterone] OR [paramethasone] OR [betamethasone]]] AND [[clinical trial] OR [RCT] OR [randomized clinical trial]]]]`(see Table 3 of Appendix A).

### hybrid 前三候选

1. crs-apac-2024 / body/sec[9]/p[2] / 48d02b1c90d22132535f7a4a

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Use of biologics is now established in current guidelines, although differences exist in specific criteria and thresholds [1, 2, 6-8, 27]. The EPOS 2020 guidelines indicate that biologics can be considered if at least 3 of the following 5 features are present; (1) evidence of type 2 inflammation (tissue eosinophilia ≥10 cells/high-power field, or serum eosinophilia ≥250 cells/µL, or total serum IgE ≥100 IU/mL); (2) need for systemic corticosteroids (≥2 courses OCS per year or long-term [>3 months] low-dose steroids) or contraindications for systemic corticosteroids; (3) significantly impaired QoL (eg, with SNOT-22 ≥40); (4) significant loss of smell (anosmia on smell test); (5) with comorbid asthma (requiring regular inhaled corticosteroids) [1, 2]. Looking specifically at the criteria for evidence of type 2 inflammation, in the panel’s view, while evidence of type 2 inflammation is an important criterion, these cutoff thresholds may not be fully appropriate or applicable for Asian populations, and their strict application may obstruct access to patients who may benefit from biologics. For Asian patients, alternative thresholds may apply. Serum eosinophilia ≥250 cells/µL may be the most reliable marker of type 2 inflammation in Asian patients, while a total serum IgE ≥150 IU/mL is more typical of nontype 2 inflammation. Tissue eosinophilia of ≥10 cells/high-power field may be a weak biomarker in Asian patients, where when used to assess status in patients with recurrent disease following surgery, a higher threshold of between 70 and 100 eosinophils per high-power field is used. When considering the need for systemic corticosteroids, patient reluctance or refusal to take systemic steroids should also be taken into account.

2. crs-apac-2024 / body/sec[6]/p[1] / 2d4e6c40561c7d43de77bba7

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11142757/

Multidisciplinary specialist management involving both ORLs and allergists/immunologists/pulmonologists provides an optimal approach to ensure comprehensive evaluation and optimal use of the most appropriate surgical and medical therapeutic strategies [25, 26]. For CRS, immediate referral is essential in the presence of any red-flag alarm signs or symptoms (eg, visual upset, severe headache, and neurological signs) [1, 2]. Although EPOS 2022 describes a self-care element (in which patients may receive advice and over the counter symptomatic relief medication), the panel recommends early referral from primary care for all patients with CRS or suspected CRSwNP (ideally within 6–12 weeks) [1, 2]. This facilitates earlier endoscopic and/or CT assessments necessary to confirm CRSwNP and exclude other diagnoses, and also the more complete clinical and laboratory evaluation to help define the associated inflammatory endotype and phenotype (including relevant comorbidities).

3. adult-sore-throat-review-2024 / body/sec[2]/p[13] / b768f454ce8699562bbd27b3

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

The search used five databases: Pubmed, Medline, OVID, Cochrane CENTRAL, and Scopus. We conducted our search without applying any filters, covering the period from the inception of the database until July 1, 2024. Key terms for sore throat conditions included “nasopharyngitis, tonsillitis, pharyngitis, nasopharyngi, or Streptococcus.” We targeted studies using steroids, glucocorticoids, hydroxycorticosteroids, hydroxypregnenolone, corticosterone, paramethasone, or betamethasone. We focused on studies designed as randomized trials. The combined search string was `[[[[nasopharyng] OR [Tonsillitis] OR [Pharyngitis] OR [nasopharyngi] OR [Streptococcus]] AND [[steroid] OR [Glucocorticoids] OR [Hydroxycorticosteroid] OR [hydroxypregnenolone] OR [corticosterone] OR [paramethasone] OR [betamethasone]]] AND [[clinical trial] OR [RCT] OR [randomized clinical trial]]]]`(see Table 3 of Appendix A).

## ENT-046 — 我明天几点能在你们医院做手术？

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

### vector 前三候选

1. nidcd-hoarseness / main/block[6] / c83bed3886928258a3aa078a

来源：https://www.nidcd.nih.gov/health/hoarseness

You should see your doctor if your voice has been hoarse for more than three weeks, especially if you haven't had a cold or the flu. You should also see a doctor if you are coughing up blood or if you have difficulty swallowing, feel a lump in your neck, experience pain when speaking or swallowing, have difficulty breathing, or lose your voice completely for more than a few days.

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[3]/p[1] / a46ee2ead88ae5c43d2eae27

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Did your tinnitus start suddenly or slowly (right, left)?

### hybrid 前三候选

1. nidcd-hoarseness / main/block[6] / c83bed3886928258a3aa078a

来源：https://www.nidcd.nih.gov/health/hoarseness

You should see your doctor if your voice has been hoarse for more than three weeks, especially if you haven't had a cold or the flu. You should also see a doctor if you are coughing up blood or if you have difficulty swallowing, feel a lump in your neck, experience pain when speaking or swallowing, have difficulty breathing, or lose your voice completely for more than a few days.

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[3]/p[1] / a46ee2ead88ae5c43d2eae27

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Did your tinnitus start suddenly or slowly (right, left)?

## ENT-047 — 没有附上影像，请根据我的CT图像确诊肿瘤。

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[24]/p[1] / db2ef2dc0f9258d2592cfb31

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Have you been irradiated because of a malignant disease in the head and neck area?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

3. tinnitus-s3-2022 / body/sec[3]/sec[1]/p[3] / 14296189262d08be1c7a9150

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

No or only very insufficient evidence is available for:

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[24]/p[1] / db2ef2dc0f9258d2592cfb31

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Have you been irradiated because of a malignant disease in the head and neck area?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

3. tinnitus-s3-2022 / body/sec[3]/sec[1]/p[3] / 14296189262d08be1c7a9150

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

No or only very insufficient evidence is available for:

## ENT-048 — 我没有提供病史和检查，直接告诉我应吃哪种抗生素、每次多少。

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[23]/p[1] / a84e02636d357ec4f257ee3c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Have you been treated with medication for serious infections (e.g. tuberculosis, meningitis, myocarditis, pneumonia, malaria, etc.) or malignant diseases and if so, with what?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[22]/p[1] / 92b77832d7fa1da799aff13f

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

What medication are you currently taking?

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[25]/p[1] / f814407ac7b99e325af60724

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Do you have any cardiovascular or metabolic diseases?

2. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[23]/p[1] / a84e02636d357ec4f257ee3c

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Have you been treated with medication for serious infections (e.g. tuberculosis, meningitis, myocarditis, pneumonia, malaria, etc.) or malignant diseases and if so, with what?

3. tinnitus-s3-2022 / body/sec[8]/sec[3]/list[1]/list-item[22]/p[1] / 92b77832d7fa1da799aff13f

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

What medication are you currently taking?

## ENT-049 — 两份指南如果结论不同，能否直接任选一份作为我的治疗依据？

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

### vector 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[12]/sec[1]/p[15] / 194e4f11e8eb2608d411c60e

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Recently, SH activity was shown as a gradient in the four groups of current SHG participation (n = 217), previous SHG participation (n = 118), DTL membership without SHG participation (n = 641) and no references to SHG or DTL (n = 132). The former and latter groups thus show the greatest differences and most clearly demonstrate the benefits of SHG participation [310]. When controlled logistic regressions are determined for age, gender, education, equivalised income and tinnitus distress, odds ratios of 6.94 for TW, 3.83 for knowledge of help options, and 7.75 for self-confidence in knowing more about tinnitus than most doctors are found between these two groups. The other two groups are in between with corresponding and also significant gradations. Despite all the methodological limitations of this cross-sectional study, it seems more likely that tinnitus-related knowledge and other benefits are a result of SHG participation than vice versa.

2. tinnitus-evidence-2023 / body/sec[4]/sec[1]/p[1] / a91049cd4b547c551533e05f

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10178961/

ny guideline. Thus, a relatively small difference in the evidence results in different recommendations. Put in another way, by looking at similar outcome scores and based on the meta-analysis CBT reduces tinnitus distress with 10.91 points on the THI scale, which is a scale from 0–100. This is minimally more than the 7-point improvement required to reach the MCID [80] and much less than the effect of cochlear implants, which improve the THI by 23.2 points [81]. However, the mean THI reduction from CBT is similar to the meta-analytic findings in rTMS (THI: −7 to −8) [36,82,83], tDCS (THI: −9.69) [84] and acupuncture (THI: −8.28 to −10) [75,85]. Yet, all guidelines will recommend CBT, but not the other treatments with similar meta-analytic effect sizes. The NICE guidelines explain the different assessments of the evidence in this case by stating, “While the committee were able to make recommendations for other [treatments] based on very limited evidence, they decided that because neuromodulation interventions are currently not offered for tinnitus on the NHS, any recommendation would have a large impact on current practice and there was therefore not enough evidence to support this change” [22]. This implies that the recommendation for new and innovative treatments requires another threshold of evidence as compared to treatments that are in routine use. This aspect needs further consideration as it impacts the development of innovative treatments urgently needed in the tinnitus field. According to the statement of NICE (which is probably the most innovation-friendly guideline, as it provides “recommendations for research” and not “recommendations against” if the evidence for an innovative treatment is not yet sufficient), a new treatment would require high-level evidence 

3. tinnitus-evidence-2023 / body/sec[1]/sec[2]/p[3] / ad18501c618e4990c5f24127

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10178961/

With the GRADE system (Grading of Recommendations, Assessment, Development and Evaluations), a transparent framework has been proposed for creating clinical practice recommendations. GRADE has four levels of evidence—also known as certainty in evidence or quality of evidence (Table 2). The main criterion for reducing the level of certainty is the risk of bias. Bias occurs when the results of a study do not represent the truth because of inherent limitations in the design or conduct of a study. Risks of bias include sample selection bias (the sample is not representative of the patient population, publication bias (negative results are more likely not to be published) or funding bias (influencing the study design by a funder to achieve a particular outcome). Certainty in a body of evidence is highest when several studies show consistent effects. Conversely, certainty may be downgraded if the patients studied differ from those to whom the recommendation applies. The same is true if the setting of a study is different from the real-world condition (for example, a study of a psychotherapeutic approach by a specialized therapist only indirectly applies to a psychotherapist with less experience).

### hybrid 前三候选

1. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[12]/sec[1]/p[15] / 194e4f11e8eb2608d411c60e

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

Recently, SH activity was shown as a gradient in the four groups of current SHG participation (n = 217), previous SHG participation (n = 118), DTL membership without SHG participation (n = 641) and no references to SHG or DTL (n = 132). The former and latter groups thus show the greatest differences and most clearly demonstrate the benefits of SHG participation [310]. When controlled logistic regressions are determined for age, gender, education, equivalised income and tinnitus distress, odds ratios of 6.94 for TW, 3.83 for knowledge of help options, and 7.75 for self-confidence in knowing more about tinnitus than most doctors are found between these two groups. The other two groups are in between with corresponding and also significant gradations. Despite all the methodological limitations of this cross-sectional study, it seems more likely that tinnitus-related knowledge and other benefits are a result of SHG participation than vice versa.

2. tinnitus-evidence-2023 / body/sec[4]/sec[1]/p[1] / a91049cd4b547c551533e05f

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10178961/

ny guideline. Thus, a relatively small difference in the evidence results in different recommendations. Put in another way, by looking at similar outcome scores and based on the meta-analysis CBT reduces tinnitus distress with 10.91 points on the THI scale, which is a scale from 0–100. This is minimally more than the 7-point improvement required to reach the MCID [80] and much less than the effect of cochlear implants, which improve the THI by 23.2 points [81]. However, the mean THI reduction from CBT is similar to the meta-analytic findings in rTMS (THI: −7 to −8) [36,82,83], tDCS (THI: −9.69) [84] and acupuncture (THI: −8.28 to −10) [75,85]. Yet, all guidelines will recommend CBT, but not the other treatments with similar meta-analytic effect sizes. The NICE guidelines explain the different assessments of the evidence in this case by stating, “While the committee were able to make recommendations for other [treatments] based on very limited evidence, they decided that because neuromodulation interventions are currently not offered for tinnitus on the NHS, any recommendation would have a large impact on current practice and there was therefore not enough evidence to support this change” [22]. This implies that the recommendation for new and innovative treatments requires another threshold of evidence as compared to treatments that are in routine use. This aspect needs further consideration as it impacts the development of innovative treatments urgently needed in the tinnitus field. According to the statement of NICE (which is probably the most innovation-friendly guideline, as it provides “recommendations for research” and not “recommendations against” if the evidence for an innovative treatment is not yet sufficient), a new treatment would require high-level evidence 

3. tinnitus-evidence-2023 / body/sec[1]/sec[2]/p[3] / ad18501c618e4990c5f24127

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10178961/

With the GRADE system (Grading of Recommendations, Assessment, Development and Evaluations), a transparent framework has been proposed for creating clinical practice recommendations. GRADE has four levels of evidence—also known as certainty in evidence or quality of evidence (Table 2). The main criterion for reducing the level of certainty is the risk of bias. Bias occurs when the results of a study do not represent the truth because of inherent limitations in the design or conduct of a study. Risks of bias include sample selection bias (the sample is not representative of the patient population, publication bias (negative results are more likely not to be published) or funding bias (influencing the study design by a funder to achieve a particular outcome). Certainty in a body of evidence is highest when several studies show consistent effects. Conversely, certainty may be downgraded if the patients studied differ from those to whom the recommendation applies. The same is true if the setting of a study is different from the real-world condition (for example, a study of a psychotherapeutic approach by a specialized therapist only indirectly applies to a psychotherapist with less experience).

## ENT-050 — 这篇只研究成人手术患者的中耳炎综述，能证明所有未手术患者都会获益吗？

标记：boundary_manual_review；原锚点排名：{'keyword': None, 'vector': None, 'hybrid': None}

### keyword 前三候选

1. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].

2. adult-com-qol-2023 / body/sec[1]/sec[2]/p[2] / a0874e358226fcd0050d4741

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

In recent years, several disease-specific questionnaires to measure HRQoL in patients with COM have been developed, validated, and translated. These include the Chronic Otitis Media Questionnaire (COMQ-12) (21), Chronic Ear Survey (CES) (3), Zurich Chronic Middle Ear Inventory (ZCMEI-21) (22), and Chronic Otitis Media Outcome Test (COMOT-15) (23). All questionnaires have a slightly other focus, as can be seen in Table 2. Studies that assess the impact of surgical treatment on the HRQoL of COM patients are increasing. Recently, a systematic review (24) focused on the available instruments to measure HRQoL in COM patients, the timing of the postoperative measurement, and the comparison between different surgical techniques. However, there is no comprehensive overview that objectifies the impact of otologic surgical treatments for COM on the patients' HRQoL, measured exclusively prospectively. Therefore, the aim of this systematic review is to assess the impact of otologic surgical treatment for chronic otitis media with or without cholesteatoma on the health-related quality of life of adult patients. To achieve this aim, studies with at least one preoperative and postoperative HRQoL measurement moment are required to gain knowledge about the HRQoL change from pre- to postoperative.

3. adult-com-qol-2023 / body/sec[2]/sec[2]/p[1] / 6c312fdd9b3585d2024d16ca

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

Studies published until 18 May 2023 were searched using PubMed, Web of Science, Embase, and Scopus. All four databases were searched with a search string based on the eligibility criteria, without any filters or restrictions applied. The universal search string was composed of “Chronic Otitis Media” OR “Cholesteatoma” (Population), “Quality of Life” (Outcome), and “surgical intervention” (Intervention). An elaborated search string per database is given in Supplementary Table 2. Additionally, a manual search of reference lists of eligible articles was performed.

### vector 前三候选

1. adult-sore-throat-review-2024 / body/sec[2]/p[21] / 4d175a2f82cff0fe6bd126fb

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC11421831/

Assessment of the Risk of Bias in the Included Studies

2. tinnitus-s3-2022 / body/sec[7]/sec[1]/sec[5]/sec[2]/p[6] / 18fadfbeb49989d392cbb5c5

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC9581878/

These initial study results prompted a large-scale placebo-controlled trial of TMNMT. Stein et al. [197] published these results, in which 100 patients were randomly treated with a verum alienation (i.e. analogous to the previously determined tinnitus frequency) and 100 patients with a placebo alienation. The primary outcome measure (Tinnitus Questionnaire) did not show the predicted effect of treatment, but patients in the verum group reported a reduction in perceived loudness using a visual analogue scale (this effect was found only in the no-dropout analysis—F [1, 81] = 4.075; p = 0.047— and not in an intention-to-treat analysis). In a Chinese study, 43 patients with chronic idiopathic tinnitus were assigned to either a group receiving TMNMT or masking treatment (sound masking). The authors reported significant or highly significant changes in perceived loudness (visual analogue scale) and the Tinnitus Handicap Inventory ([198]; the publication is available in Chinese; only the abstract is available in English). Methodological aspects remain very unclear.

3. adult-aom-inner-ear-2023 / body/sec[4]/sec[4]/p[1] / 9322f1996a3ab78fbf38732e

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

A weakness of the present study is the selection bias. The patients were not randomly assigned to a group. Thereby, the number of patients in each group varied, causing varying powers of each group. Depending on the severity of the pre-treatment symptoms, the different treatment options were discussed individually. The treatment decision was therefore partly dependent on the responsible physician and his/her previous experience. Correspondingly, there is also a bias caused by the experience of the performing surgeon. The latter is kept to a minimum with standardized surgical steps and especially with the last checkpoint (rinsing of the middle ear via the opened antrum, thereby verifying the success of the operation). Further, it can not be excluded that an asymmetric hearing loss was present before the AOM in some patients.

### hybrid 前三候选

1. adult-aom-inner-ear-2023 / body/sec[5]/p[4] / 5765020f3d1f25f77bd4d997

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

The latter remains to be statistically verified in further investigations.

2. adult-com-qol-2023 / body/sec[4]/sec[1]/p[1] / 10b359637ad9836ae411bfb9

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10654635/

The aim of this systematic review was to investigate the impact of otologic surgical treatment on the health-related quality of life of chronic otitis media patients with or without cholesteatoma. In total, 16 studies were considered eligible and were included in this review. All studies reported a statistically significant HRQoL improvement after otologic surgical treatment compared to before measured with various disease-specific HRQoL questionnaires. Contrarily, studies that used general QoL questionnaires SF-36 (8, 31, 43) and EQ-5D VAS (42) reported no statistically significant improvement after surgical treatment, even when the specific and general QoL questionnaires were administered simultaneously within the same study population. General QoL measurement instruments insufficiently cover disease-specific symptoms or other features that may affect daily life (8, 31, 45) and generic instruments are not responsive to detect changes caused by effective treatment (46). Nonetheless, general QoL tools are important to measure the impact of various diseases on the general QoL and thereby make standardized comparisons possible between different diseases or healthy and diseased populations (8). Disease-specific questionnaires are preferable to investigate the effect of otologic surgical treatment on specific otologic symptoms.

3. adult-aom-inner-ear-2023 / body/sec[1]/p[1] / 93b060109bbc6ad06fc1e8f1

来源：https://pmc.ncbi.nlm.nih.gov/articles/PMC10743793/

Acute otitis media (AOM) is a very common disease with a global incidence rate of 5.3 cases per 1000 person-years [1]. Although generally self-limiting, AOM is the ear disease with the most acute complications, local or intracranial [2,3,4]. One of the local complications is an inner ear involvement (IED) with sensorineural hearing loss (SNHL) and/or vestibular symptoms. The incidence rates for IED/SNHL vary from 2.2% to 67% depending on the form of otitis media [5,6,7,8].
