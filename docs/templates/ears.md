
# Easy Approach to Requirements Syntax

en.wikipedia.org

Contributors to Wikimedia projects
11–14 Minuten

From Wikipedia, the free encyclopedia

The Easy Approach to Requirements Syntax (EARS) is a structured method for writing natural language requirements using a small set of keywords and sentence patterns. Developed by Alistair Mavin and colleagues at Rolls-Royce plc while analysing airworthiness regulations for a jet engine control system, EARS was first published at the IEEE International Requirements Engineering Conference (RE'09) in 2009.[1] EARS gently constrains free-form natural language by imposing a consistent clause order and a limited vocabulary of structural keywords, reducing or eliminating common problems such as ambiguity, vagueness and incompleteness.[2]

EARS has been adopted by organisations including Airbus, Bosch, Dyson, Honeywell, Intel, NASA, Rolls-Royce and Siemens, and is taught at universities in China, France, Germany, Sweden, the United Kingdom and the United States.[2] Since 2025, EARS notation has been integrated into AI-assisted spec-driven development tooling, most notably Amazon's Kiro IDE.[3]

System requirements are usually written in unconstrained natural language, which is inherently imprecise. Requirements authors are often domain experts rather than trained requirements engineers, and poorly expressed requirements propagate errors to downstream design, implementation and testing phases, increasing cost and schedule risk. While formal specification languages can increase precision, they impose a significant training overhead and require translation of source requirements, which can itself introduce errors.[4]

EARS was designed to occupy a middle ground: it retains natural language so that all stakeholders can read and review requirements without specialist training, while imposing enough syntactic structure to eliminate the most common defects. The approach arose during Mavin's analysis of the airworthiness regulations contained in the certification basis for a Rolls-Royce aero engine control system, where he observed that well-written requirements all followed a similar underlying structure.[1]

The general structure of an EARS requirement is:

    WHILE <optional precondition(s)>, WHEN <optional trigger>, the <system name> SHALL <system response>

The EARS ruleset states that a requirement must have:[2]

- Zero or many preconditions
- Zero or one trigger
- Exactly one system name
- One or many system responses

The clauses always appear in the same temporal order, and a small number of keywords denote the different clause types. This produces requirements that fall into one of five basic patterns, plus combinations thereof.

Ubiquitous requirements are always active. They have no EARS keyword because there is no triggering condition.

    THE <system name> SHALL <system response>

Example: "The mobile phone SHALL have a mass of less than 150 grams."

Event-driven requirements specify how a system must respond when a triggering event occurs. They are denoted by the keyword WHEN.

    WHEN <trigger>, the <system name> SHALL <system response>

Example: "WHEN 'mute' is selected, the laptop SHALL suppress all audio output."

State-driven requirements are active as long as a specified state remains true. They are denoted by the keyword WHILE.

    WHILE <precondition(s)>, the <system name> SHALL <system response>

Example: "WHILE there is no card in the ATM, the ATM SHALL display 'insert card to begin'."

Optional feature requirements apply only in products or system variants that include a specified feature. They are denoted by the keyword WHERE.

    WHERE <feature is included>, the <system name> SHALL <system response>

Example: "WHERE the car has a sunroof, the car SHALL have a sunroof control panel on the driver door."

Unwanted behaviour requirements specify the required system response to undesired situations such as faults, failures or errors. They are denoted by the keywords IF and THEN.

    IF <trigger>, THEN the <system name> SHALL <system response>

Example: "IF an invalid credit card number is entered, THEN the website SHALL display 'please re-enter credit card details'."

## Complex requirements

The simple building blocks above can be combined to specify richer system behaviour. Complex requirements use more than one EARS keyword:[2]

    WHILE <precondition(s)>, WHEN <trigger>, the <system name> SHALL <system response>

Example: "WHILE the aircraft is on ground, WHEN reverse thrust is commanded, the engine control system SHALL enable reverse thrust."

## Benefits and limitations

EARS provides several documented advantages over unconstrained natural language requirements:[1][4]

- Reduced ambiguity – The fixed clause order and keyword vocabulary force authors to make triggering conditions, preconditions and expected responses explicit.
- Low adoption barrier – The keywords closely match everyday English usage, so there is minimal training overhead and no need for specialised tooling.
- Language accessibility – EARS is particularly effective for authors who write requirements in English but whose first language is not English.
- Improved testability – The structured separation of conditions and responses makes it straightforward to derive test cases.
- Compatibility with existing tools – Requirements can be written in any text editor, word processor or requirements management tool.

EARS is not suited to every requirement type. Requirements with more than three preconditions can produce unwieldy single sentences, and some requirements are better expressed as mathematical formulae, decision tables, or state-transition diagrams.[5] The notation is also less appropriate for non-functional requirements that cannot be captured as conditional behaviour (e.g., architectural constraints).

## Publication history

|Year	|Publication	Notes|
|--|--|
|2009	|"Easy Approach to Requirements Syntax (EARS)" – RE'09	Original paper introducing the five EARS patterns.[1]|
|2010	|"Big Ears (The Return of Easy Approach to Requirements Engineering)" – RE'10	Wider experiments across multiple requirement document sets; templates refined and limitations addressed.[6]|
|2011	|"Easy EARS: Rapid application of the Easy Approach to Requirements Syntax" – RE'11	Industry short paper on rapid adoption by Sarah Gregory.[7]|
|2016	|"Listens Learned (8 Lessons Learned Applying EARS)" – RE'16	Lessons from seven years of industrial application.[4]|
|2019	|"Ten Years of EARS" – IEEE Software	Retrospective by the original authors on a decade of adoption and evolution.[8]|

## Use in spec-driven development

Spec-driven development (SDD) is a software methodology in which a formal or semi-formal specification—rather than ad-hoc prompts or informal descriptions—drives code generation, testing and documentation. In SDD workflows, requirements are first captured in a structured format, then used to produce a technical design, and finally broken down into implementation tasks. EARS notation has emerged as a favoured syntax for the requirements phase of SDD because its constrained natural language can be parsed by both humans and large language models (LLMs), bridging the gap between product intent and machine-readable specifications.[9]

Kiro, an agentic AI integrated development environment announced by Amazon in 2025 and built on Code OSS, has adopted EARS as its native requirements notation.[3] Kiro's spec-driven workflow operates in three phases:

1. Requirements (requirements.md): The developer enters a natural language prompt (e.g., "Add a review system for products"). Kiro expands this into user stories, each with acceptance criteria written in EARS notation. The structured format explicitly captures preconditions, triggers and expected system responses, covering edge cases that developers would otherwise discover during implementation.[10]
2. Design (design.md): Based on the EARS requirements and the existing codebase, Kiro generates a technical design document including architecture, sequence diagrams, and technology stack decisions.
3. Tasks (tasks.md): The design is decomposed into discrete, sequenced implementation tasks with dependency tracking.

Because each acceptance criterion follows the EARS pattern WHEN \<condition/event\> THE SYSTEM SHALL \<expected behaviour\>, the requirements are directly testable and provide unambiguous success criteria for each generated task. Developers can also manually author requirements in EARS format and use Kiro's "Refine" function to validate or restructure them.[11]

## Broader AI-assisted adoption

The integration of EARS into Kiro reflects a broader trend in which structured requirements templates are used to improve the predictability and quality of LLM-generated code. Compared to free-form prompts (sometimes called "vibe coding"), EARS-formatted specifications reduce the ambiguity that causes AI agents to make undesirable assumptions.[9] Community projects have extended the approach to other AI coding assistants through plugins and Model Context Protocol (MCP) servers that expose EARS-based spec-driven workflows.[12]

|Method	|Format	|Primary use	|Key difference from EARS|
|--|--|--|--|
|EARS	|Constrained natural language with keywords	|System/software requirements	|Lightweight keyword-based patterns|
|User story	|"As a \<role\>, I want \<goal\>, so that \<benefit\>"	|Agile feature descriptions	|Focuses on user value, not system behaviour; no syntactic constraints on acceptance criteria|
|Gherkin (Given/When/Then)	|Structured scenario language	|Behavior-driven development (BDD)	|Oriented toward executable test scenarios rather than system-level requirements|
|Rupp's template	|"The system shall <process verb> <object>" with condition extensions	|Requirements specification	|More prescriptive verb taxonomy; requires deeper training|
|Boilerplate templates	|Parameterised sentence patterns	|Formal requirements	|Greater formality and tool dependency|

EARS and user stories are frequently used together in practice: user stories capture high-level stakeholder needs, while EARS is used to specify detailed acceptance criteria within each story—an approach formalised by Kiro's spec-driven workflow.[10]

- Requirements engineering
- Spec-driven development
- Controlled natural language
- Requirements analysis
- Behavior-driven development
- Systems engineering
- Vibe coding

1. Mavin, Alistair; Wilkinson, Philip; Harwood, Adrian; Novak, Mark (2009). Easy Approach to Requirements Syntax (EARS). 17th IEEE International Requirements Engineering Conference (RE'09). IEEE. pp. 317–322. doi:10.1109/RE.2009.9.
2. Alistair Mavin. "EARS – Easy Approach to Requirements Syntax". Retrieved 2026-02-07.
3. "Introducing Kiro". Kiro. 2025. Retrieved 2026-02-07.
4.  Mavin, Alistair; Wilkinson, Philip; Gregory, Sarah; Uusitalo, Eero (2016). Listens Learned (8 Lessons Learned Applying EARS). 24th IEEE International Requirements Engineering Conference. pp. 276–282. doi:10.1109/RE.2016.38.
5.  "When Not to Use EARS". QRA Corp. 2025. Retrieved 2026-02-07.
6.  Mavin, Alistair; Wilkinson, Philip (2010). Big Ears (The Return of Easy Approach to Requirements Engineering). 18th IEEE International Requirements Engineering Conference. pp. 277–282. doi:10.1109/RE.2010.39.
7.  Gregory, Sarah (2011). Easy EARS: Rapid application of the Easy Approach to Requirements Syntax. 19th IEEE International Requirements Engineering Conference (Industry Short Paper).
8.  Mavin, Alistair; Wilkinson, Philip; Gregory, Sarah; Uusitalo, Eero (2019). "Ten Years of EARS". IEEE Software.
9.  "Beyond Vibe Coding: Amazon Introduces Kiro, the Spec-Driven Agentic AI IDE". InfoQ. 2025-08-18. Retrieved 2026-02-07.
10. "Specs – Concepts". Kiro. 2025. Retrieved 2026-02-07.
11. Drange, Håkon Eriksen (2025-08-14). "How to use Kiro for AI assisted spec-driven development". Retrieved 2026-02-07.
12. "Complete System Prompts for Kiro IDE by Amazon". GitHub. Retrieved 2026-02-07.

- [EARS – Official page by Alistair Mavin](https://alistairmavin.com/ears/)
- [EARS original paper on IEEE Xplore](https://ieeexplore.ieee.org/document/5328509/)
- [Kiro documentation – Specs concepts](https://kiro.dev/docs/specs/concepts/)
- [QRA – The Easy Approach to Requirements Syntax: The Definitive Guide](https://qracorp.com/guides_checklists/the-easy-approach-to-requirements-syntax-ears/)
- [Jama Software – Adopting EARS Notation for Requirements Engineering](https://www.jamasoftware.com/requirements-management-guide/writing-requirements/adopting-the-ears-notation-to-improve-requirements-engineering/)

