# Why is this repository here?

## Purposes

There are 73,000 cataloged code repositories within Throughput. These are associated with various databases, based on scraping that was done in other Throughput repositories. The challenge, is that when a user searches for repositories that are associated with a database they may find a large number of resources that aren't helpful in a "cookbook" sense.

To help us we can look at some code repositories and see if we can categorize them. We use the following call directly against the database:

```cypher
MATCH (tyc:TYPE {type: 'schema:CodeRepository'})
MATCH (tyb:TYPE {type: 'schema:DataCatalog'})
MATCH (r:OBJECT)-[:isType]-(tyc)
  WHERE exists(r.name)
WITH r, tyb
MATCH (d:OBJECT)-[:isType]-(tyb)
MATCH (d)<-[:Target]-(:ANNOTATION)-[:Target]->(r)
  WITH DISTINCT r, COLLECT(d) AS dbs, rand() AS number
RETURN dbs[0].name, r.name, r.url
ORDER BY number
LIMIT 100
```

This returns the set of repositories with `name` properties that are connected directly to a database, because some repositories can be connected to many databases, be only choose one database per repository and we add a random integer to the result set (`rand() as number`) to ensure that we get a distinct subset (`n = 100`) of all the results.

Broadly, we're looking at a few categories:

### Education

Elements of the repository serve to house educational resources. This may include:

- Class assignment 
- Class notes
- Documentation of use
- Resources
- Tutorial

### Analysis

Elements of this repository serve as the primary analysis for a workflow.

- Comparative data use/reuse
- Integrative data use/reuse 
- Database API use


### Archiving

There is data that is stored in this repository.

### Informational

This is primarily things like websites.

- Scraping database registries 

## Repositories and Their Classifications

Things can have multiple categories.

