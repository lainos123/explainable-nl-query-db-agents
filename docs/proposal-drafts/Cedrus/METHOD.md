# Methods that have been used by other projects

(By Cedrus Dang @UWA)

**CONTENTS**

- [PART 1: TEXT-TO-SQL METHODS ON SPIDER DATASET](#part-1-text-to-sql-methods-on-spider-dataset)
  - [Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation (2023)](#1-text-to-sql-empowered-by-large-language-models-a-benchmark-evaluation-2023spider-ver1)
  - [DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction (2023)](#din-sql-decomposed-in-context-learning-of-text-to-sql-with-self-correction-2023spider-ver1)
  - [Other options on Spider 2.0](#other-options-on-spider-20)
- [PART 2: AGENTIC AI DESIGN](#part-2-agentic-ai-design)
  - [Demonstration of DB-GPT](#1-demonstration-of-db-gpt-next-generation-data-interaction-system-empowered-by-large-language-models)
  - [DAgent: Relational Database-Driven Data Analysis Report Generation Agent](#2-dagent-a-relational-database-driven-data-analysis-report-generation-agent)
- [PART 3: Interactive Reasoning STEPS in Agentic AI](#part-3-interactive-reasoning-steps-in-agentic-ai)
  - [AI chains: Transparent and controllable Human-AI interaction](#1-ai-chains-transparent-and-controllable-human-ai-interaction-by-chaining-large-language-model-prompts)
  - [Interactive Reasoning: Visualizing and Controlling Chain-of-Thought Reasoning](#2-interactive-reasoning-visualizing-and-controlling-chain-of-thought-reasoning-in-large-language-models)
- [PART 4: EVALUATION METRICS](#part-4-evaluation-metrics)
  - [Spider 1: Original Dataset](#spider-1-the-original-spider-dataset)
  - [Spider 2: Extended Dataset](#spider-2-an-extended-version-of-the-spider-dataset)
  - [Evaluation Protocols and Best Practices](#how-to-use-the-benchmarks)

## PART 1: TEXT-TO-SQL METHODS ON SPIDER DATASET

### 1. Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation (2023)(Spider ver1)

IEEE: D. Gao et al., “Text-to-SQL empowered by large language models: a benchmark evaluation,” arXiv.org, Aug. 29, 2023. https://arxiv.org/abs/2308.15363

- Score: Spider Ver1 86.6%

***Abstract***
"Large language models (LLMs) have emerged as a new paradigm for Text-to-SQL task. However, the absence of a systematical benchmark inhibits the development of designing effective, efficient and economic LLM-based Text-to-SQL solutions. To address this challenge, in this paper, we first conduct a systematical and extensive comparison over existing prompt engineering methods, including question representation, example selection and example organization, and with these experimental results, we elaborate their pros and cons. Based on these findings, we propose a new integrated solution, named DAIL-SQL, which refreshes the Spider leaderboard with 86.6% execution accuracy and sets a new bar. To explore the potential of open-source LLM, we investigate them in various scenarios, and further enhance their performance with supervised fine-tuning. Our explorations highlight open-source LLMs' potential in Text-to-SQL, as well as the advantages and disadvantages of the supervised fine-tuning. Additionally, towards an efficient and economic LLM-based Text-to-SQL solution, we emphasize the token efficiency in prompt engineering and compare the prior studies under this metric. We hope that our work provides a deeper understanding of Text-to-SQL with LLMs, and inspires further investigations and broad applications."

***Methods:***

- Purpose: Evaluate how recent large language models (LLMs) perform on Text-to-SQL tasks across multiple benchmarks, comparing with prior systems.

- Benchmarks Used: Spider, BIRD, WikiSQL, and others with varying schema complexity and query difficulty.

- Using SOTA (State Of The Art) models: GPT-4 GPT-3.5-TURBO TEXT-DAVINCI-003 Vicuna-33B

- Techniques: Zero shots to few shots (Max=5), the results that Zero shots perfomance badly (10-20% lower than few shots)

=> This mean that prompting engineering is very important, margin is 10-20% for each level.

***Explain:***

Here is the explanation again with concrete samples:

**Zero-shot**

* **Definition**: No example in the prompt. Only the task instruction and the target question.
* **Prompt**:

```
Translate the following question into SQL:
Q: List all employee names hired after 2020.
```

* Model must generate SQL without seeing any example.

**1-shot**

* **Definition**: One example question–SQL pair is given before the target question.
* **Prompt**:

```
Q: Show the names of all customers from France.
SQL: SELECT name FROM customers WHERE country = 'France';

Q: List all employee names hired after 2020.
```

* Model uses the single example as guidance.

**Random 1-shot**

* **Definition**: One example is selected at random from the dataset.
* **Prompt**:

```
Q: What is the maximum order amount?
SQL: SELECT MAX(amount) FROM orders;

Q: List all employee names hired after 2020.
```

* The example may be unrelated to the target question.

**Question Similarity selection**

* **Definition**: Use retrieval (e.g., cosine similarity of embeddings) to find the most semantically similar question.
* **Prompt**:

```
Q: Show the names of employees hired in 2019.
SQL: SELECT name FROM employees WHERE hire_year = 2019;

Q: List all employee names hired after 2020.
```

* Retrieved example is semantically close to target query.

**Masked Question Similarity selection**

* **Definition**: Similar to above, but schema-specific terms are masked before similarity calculation.

* **Before masking**:
  
  * Q1: "Show the names of employees hired in 2019."
  * Q2: "Show the titles of books published in 2019."

* **After masking**: Both become "Show the X of Y in 2019."

* Ensures retrieval is based on query intent, not just shared schema words.

**DAIL selection**

* **Definition**: Database-Aware Information Level selection. Uses both semantic similarity and schema context for retrieval.
* **Prompt**:

```
Q: Show the average salary of engineers.
SQL: SELECT AVG(salary) FROM employees WHERE job_title = 'Engineer';

Q: List all employee names hired after 2020.
```

* Example chosen is relevant both in meaning and in schema overlap (same `employees` table).

**Upper Limit**

* **Definition**: Oracle choice — pick the example that would produce the highest possible accuracy for the specific test question.
* **Prompt** (chosen after knowing test case answer):

```
Q: List all employees hired after 2015.
SQL: SELECT name FROM employees WHERE hire_date > '2015-12-31';

Q: List all employee names hired after 2020.
```

* This is only for theoretical ceiling measurement, not realistic in deployment.

***Mention in the paper:***
    - Text-to-SQL prompt engineering needs a systematic study.
    - The potential of open-source LLMs is underexplored.
    - Prompt efficiency remains a challenging open question.
    - Do mention about EM (Exact Set Match Accuracy) & EX (Execution Accuracy), when EX > EM significantly (>30%). This is out of our scope because we only care about the final result, not the SQL code matching.
    - “Across all benchmarks, LLMs still exhibit weaknesses in schema linking—accurately mapping question terms to the correct tables and columns—especially in large or unfamiliar schemas. Complex joins and nested queries are another consistent challenge, as these require multi-step reasoning over multiple tables and conditions.
    - Supervised Fine-Tuning (SFT) : “Supervised fine-tuning (SFT) has been the dominant paradigm for training Text-to-SQL parsers before the rise of large language models. SFT can tailor a model to a specific domain or benchmark by learning the schema structure, naming conventions, and common query patterns directly from annotated pairs of natural language questions and SQL. This often results in higher stability on complex queries and less reliance on long prompts during inference. However, SFT requires large-scale, high-quality labeled data, which can be costly to collect, and models fine-tuned in this way tend to overfit to the training schema, performing poorly when faced with unseen databases or domains. Moreover, training large models from scratch or even fine-tuning them demands substantial computational resources, making SFT impractical for proprietary closed-source LLMs such as GPT-4. In contrast, prompt-based methods can adapt to new databases and domains simply by changing the examples or instructions, though they may suffer from higher token costs and latency due to longer prompts.”

***FINAL RECOMMEND FROM THIS PAPER***

- Prompting Engineering is a must to achieve high performance.
- We should not use Upper Limit because it is not realistic as we cannot know the answer beforehand (It mean low AI maturity).
- We should test on all other methods, as they can improve performance significantly when they are more detailed, but it also increases the requirements. This may create overfitting to the dataset, making the solution less generalizable and requiring more resources (human or AI) to learn about the dataset.
- However, we can also raise the question that can we leverage this overfitting instead of avoid it, and create a pipeline that will prepare new knowledge using AI: Pre learn about the data in small or full scope before letting the users to use the data when a new dataset injected
  into the system. This should be consider follow what is our real target: low resources usage or high performance system?
- Schema linking and Complex joins / nested queries are two major challenges that prevent them to achieve high performance.
- Supervised Fine-Tuning (SFT) is not practical for closed-source LLMs like GPT-4, but it can be used for open-source models (In long-term projects only, because it could take few days to weeks for 1B Model fine-tuning on HPC machines, which only 1% with the 1xx parameters SOTA Models).

### DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction (2023)(Spider ver1)

IEEE: M. Pourreza and D. Rafiei, “DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction,” arXiv.org, Apr. 21, 2023. https://arxiv.org/abs/2304.11015

- Score: Spider Ver1 85.3%

***Abstract***

"There is currently a significant gap between the performance of fine-tuned models and prompting approaches using Large Language Models (LLMs) on the challenging task of text-to-SQL, as evaluated on datasets such as Spider. To improve the performance of LLMs in the reasoning process, we study how decomposing the task into smaller sub-tasks can be effective. In particular, we show that breaking down the generation problem into sub-problems and feeding the solutions of those sub-problems into LLMs can be an effective approach for significantly improving their performance. Our experiments with three LLMs show that this approach consistently improves their simple few-shot performance by roughly 10%, pushing the accuracy of LLMs towards SOTA or surpassing it. On the holdout test set of Spider, the SOTA, in terms of execution accuracy, was 79.9 and the new SOTA at the time of this writing using our approach is 85.3. Our approach with in-context learning beats many heavily fine-tuned models by at least 5%. Additionally, when evaluated on the BIRD benchmark, our approach achieved an execution accuracy of 55.9%, setting a new SOTA on its holdout test set.
"

***Methods:***

1. **Decomposed In-Context Learning**: The core idea is to break down the text-to-SQL generation task into smaller, manageable sub-tasks. This allows the model to focus on one aspect of the problem at a time, potentially leading to better overall performance.

2. **Self-Correction Mechanism**: Incorporating a self-correction mechanism enables the model to iteratively refine its outputs by comparing them against expected results and making necessary adjustments.

3. **In-Context Learning**: Leveraging in-context learning allows the model to utilize examples and context provided during the prompting phase, improving its ability to generate accurate SQL queries.

The flow of the method is as follows:

1. Input question is processed by the Schema Linking Module to identify relevant schema elements.
2. The Query Classification & Decomposition Module analyzes the query complexity and breaks it down into sub-problems.
3. The SQL Generation Module generates SQL queries based on the identified schema and decomposed sub-problems.
4. The Self-Correction Module iteratively refines the generated SQL queries to fix minor errors.

***Details and Explanation:***

**1. Schema Linking Module**

* **Goal**: Map words in the question to the correct database tables, columns, and possible cell values.

* **Prompt design**:
  
  * Few-shot examples from Spider training set.
  * “Let’s think step by step” chain-of-thought style.
  * Output lists relevant schema elements and foreign keys.

* **Why**: Schema linking was the top source of failure in basic few-shot prompting.

**2. Query Classification & Decomposition Module**

* **Goal**: Identify query complexity and break it into sub-problems.

* **Classification**:
  
  * **Easy**: Single table, no join, no sub-query.
  * **Non-nested complex**: JOINs but no sub-query.
  * **Nested complex**: JOINs + sub-queries or set operations.

* **Extra step**: For non-nested and nested queries, detect all tables to join and sub-queries to generate.

* **Why**: JOIN errors grow with query complexity, so different prompts are needed.

**3. SQL Generation Module**

* **Easy class**: Direct few-shot prompt → final SQL.

* **Non-nested complex**:
  
  * Use **NatSQL intermediate representation** to simplify SQL structure (removes JOIN ON, GROUP BY, etc.) before final SQL.

* **Nested complex**:
  
  * Generate sub-query SQLs first (each as its own \<question, answer> pair).
  * Combine sub-queries + NatSQL → final SQL.

* **Why**: Avoids forcing LLM to “mentally” handle all logic at once.

**4. Self-Correction Module**

* **Goal**: Fix minor errors (syntax, missing DISTINCT, wrong DESC, etc.).

* **Prompt types**:
  
  * **Generic** (“Buggy SQL… Fixed SQL…”): better for CodeX.
  * **Gentle** (“Check if SQL has issues…”): better for GPT-4.

* **Why**: Even correct logic can fail due to small syntax mistakes.

***Samples***

Here are representative **prompt samples** for each DIN-SQL module, adapted directly from the paper's examples.

**1. Schema Linking Module**

**Prompt style:** Few-shot, chain-of-thought, output = list of schema elements and foreign keys.

**Example:**

```
# Find the schema_links for generating SQL queries for each question 
# based on the database schema and Foreign keys.

Table city, columns = [*,City_ID,Official_Name,Status,Area_km_2,Population,Census_Ranking]
Table farm_competition, columns = [*,Competition_ID,Year,Theme,Host_city_ID,Hosts]
Foreign_keys = [farm_competition.Host_city_ID = city.City_ID]

Q: "Show the status of the city that has hosted the greatest number of competitions."
A: Let’s think step by step.
- "status of the city" → column [city.Status]
- "hosted the greatest number of competitions" → column [farm_competition.*]
- Foreign key needed: [farm_competition.Host_city_ID = city.City_ID]
Schema_links: [city.Status, farm_competition.*, farm_competition.Host_city_ID = city.City_ID]
```

**2. Query Classification & Decomposition Module**

**Prompt style:** Given schema links + question → classify complexity + list joins/sub-queries.

**Example:**

```
Given a question, schema links, and schema, classify the query into:
- Easy: single-table, no joins, no sub-queries
- Non-nested complex: joins but no sub-queries
- Nested complex: joins + sub-queries or set operations
Also list the tables to join and sub-queries (if any).

Q: "Find the names of students who have taken any course in Fall 2009 but not in Spring 2010."
Schema_links: [student.name, takes.ID, teaches.ID, teaches.semester, teaches.year]
Classification: Nested complex
Tables_to_join: [student, takes]
Sub-queries: 
  1. Students with course in Fall 2009
  2. Students with course in Spring 2010
```

**3. SQL Generation Module**

* **Easy Class**

```
Q: "Find the buildings with rooms that have capacity more than 50."
Schema_links: [classroom.building, classroom.capacity]
SQL: SELECT DISTINCT building FROM classroom WHERE capacity > 50
```

* **Non-Nested Complex Class** (using **NatSQL** intermediate representation)

```
Q: "List the names and salaries of instructors who work in the same department as 'Smith'."
Schema_links: [instructor.name, instructor.salary, instructor.dept_name]
NatSQL: SELECT name, salary FROM instructor WHERE dept_name = 
         (SELECT dept_name FROM instructor WHERE name = 'Smith')
SQL: SELECT T1.name, T1.salary FROM instructor AS T1 
     WHERE T1.dept_name = (SELECT T2.dept_name FROM instructor AS T2 
                            WHERE T2.name = 'Smith')
```

* **Nested Complex Class** (generate sub-queries first)

```
Q_main: "Find the names of students who took courses in both 2009 and 2010."
Schema_links: [student.name, takes.year]
Sub-query 1 Q: "Students who took courses in 2009"
  SQL: SELECT DISTINCT ID FROM takes WHERE year = 2009
Sub-query 2 Q: "Students who took courses in 2010"
  SQL: SELECT DISTINCT ID FROM takes WHERE year = 2010
Final SQL: SELECT name FROM student 
           WHERE ID IN (Sub-query1) AND ID IN (Sub-query2)
```

**4. Self-Correction Module**

**Generic prompt** (CodeX preferred)

```
BUGGY SQL:
SELECT DISTINCT name salary FROM instructor WHERE dept_name = 'History'
-- Missing comma between name and salary

FIXED SQL:
SELECT DISTINCT name, salary FROM instructor WHERE dept_name = 'History'
```

**Gentle prompt** (GPT-4 preferred)

```
Please check the following SQL for correctness. 
Pay attention to SELECT clause, WHERE clause, joins, and aggregation functions.

SQL: SELECT dept_name AVG(salary) FROM instructor GROUP BY dept_name
-- Suggestion: Missing comma between dept_name and AVG(salary)
Corrected SQL: SELECT dept_name, AVG(salary) FROM instructor GROUP BY dept_name
```

If you want, I can also create a **side-by-side table** showing *module → input → output example* for all four steps so it’s easier to see the decomposition pipeline in one view.
Do you want me to prepare that?

***Mention***

- "Despite improvements over zero-shot, few-shot models struggle on more complex queries including
  those where schema linking is less trivial and the queries that use multiple joins or have a nested
  structure"

- Prompting has several advantages over traditional approaches using pretraining or fine-tuning. The main benefit is that LLMs can perform prediction tasks without requiring large task-specific training data. Training models from scratch or fine-tuning them is a resource-intensive process, often requiring a large number of training samples and machine resources, which may not be available. Additionally, few-shot prompting has been shown to outperform previous state-of-the-art methods on several benchmark datasets and can achieve high accuracy even with limited training examples [Brown et al., 2020, Wei et al., 2022b].

***FINAL RECOMMEND FROM THIS PAPER***

* Zero shot continue proving it weakness and few shots is better.
* Decomposing the task into smaller sub-tasks is effective (**Result**: +\~10% execution accuracy over few-shot baseline across models; largest gains in hard and extra-hard queries).
* Schema linking is effective, however, it was manually injected into the prompts by human, raising the novelty question: Can we do it unsupervised? Without the JSON file of the schema (Developer's knowledge)?
* Self-Correction is effective for fixing minor errors in SQL queries (**\~5% improvement** for CodeX with generic prompt, smaller gain for GPT-4 with gentle prompt). The authors simply use: Assume the results is wrong, and fix the result. *What about more complex supervised correction?* Using frameworks with step-by-step checking, or prompts that will not give assumption but instruction, even create results and check if they sound correct? Sample: Check syntax, run the code and check results, if error – fix it – if not – check the first 10 rows (by function) … The simplest improvement is: Run the code, check for errors, and fix them, all automatically with agentic AI.

# Other options on Spider 2.0.

IEEE: “Spider 2.0.” https://spider2-sql.github.io/

*Problems:* All high ranking works are not publicly available.

| Rank | Date         | Method / Team                                                | Score |
| ---- | ------------ | ------------------------------------------------------------ | ----- |
| 1    | Aug 8, 2025  | WindAgent + Claude-4-Sonnet (MeiTuan AI)                     | 59.05 |
| 2    | Aug 6, 2025  | Ask Data w/ Relational Knowledge Graph (AT&T & RelationalAI) | 57.77 |
| 3    | Jul 28, 2025 | ByteBrain-Agent (ByteDance)                                  | 56.86 |
| 4    | Jul 21, 2025 | DB-Surfer Agent (Alibaba Cloud)                              | 53.02 |
| 5    | Jul 7, 2025  | Meituan-agent (Meituan FinData)                              | 51.37 |
| 6    | Aug 4, 2025  | AiCheng Agent (ALIBABA_EI)                                   | 50.27 |
| 7    | Jul 2, 2025  | Chat2DB-Agent + Claude-4-Sonnet (Chat2DB)                    | 44.06 |

***Recommendation:*** Relational Knowledge Graph have been used by AT&T and RelationalAI, and it is a good option to consider for Spider 2.0. However, the details of the implementation are not available, so we cannot replicate it. It is also not our main focus on the project, as the focus is on explainable interaction with relational databases using a multi-agent system.

## PART 2: AGENTIC AI DESIGN

### **1. Demonstration of DB-GPT: Next Generation Data Interaction System Empowered by Large Language Models**

S. Xue et al., “Demonstration of DB-GPT: Next generation Data Interaction System empowered by large language models,” arXiv.org, Apr. 16, 2024. https://arxiv.org/abs/2404.10209

"DB-GPT is a open-source, product-ready Python library that integrates LLMs into traditional data interaction tasks to enhance user experience and accessibility. DB-GPT is designed to understand data interaction tasks described by natural language and provide context-aware responses powered by LLMs, making it an indispensable tool for users ranging from novice to expert."

Its main focus are:

- 1. Design of multi-agents framework for supporting database interaction.
- 2. The declarative expression supporting arrange multi-agents flexibly.
- 3. Focuses on the design of private LLM-empowered data interaction.

It have: 

It has:

* **Multi-Agent Framework** – Automates complex data interaction tasks, such as Text-to-SQL, multi-dimensional reporting, and generative analysis, with specialized agents for planning, execution, and aggregation.
* **Agentic Workflow Expression Language (AWEL)** – A DAG-based declarative language (inspired by Apache Airflow) for flexible orchestration of multiple agents, available via code or drag-and-drop UI.
* **Service-oriented Multi-model Management Framework (SMMF)** – Manages multiple LLMs locally or in the cloud, supports private model execution for data privacy, and enables fine-tuned Text-to-SQL models.
* **Retrieval-Augmented Generation (RAG) from multiple data sources** – Builds and searches knowledge bases with vector, inverted, and graph indexes; retrieves context to improve LLM outputs through Interactive Contextual Learning.
* **Product-ready features** – Multilingual support (English/Chinese), chat-to-database/data/Excel/visualization, user-friendly front-end, distributed/cloud deployment via Ray, and strong visualization capabilities.
* **Fine-tuning hub (DB-GPT-Hub)** – Allows domain-specific Text-to-SQL model training and private on-premise execution.

***FINAL RECOMMENDATION***

- The system can follow MLOps principles to ensure smooth deployment, monitoring, and maintenance of the AI models and workflows. If so, the design could have modules but not limited as monitoring, evaluation, feedback, testing and debugging. Layers of the system can be designed with layers as Visualization, Application, server, module, protocol and training (With supporting models).

- Visualization Layer could be flexible with purely textual question-and-answer formats, then chart and tables generations

- We can also have Prompt strategy management module to control and increase the performance of the system.

- Data privacy could be a part of our project.

- Reasoning part could be presented clearly together with final result to increase clarity. Novelty point: Interactive capacity in reasoning steps of AI agents did not been mentioned.

### 2. DAgent: A Relational Database-Driven Data Analysis Report Generation Agent

W. Xu et al., “DAGENT: a Relational Database-Driven Data Analysis Report Generation agent,” ACM, conference-proceeding, 2018. [Online]. Available: https://arxiv.org/pdf/2503.13269v1

Score: DA-BIRD Dataset: F1 Table Retrieval 0.82, F1 Column Retrieval 0.71.

***Information***

- "The LLM Agent System is a framework designed to address complex
  tasks by integrating reasoning, planning and execution capabilities
  within large language models."

- "Single-agent systems operate independently, leveraging methods like Chain-of-Thought (CoT)[34] reasoning and Tree-of-Thought (ToT)[37], while multiagent systems involve the collaboration of multiple agents to solve
  large-scale problems through communication, task sharing, and collective intelligence, thereby enhancing scalability.[14]."

- "At its core, an LLM Agent System consists of three core modules:
  planning, tools and memory[35]. "

- "To efficiently adapt LLMs to specific downstream tasks, fine-tuning
  is often necessary. However, full-parameter fine-tuning of LLMs
  is computationally expensive and requires substantial memory resources, making it impractical for many applications. To address
  this challenge, parameter-efficient fine-tuning (PEFT) techniques
  have been developed, which aim to adapt pre-trained models to
  new tasks by updating only a small subset of parameters. Among
  these techniques, Low-Rank Adaptation (LoRA)[18] has emerged as
  one of the most widely recognized and effective methods, achieving
  competitive performance across various tasks while significantly
  reducing resource requirements[25]." 

***FINAL RECOMMENDATION***

- Could separate the design structure of the AI system into 3 parts: planning, tools, and memory as follows:
  
  1. **Planning**: "The Planning module is responsible for formulating execution strategies and coordinating tool usage to process natural language questions accurately. When a natural language question 𝑄 is received, the planning module first evaluates whether decomposition is required. The decision is based on factors such as question complexity, the number of distinct aspects involved, and whether multi-step reasoning."
  
  2.1 **Tools**: "The tools module is responsible for completing specific operations according to the task path formulated by the planning module. As a functional module called by the planning module, each tool in the tools module has a clear functional division, providing support for different aspects of the task respectively to ensure the efficiency and accuracy of task execution."
  2.2 "We can separate the tools to: Problem Decomposition Tools, Data retrieval Tools, SQL Rewriting Tools, Report Generation Tools"
  
  3.1 **Memory**: "Memory module is to provide efficient support for task execution. By storing key information, the system can leverage historical experience in questions, thereby improving the efficiency and quality of task processing. 
  3.2 Specifically, the Memory module achieves this goal through three types of memory: historical user questions and results, intermediate content for the question, and historical question and planning path correspondence."

## PART 3: INTERACTIVE REASONING STEPS IN AGENTIC AI

### 1. AI chains: Transparent and controllable Human-AI interaction by chaining large language model prompts

AI Chains = Chains of Thought, was design to increase the clarity by showing the reasoning process of the AI in a step-by-step manner. It also decomposing the prompts to smaller pieces so the AI can work better. Editable reasoning steps also include and do improve performance and UI, allowing users to interact with and refine the AI's thought process.

It do use 3 type of tool categories with 8 type of tool: Validation/Categorization: Classification, Information Gathering: Factual Query, Generation (creative “hallucination”), Ideation (lists/examples), and Re-organization: Information Extraction, Rewriting, Split Points (1-N mapping), Compose Points (N-1 mapping).

Its System Architecture are: 

- Chain Structure: Visual, node-based representation of steps and data layers

- Step View: Per-step prompt templates with placeholders for inputs, outputs, few-shot examples, and parameters (e.g., temperature)

- Interactivity: Users can Edit prompts locally per step, Edit intermediate data outputs, and Rewire/add/remove steps globally.

- Execution Modes: Run individual steps, parallel branches, or the entire chain

***Results***

- Higher ratings for transparency, control, collaboration, and goal-matching outputs versus a single-prompt baseline (Sandbox)

- Participants curated outputs more (77% vs 41%) and re-ran without edits less (36% vs 51%)

- Independent raters preferred Chaining outputs ~82% of the time

- Users leveraged chaining to: calibrate expectations, explore prompt variations, debug outputs, and discover new uses

***FINAL RECOMMENDATION***

We can design the similar system and explore-testing the combination of tools for this. Instead of using human interaction for planning what tools is the best, we will do as previous papers did, to use AI do to automated tool selection and planning, but do have ability for human interaction in the reasoning steps.

T. Wu, M. Terry, and C. J. Cai, “AI chains: Transparent and controllable Human-AI interaction by chaining large language model prompts,” arXiv.org, Oct. 04, 2021. Available: https://arxiv.org/abs/2110.01691?utm_source=chatgpt.com

### 2. Interactive Reasoning: Visualizing and Controlling Chain-of-Thought Reasoning in Large Language Models

R. Y. Pang et al., “Interactive Reasoning: Visualizing and Controlling Chain-of-Thought Reasoning in Large Language Models,” journal-article, Jun. 2025. Available: https://arxiv.org/pdf/2506.23678

- Build up a Chain-of-Thought (CoT) reasoning application with ability to interact with reasoning steps, using modern tree style UI nodes.
- It includes a tree visualization of the reasoning steps and allows users to directly control when models need users’ feedback.
- Beside reasoning steps, it also have feedback steps that will ask for user feedbacks for more information, this is similar with intructions, add knowledge, and manupilating steps, however, instead of passively been edited by users, it demand users to actively engage with the model by providing input and guidance or it will stop the reasoning process and wait.

Results: 

- Experiments on mathematical reasoning, commonsense reasoning, and logical deduction tasks show that interactive CoT yields higher accuracy than standard CoT prompting.

- User studies (N ≈ 20) found that participants rated the system higher for transparency, control, and engagement compared to non-interactive baselines. The difference in ratings was statistically significant, from approximately 10% to 25%.

- Interactive reasoning reduced unnecessary full-regenerations and improved the efficiency of debugging faulty reasoning steps.

# PART 4: EVALUATION METRICS

We will use spider 1 and spider 2.

1. Spider 1: The original Spider dataset, which includes a diverse set of text-to-SQL examples across various databases and schemas.

T. Yu et al., “Spider: a Large-Scale Human-Labeled dataset for complex and Cross-Domain semantic parsing and Text-to-SQL task,” arXiv.org, Sep. 24, 2018. https://arxiv.org/abs/1809.08887

2. Spider 2: An extended version of the Spider dataset, which includes additional examples, more complex queries, and improved schema representations.

F. Lei et al., “Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL workflows,” arXiv.org, Nov. 12, 2024. https://arxiv.org/abs/2411.07763

***How to use the benchmarks***

To benchmark with **Spider 1** and **Spider 2**, follow the same general evaluation protocol, but note the differences in dataset size and complexity:

**1. Metrics**

* **Exact Match (EM):** The predicted SQL must match the gold SQL exactly after formatting/normalization.
* **Execution Accuracy (EX):** The predicted SQL, when executed, must return the same results as the gold SQL on the database.
* **Component Matching (Partial Match):** Evaluates the correctness of individual SQL components (SELECT, WHERE, GROUP BY, etc.), allowing partial credit.
* **SQL Hardness Analysis:** Break results down into “easy”, “medium”, “hard”, and “extra hard” categories based on query complexity to assess model performance at different difficulty levels  .

**2. Evaluation Procedure**

1. **Use the official Spider evaluation script** provided by the dataset authors.
   
   * For Spider 1: `python evaluation.py --gold data/dev_gold.sql --pred predicted.sql --db data/database`
   * For Spider 2: Use its updated evaluation script and schema files (it adds more complex queries and refined schema links).

2. **Normalize SQL** before comparison — remove formatting differences, alias variations, and ordering changes that do not affect execution.

3. **Run Execution Accuracy tests** by executing both predicted and gold SQL on the associated database and comparing returned tuples.

4. **Report per-difficulty breakdown** to show how performance scales with complexity.

5. **Optionally evaluate cross-domain generalization** — Spider datasets are designed to test on unseen schemas, so ensure your model is not trained on evaluation databases.

**3. Best Practice**

* Always report **both EM and EX** for completeness.
* Include **component-level F1 scores** to show where errors occur (e.g., SELECT clause correct but WHERE incorrect).
* For Spider 2, highlight performance on the newly introduced harder queries and additional schema features.