# I. Methods

**Task 1: Design and deploy the core modules of the Agentic AI application**

SQL query tasks already proved to be complex and challenging for simple AI applications. Meanwhile, complex agentic AI prove to be more effective when solving this type of tasks [][][][]. Advanced agentic AI techniques like Chain-of-Thought (CoT) reasoning process, prompting techniques, Schema Linking, editable reasoning steps also boost the effectiveness significantly[][][][][]. <- Should this be in the background section? (I Dont think I should put it here)(Remove it you think the same)

The project aim to experiment on mutiple complex design increase with performance of the AI application. The project will implement mutiple strategies but not limited to:

- Few shots prompting, database-aware (DAIL).
- Schema linking with explicit linking prompts and foreign-key surfacing.
- Decomposition prompts
- Self-correction prompts
- Agentic planning and tooling

To test the effectiveness of these strategies, we will design mutiple structures of applications. Optionaly, editable reasoning can be implemented to allow users to modify the reasoning steps of the AI agents, providing both explainable capacity and performance.

The data set of the project will be Spider version 1 dataset, which is a complex SQL query dataset used to evaluate the performance of AI applications in solving SQL query tasks.

**Task 2: Evaluate and optimize the performance of the designs**

The performance of the Agentic AI application will be evaluated using the built-it test sets of the Spider version 1 dataset. The valuation will be conducted through a series of combinations by models and agentic AI techniques based on the Spider version 1 dataset's metrics that been proposed in the dataset's paper. Metrics that will be used are Exact-Match, Execution Accuracy, and other relevant metrics.

**Task 3: Design and deploy the explainable elementors for the Agentic AI application in the GUI of the application.**

To overcome the limited clarity of the reasoning process in the Agentic AI application, we will implement explainable elementors in the GUI of the application. These elementors will provide users with insights into the reasoning process of the AI agents, enhancing transparency and user understanding. The design may explore various visualization techniques, such as reasoning paths and tree, along with result presentation like chart, data table, SQL tables or other formats that can effectively increase the explainable capacity of the AI agents.

**Task 4: Evaluate the effectiveness of the explainable elementors in the Agentic AI application in enhancing the AI agents' performance and user satisfaction.**

The effectiveness of the explainable elementors will be evaluated through user studies and performance metrics using surveying techniques [][][][][]. User studies will involve gathering feedback from users on the clarity and usefulness of the explanations provided by the elementors as well as their impact on user satisfaction and trust in the AI agents. Each of the metrics will be evaluated and the overall feedback also collected. The space of evaluation samples will include a diverse range of user interactions and scenarios, base on the Spider data set and SQL potential tasks to ensure comprehensive evaluation.

The project source code and documentation, including design documents, proposals, and final paper, will be managed using Github version control system, with built-in product managing features like tasks - issues, and virtual co-workspace.


[1] D. Gao et al., “Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation,” 2023. 
[2] M. Pourreza and D. Rafiei, “DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction,” 2023. 
[3] S. Xue et al., “Demonstration of DB-GPT: Next Generation Data Interaction System Empowered by LLMs,” 2024. 
[4] T. Wu, M. Terry, and C. J. Cai, “AI Chains: Transparent and Controllable Human-AI Interaction,” 2021. 
[5] R. Y. Pang et al., “Interactive Reasoning: Visualizing and Controlling Chain-of-Thought Reasoning,” 2025. 
[6] T. Yu et al., “Spider: A Large-Scale Human-Labeled Dataset for Text-to-SQL,” 2018.
[7] F. Lei et al., “Spider 2.0: Evaluating LMs on Real-World Enterprise Text-to-SQL Workflows,” 2024; site and leaderboard updated 2025-08. 
[8] W. Xu et al., “DAgent: A Relational Database-Driven Data Analysis Report Generation Agent,” 2025. 