DB                                                            | Repo                                                                                                            | Repo Class | Notes
------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ---------- | -----
DSpace@MIT                                                    | [ziyaxu/JAZWUX](https://github.com/ziyaxu/JAZWUX)                                                               |       Education - Documentation of use   | One article in DB (3x) for mathmatical methods they use for an XY printer to draw raster images they created while attending LEAP@CMU. . 
DRYAD                                                         | [hsf-training/analysis-essentials](https://github.com/hsf-training/analysis-essentials)                         |    Education - Resources; Informational        |Links to Dryad homepage as an example of open science. 
European Social Survey                                        | [artemkramov/python-filter](https://github.com/artemkramov/python-filter)                                       |    **Informational and/or Archiving?**     |Data for the project consists of articles and their metadata including links to EES data and the EES database. Some documentation in Ukrainian.  
European Election Database                                    | [CINERGI/scraper](https://github.com/CINERGI/scraper)                                                           |   Informational - Scraping database registries        |Scraped Databib which included European Election Database. 
UNdata                                                        | [chinapedia/wikipedia.zh](https://github.com/chinapedia/wikipedia.zh)                                           |    Unable to categorize.     |Documentation and code in Mandarin. 
EUDAT                                                         | [zenodo/zenodo-docs-user](https://github.com/zenodo/zenodo-docs-user)                                           |  Informational          |Link to EUDAT as a partner of Zenodo. 
NDSF Data Portal                                              | [CINERGI/scraper](https://github.com/CINERGI/scraper)                                                           |    Informational - Scraping database registries         |Scraped Databib which included NDSF Data Portal.
dictybase                                                     | [adristoteles/workinCopyMay](https://github.com/adristoteles/workinCopyMay)                                     |      Unable to categorize.     |Lack of documentation. 
NCBI Taxonomy                                                 | [Ensembl/public-plugins](https://github.com/Ensembl/public-plugins)                                             |            | Plugins for Ensembl Genome Browser. 
Global Land Cover Facility                                    | [ocftw/OpenFoundry-Archive](https://github.com/ocftw/OpenFoundry-Archive)                                       |            |
DEIMS-SDR                                                     | [ajpelu/nota_dataRepositories](https://github.com/ajpelu/nota_dataRepositories)                                 |Informational          |  Article reviewing and citing different data repository options in Spanish. 
Center for Operational Oceanographic Products and Services    | [just6979/tide-catcher](https://github.com/just6979/tide-catcher)                                               |      **Needs new category**      |Use Center for Operational Oceanographic Products and Services tide data for an application. 
DataONE                                                       | [au-research/ARDC-23-things](https://github.com/au-research/ARDC-23-things)                                     |        Education - Resources; Informational   |Links to DataONE data management plan resources. 
OpenML                                                        | [Alex-Samarkin/untitled13](https://github.com/Alex-Samarkin/untitled13)                                         |   Unable to categorize.         |Some documentation in Ukrnanian. 
Synapse                                                       | [smc-rna-challenge/jeltje-9605360](https://github.com/smc-rna-challenge/jeltje-9605360)                         |        Analysis - Integrative data use; Educational - Tutorial     |This is a CWL workflow which was submitted to the SMC-RNA Challenge in the isoform quantification category. Example and reference data files are stored on Synapse and are defined in synapse_inputs.json.
GEON                                                          | [GoldRenard/AllegroROM_4.4.2_mt6589](https://github.com/GoldRenard/AllegroROM_4.4.2_mt6589)                     |     Unable to categorize.       | This may be a false positive of GEON. 
BioPortal                                                     | [yannrivault/queryMed](https://github.com/yannrivault/queryMed)                                                 |     **Database API use**       |Use API from BioPortal and SIFR in their package to create pharmacological and medical annotations
BeeBase                                                       | [CINERGI/TextTeaserOnline](https://github.com/CINERGI/TextTeaserOnline)                                         |    Informational - Scraping database registries        |Scraped hydro10 which included BeeBase.
Data.gov.au                                                   | [stainsby/dga-sync](https://github.com/stainsby/dga-sync)                                                       |       Education - Tutorial & **Needs new category**     |**Tool syncs datsets from data.gov.au using JSON metadata stored on data.gov.au for each each dataset** and repo has tutorial of tool using data.gov.au data. 
SILVA                                                         | [JavierRamiroGarcia/NG-Tax](https://github.com/JavierRamiroGarcia/NG-Tax)                                       |  **Unsure - Needs new catoregy**       |Download Silva database and taxonomy during installation of pipeline and used within pipeline to generate the customized databases adapted to NG-Tax by in-silico PCR.
Association of Religion Data Archives                         | [NikulinVs/inv_index_lab](https://github.com/NikulinVs/inv_index_lab)                                           |      Analysis; Archiving      |Cites to the dataset of each/country state involved in analysis. Adds actual data in textual form in .txt file. 
GiardiaDB                                                     | [bio-tools/content](https://github.com/bio-tools/content)                                                       |      Informational      |Central place for the exchange of tool metadata for multiple projects, including GiardiaDB.
Internet Archive                                              | [sato-takuya/sample_app](https://github.com/sato-takuya/sample_app)                                             |       Unable to categorize.    |Documentation in Japanese. 
The Human Protein Atlas                                       | [jay-feng/CORD-project](https://github.com/jay-feng/CORD-project)                                               |  **Informational and/or archiving**          |Data for the project consist of articles/metadata. This includes links to Human Protein Atlas data and database.
MaizeGDB                                                      | [misscindz/Bioinformatics-Codes](https://github.com/misscindz/Bioinformatics-Codes)                             |   Education - Class assignment; Informational          | Class assignments dataset with abbreviations for cross-referenced databases including abbreviation, database, genric-url, url_syntax, url-example, etc. 
UK Data Service                                               | [digipres/digipres.github.io](https://github.com/digipres/digipres.github.io)                                   |      Informational      |Linking to UK Data Service for tips on managing data.
KONECT                                                        | [YupingLu/biclique](https://github.com/YupingLu/biclique)                                                       |     Education - Tutorial       |Test datasets downloaded from Konect.Maximal Biclique Enumeration in Bipartite Graphs. A tool for enumerating maximal complete bipartite graphs. **KONECT is no longer hosted by the Institute of Web Science and Technologies.**  
National Archives                                             | [usnationalarchives/digital-preservation](https://github.com/usnationalarchives/digital-preservation)           | Informational           |The National Archives and Records Administration is releasing its Digital Preservation Framework, which consists of a Risk and Prioritization Matrix and File Format Preservation Action Plans.
Worldpop                                                      | [elifesciences/elife-articles](https://github.com/elifesciences/elife-articles)                                 |  Informational          |Github repository is xml of elife articles. Some of the xml files of elife articles contained links to Worldpop homepage.   
FANTOM                                                        | [Hypercubed/fantom-cat](https://github.com/Hypercubed/fantom-cat)                                               |   Analysis - Integrative data reuse        |Using FANTOM5 Cap Analysis of Gene Expression (CAGE) data the team integrated multiple transcript collections to generate a comprehensive catalog of 23,887 high-confidence 5’ complete human lncRNA genes and their expression profiles across 1,829 samples from the major human primary cell types and tissues.
NSF Arctic Data Center                                        | [climate-mirror/datasets](https://github.com/climate-mirror/datasets)                                           |            |
Human Metabolome Database                                     | [chinapedia/wikipedia.zh.mediawiki](https://github.com/chinapedia/wikipedia.zh.mediawiki)                       |            |
London Datastore                                              | [TAnarchy/EngineGroupApplication](https://github.com/TAnarchy/EngineGroupApplication)                           |            |
PhytoPath                                                     | [santex/micro-biological](https://github.com/santex/micro-biological)                                           |            |
EMBL-EBI                                                      | [ens-lgil/PGS_Catalog](https://github.com/ens-lgil/PGS_Catalog)                                                 |            |
Synapse                                                       | [leem42/portals](https://github.com/leem42/portals)                                                             |            |
Universal PBM Resource for Oligonucleotide Binding Evaluation | [james-chuang/dissertation](https://github.com/james-chuang/dissertation)                                       |            |
Plant Genomics and Phenomics Research Data Repository         | [bio-tools/content.jsonld](https://github.com/bio-tools/content.jsonld)                                         |            |
European Nucleotide Archive                                   | [zorbax/ottotype](https://github.com/zorbax/ottotype)                                                           |            |
Worldpop                                                      | [xiaoyaoziyao/msc_project](https://github.com/xiaoyaoziyao/msc_project)                                         |            |
HomoMINT                                                      | [smangul1/good.software](https://github.com/smangul1/good.software)                                             |            |
Spiral                                                        | [karansinghneu/CS-6200-IR](https://github.com/karansinghneu/CS-6200-IR)                                         |            |
Eurostat                                                      | [cran/convergEU](https://github.com/cran/convergEU)                                                             |            |
CERN Open Data                                                | [HariKumarValluru/100_Days_of_ML_Code](https://github.com/HariKumarValluru/100_Days_of_ML_Code)                 |            |
GenBank                                                       | [xiaoyaoziyao/msc_project](https://github.com/xiaoyaoziyao/msc_project)                                         |            |
Academic Torrents                                             | [arxaqapi/lightsite](https://github.com/arxaqapi/lightsite)                                                     |            |
European Data Portal                                          | [weirdnose/data](https://github.com/weirdnose/data)                                                             |            |
Harvard Dataverse                                             | [annerosenisser/banner](https://github.com/annerosenisser/banner)                                               |            |
Climate Data Online                                           | [millerhoo/journey2-new-data-lake](https://github.com/millerhoo/journey2-new-data-lake)                         |            |
Community Data Portal                                         | [NCAR/dash-opensky-prod](https://github.com/NCAR/dash-opensky-prod)                                             |            |
Water Survey of Canada                                        | [ECCC-CCCS/climate-data-extraction-tool](https://github.com/ECCC-CCCS/climate-data-extraction-tool)             |            |
The Paleobiology Database                                     | [LaurentFranckx/auto_dat_col](https://github.com/LaurentFranckx/auto_dat_col)                                   |            |
DRYAD                                                         | [sharonWANGS/Spatio-temporal-data](https://github.com/sharonWANGS/Spatio-temporal-data)                         |            |
Alaska Native Language Archive                                | [glottolog/glottolog](https://github.com/glottolog/glottolog)                                                   |            |
DrugBank                                                      | [yhao-compbio/tox_data](https://github.com/yhao-compbio/tox_data)                                               |            |
GENCODE                                                       | [HumanCellAtlas/skylab](https://github.com/HumanCellAtlas/skylab)                                               |            |
Comprehensive Large Array-data Stewardship System             | [geopaparazzi/libjsqlite-spatialite-android](https://github.com/geopaparazzi/libjsqlite-spatialite-android)     |            |
KBase                                                         | [cshenry/fba_tools](https://github.com/cshenry/fba_tools)                                                       |            |
ArrayExpress                                                  | [BioContainers/tools-metadata](https://github.com/BioContainers/tools-metadata)                                 |            |
Ensembl                                                       | [kevinrue/hancock2018](https://github.com/kevinrue/hancock2018)                                                 |            |
Worldpop                                                      | [rostro36/ML4HC-KaggleTask](https://github.com/rostro36/ML4HC-KaggleTask)                                       |            |
Kaggle                                                        | [OpenTwinCities/open-data-getting-started](https://github.com/OpenTwinCities/open-data-getting-started)         |            |
PharmGKB                                                      | [bio-tools/content](https://github.com/bio-tools/content)                                                       |            |
figshare                                                      | [olivernash/collective-analytics](https://github.com/olivernash/collective-analytics)                           |            |
OpenKIM                                                       | [grahamstockton/silent-amp](https://github.com/grahamstockton/silent-amp)                                       |            |
Harvard Dataverse                                             | [the-isf-academy/unit-1-project-teaching-team](https://github.com/the-isf-academy/unit-1-project-teaching-team) |            |
CRAWDAD                                                       | [joehonig/gps2net](https://github.com/joehonig/gps2net)                                                         |            |
Behavioral Risk Factor Surveillance System                    | [chuyingma/260_final_project](https://github.com/chuyingma/260_final_project)                                   |            |
Academic Torrents                                             | [Zippen-Huang/self-driving-car](https://github.com/Zippen-Huang/self-driving-car)                               |            |
Censusindia                                                   | [nishsak96/WT_n](https://github.com/nishsak96/WT_n)                                                             |            |
Kaggle                                                        | [cloudmesh-book/book-latex-2018](https://github.com/cloudmesh-book/book-latex-2018)                             |            |
American National Election Studies                            | [frankjin333/PythonCryptoTrader](https://github.com/frankjin333/PythonCryptoTrader)                             |            |
Kaggle                                                        | [Wchino/jeykll-test](https://github.com/Wchino/jeykll-test)                                                     |            |
Plant Transcription Factor Database                           | [ShantanuNair/OUPDownloader](https://github.com/ShantanuNair/OUPDownloader)                                     |            |
U.S. Energy Information Administration                        | [ProjectDrawdown/solutions](https://github.com/ProjectDrawdown/solutions)                                       |            |
PRO-ACT                                                       | [cghoehne/transport-uhi-phx](https://github.com/cghoehne/transport-uhi-phx)                                     |            |
Humanitarian Data Exchange                                    | [Chaos-Tech-Corp/covidist.com](https://github.com/Chaos-Tech-Corp/covidist.com)                                 |            |
TopFIND                                                       | [andrawaag/WikiPathwaysRDFConversion](https://github.com/andrawaag/WikiPathwaysRDFConversion)                   |            |
The European Database of Seismogenic Faults                   | [CelsoReyes/zmap7](https://github.com/CelsoReyes/zmap7)                                                         |            |
Internet Archive                                              | [jakeyoung-517/CSE373](https://github.com/jakeyoung-517/CSE373)                                                 |            |
IDEAS                                                         | [littlewen97/CrawlerofEconomists](https://github.com/littlewen97/CrawlerofEconomists)                           |            |
ORegAnno                                                      | [ShantanuNair/OUPDownloader](https://github.com/ShantanuNair/OUPDownloader)                                     |            |
SILVA                                                         | [HCBravoLab/silva128.1MgDb](https://github.com/HCBravoLab/silva128.1MgDb)                                       |            |
MetaboLights                                                  | [phnmnl/container-galaxy-k8s-runtime](https://github.com/phnmnl/container-galaxy-k8s-runtime)                   |            |
European Nucleotide Archive                                   | [mianlee/Fu-s-test](https://github.com/mianlee/Fu-s-test)                                                       |            |
GenBank                                                       | [Zarete/Blob](https://github.com/Zarete/Blob)                                                                   |            |
Encyclopedia of Life                                          | [ropensci/rmangal](https://github.com/ropensci/rmangal)                                                         |            |
NASA Exoplanet Archive                                        | [evan-lee-2018/ml](https://github.com/evan-lee-2018/ml)                                                         |            |
DEG                                                           | [ncchung/bioinformatics](https://github.com/ncchung/bioinformatics)                                             |            |
OLAC                                                          | [ualbertalib/metadata](https://github.com/ualbertalib/metadata)                                                 |            |
IMEx                                                          | [ShantanuNair/OUPDownloader](https://github.com/ShantanuNair/OUPDownloader)                                     |            |
TopFIND                                                       | [haidertom/WikipediaCategorization](https://github.com/haidertom/WikipediaCategorization)                       |            |
Human Metabolome Database                                     | [elifesciences/elife-article-xml](https://github.com/elifesciences/elife-article-xml)                           |            |
Internet Archive                                              | [eellak/gsoc2019-3gm](https://github.com/eellak/gsoc2019-3gm)                                                   |            |
Kaggle                                                        | [Drvinc/R-beginner](https://github.com/Drvinc/R-beginner)                                                       |            |
UniProtKB                                                     | [diamond0411/ndexncipidloader](https://github.com/diamond0411/ndexncipidloader)                                 |            |
NetPath                                                       | [ayadlin/Capstone](https://github.com/ayadlin/Capstone)                                                         |            |
Cystic Fibrosis Mutation Database                             | [saetre/biocreative_data](https://github.com/saetre/biocreative_data)                                           |            |
Alzforum                                                      | [bdhsu/bdhsu.github.io](https://github.com/bdhsu/bdhsu.github.io)                                               |            |
MetaCyc                                                       | [datapplab/SBGNhub](https://github.com/datapplab/SBGNhub) \                                                     | \          | \
