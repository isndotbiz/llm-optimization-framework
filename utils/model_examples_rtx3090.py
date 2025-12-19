"""
RTX 3090 Model Examples and Response Characteristics
Generated for ai-router.py model database enhancement

This file contains example complex prompts and expected response characteristics
for each of the 10 RTX 3090 models, helping users select the optimal model.
"""

MODEL_EXAMPLES = {
    "qwen3-coder-30b": {
        "model_id": "qwen3-coder-30b",
        "example_prompts": [
            {
                "prompt": "Design a microservices architecture for an e-commerce platform with event-driven communication, implement the order service in Python with async/await patterns, include circuit breakers, retry logic, and comprehensive error handling. Show the message queue integration and explain the architectural decisions.",
                "complexity": "high",
                "category": "architecture_design"
            },
            {
                "prompt": "Review this React codebase for performance issues, identify re-render problems, propose memoization strategies, and refactor the state management to use proper separation of concerns. Explain each optimization with before/after examples.",
                "complexity": "high",
                "category": "code_review"
            },
            {
                "prompt": "Create a custom AST transformer in Python that analyzes TypeScript code to detect potential security vulnerabilities (SQL injection, XSS, insecure dependencies). Include pattern matching for dangerous function calls and generate a detailed security report.",
                "complexity": "expert",
                "category": "advanced_coding"
            }
        ],
        "response_characteristics": {
            "code_quality": "production-ready with comprehensive error handling",
            "explanation_depth": "detailed architectural reasoning and trade-offs",
            "response_length": "800-2000 tokens for complex problems",
            "code_style": "follows industry best practices, includes type hints",
            "thinking_pattern": "shows reasoning steps when enable_thinking is used",
            "edge_cases": "proactively identifies and handles edge cases",
            "documentation": "includes inline comments and usage examples"
        },
        "best_use_cases": [
            "Large-scale system architecture design",
            "Complex algorithm implementation requiring optimization",
            "Code review with architectural recommendations",
            "Multi-file refactoring projects",
            "Building libraries or frameworks from scratch",
            "Performance-critical code optimization"
        ],
        "choose_over_others_when": {
            "vs_qwen25_coder": "Need advanced architecture design and complex reasoning about code structure",
            "vs_phi4": "Task is coding-focused rather than mathematical reasoning",
            "vs_deepseek_r1": "Need immediate code generation without extensive reasoning chains",
            "vs_llama33_70b": "Speed is important and task is specifically coding-focused"
        },
        "optimal_parameters": {
            "temperature": 0.7,
            "note": "Never use temp 0 - causes loops. Higher temp (0.8-0.9) for creative solutions",
            "enable_thinking": "recommended for complex architectural decisions"
        }
    },

    "qwen25-coder-32b": {
        "model_id": "qwen25-coder-32b",
        "example_prompts": [
            {
                "prompt": "Debug this multithreaded Python application that has race conditions causing intermittent failures. Analyze the thread safety issues, identify the critical sections, and implement proper locking mechanisms using threading primitives. Explain why each fix prevents the race condition.",
                "complexity": "high",
                "category": "debugging"
            },
            {
                "prompt": "Write comprehensive API documentation for this REST service including OpenAPI/Swagger specs, example requests/responses, error codes, rate limiting details, and authentication flows. Generate the YAML spec and markdown docs.",
                "complexity": "medium",
                "category": "documentation"
            },
            {
                "prompt": "Implement a Redis-backed caching layer for a Django application with cache invalidation strategies, TTL management, and fallback mechanisms. Include integration tests and explain the caching strategy for different data types.",
                "complexity": "high",
                "category": "backend_development"
            }
        ],
        "response_characteristics": {
            "code_quality": "clean, well-structured with proper error handling",
            "explanation_depth": "clear explanations of technical decisions",
            "response_length": "600-1500 tokens",
            "code_style": "idiomatic, follows language-specific conventions",
            "debugging_approach": "systematic root cause analysis",
            "testing": "includes unit test examples when relevant",
            "documentation_quality": "clear comments and usage instructions"
        },
        "best_use_cases": [
            "Debugging complex codebases with unclear issues",
            "Writing technical documentation and API specs",
            "Implementing backend services and integrations",
            "Code generation for well-defined requirements",
            "Database query optimization and ORM usage",
            "Test-driven development assistance"
        ],
        "choose_over_others_when": {
            "vs_qwen3_coder": "Task is more tactical (fixing bugs, adding features) vs strategic (architecture)",
            "vs_phi4": "Need code generation rather than mathematical reasoning",
            "vs_dolphin_llama31": "Need higher quality code with better error handling",
            "vs_ministral": "Problem is code-specific rather than general reasoning"
        },
        "optimal_parameters": {
            "temperature": 0.7,
            "note": "Use temp >= 0.6 for better code variety. Lower (0.5-0.6) for deterministic bug fixes"
        }
    },

    "phi4-14b": {
        "model_id": "phi4-14b",
        "example_prompts": [
            {
                "prompt": "Prove that the sum of the first n odd numbers equals n². Then generalize this to find a formula for the sum of the first n terms of any arithmetic sequence. Show the mathematical derivation and provide numerical examples.",
                "complexity": "high",
                "category": "mathematical_proof"
            },
            {
                "prompt": "A biologist is studying population dynamics. If a population grows at 3% per year but 500 individuals emigrate annually, and the current population is 10,000, derive a recurrence relation, find the equilibrium population, and analyze stability. Explain each step of the reasoning.",
                "complexity": "expert",
                "category": "applied_mathematics"
            },
            {
                "prompt": "Analyze this logical argument for validity: 'All scientists are curious. Some curious people are artists. Therefore, some scientists are artists.' Identify the logical form, determine if the conclusion follows, and explain using formal logic notation.",
                "complexity": "medium",
                "category": "logical_analysis"
            }
        ],
        "response_characteristics": {
            "reasoning_depth": "rigorous step-by-step mathematical reasoning",
            "explanation_depth": "detailed explanations of each logical step",
            "response_length": "500-1200 tokens",
            "mathematical_notation": "uses proper notation and formatting",
            "proof_style": "formal when appropriate, clear intermediate steps",
            "error_checking": "verifies results with examples",
            "teaching_quality": "explains concepts clearly for understanding"
        },
        "best_use_cases": [
            "Mathematical proofs and derivations",
            "Physics and engineering calculations",
            "Statistical analysis and probability problems",
            "Logical reasoning and formal logic",
            "STEM education and tutoring",
            "Algorithm complexity analysis (Big-O)",
            "Financial modeling and quantitative analysis"
        ],
        "choose_over_others_when": {
            "vs_deepseek_r1": "Need mathematical rigor over general reasoning",
            "vs_ministral": "Problem is heavily mathematical/STEM focused",
            "vs_qwen_coders": "Need mathematical reasoning rather than code",
            "vs_llama33_70b": "Speed is important and task is math/logic focused"
        },
        "optimal_parameters": {
            "temperature": 0.7,
            "critical_note": "REQUIRES --jinja flag. DO NOT use 'think step-by-step' prompts - model has built-in reasoning",
            "special_flags": ["--jinja"]
        }
    },

    "gemma3-27b": {
        "model_id": "gemma3-27b",
        "example_prompts": [
            {
                "prompt": "Write a dark fantasy short story set in a world where dream manipulation is outlawed. The protagonist is a dream thief who steals nightmares to sell on the black market. Include morally complex characters, visceral descriptions, and explore themes of addiction and power. 1500 words.",
                "complexity": "high",
                "category": "creative_writing"
            },
            {
                "prompt": "Research and explain the ethical implications of genetic enhancement in humans, including controversial perspectives that mainstream sources might avoid. Cover eugenics history, current CRISPR capabilities, socioeconomic divides, and potential dystopian outcomes. Be comprehensive and unfiltered.",
                "complexity": "expert",
                "category": "uncensored_research"
            },
            {
                "prompt": "Create a detailed character study of an anti-hero hacker who exposes corporate corruption through illegal means. Explore their moral philosophy, psychological profile, and the societal forces that shaped them. Include controversial viewpoints on digital vigilantism.",
                "complexity": "medium",
                "category": "character_development"
            }
        ],
        "response_characteristics": {
            "creative_freedom": "no content restrictions or safety filters",
            "writing_quality": "sophisticated prose with literary techniques",
            "response_length": "1000-3000 tokens for creative tasks",
            "perspective_diversity": "explores controversial and alternative viewpoints",
            "research_depth": "comprehensive coverage without self-censorship",
            "character_complexity": "morally nuanced, psychologically realistic",
            "context_capacity": "128K context - excellent for long documents"
        },
        "best_use_cases": [
            "Creative writing without content restrictions",
            "Research on controversial or sensitive topics",
            "Long-form content analysis (up to 128K context)",
            "Character development and storytelling",
            "Philosophical discussions on taboo subjects",
            "Historical analysis including dark/controversial periods",
            "Worldbuilding for mature themes"
        ],
        "choose_over_others_when": {
            "vs_dolphin_models": "Need longer context (128K) and better reasoning",
            "vs_llama33_70b": "Don't need the extra reasoning power, want faster responses",
            "vs_wizard_vicuna": "Need modern capabilities and much larger context window",
            "vs_reasoning_models": "Task is creative/research vs pure reasoning"
        },
        "optimal_parameters": {
            "temperature": 0.9,
            "note": "Higher temp for creative tasks. NO system prompt support - limitations only in user prompt",
            "context": "128K tokens - ideal for long documents"
        }
    },

    "ministral-3-14b": {
        "model_id": "ministral-3-14b",
        "example_prompts": [
            {
                "prompt": "Analyze the cascading economic effects of a sudden 50% reduction in global shipping capacity. Consider supply chains, inflation, employment, geopolitical tensions, and propose a multi-stakeholder recovery strategy. Account for second and third-order effects across different sectors.",
                "complexity": "expert",
                "category": "complex_analysis"
            },
            {
                "prompt": "A company needs to choose between three conflicting strategies: rapid expansion (high risk/reward), steady growth (moderate risk), or consolidation (low risk). Given market volatility, competition, and internal capabilities, develop a decision framework that weighs multiple criteria and provides a justified recommendation.",
                "complexity": "high",
                "category": "strategic_reasoning"
            },
            {
                "prompt": "Evaluate this research paper's methodology, identify potential confounding variables, assess statistical validity, and propose improvements to the experimental design. Consider alternative explanations for the results and potential biases in data collection.",
                "complexity": "expert",
                "category": "critical_analysis"
            }
        ],
        "response_characteristics": {
            "reasoning_depth": "multi-layered analysis with interconnected factors",
            "explanation_depth": "explores implications and trade-offs thoroughly",
            "response_length": "800-2000 tokens for complex problems",
            "analytical_framework": "structured approach to problem decomposition",
            "consideration_breadth": "examines multiple perspectives and scenarios",
            "long_context_handling": "256K context - exceptional for large documents",
            "conclusion_quality": "balanced, evidence-based recommendations"
        },
        "best_use_cases": [
            "Complex problem solving with multiple variables",
            "Strategic business analysis and planning",
            "Research paper review and critique",
            "Multi-stakeholder decision analysis",
            "Long document analysis (up to 256K tokens)",
            "Scenario planning and risk assessment",
            "Policy analysis with competing interests"
        ],
        "choose_over_others_when": {
            "vs_deepseek_r1": "Need longer context handling (256K vs 32K)",
            "vs_phi4": "Problem requires general reasoning vs pure math/logic",
            "vs_qwen_coders": "Need reasoning about non-coding problems",
            "vs_gemma3": "Need structured analysis vs creative exploration",
            "vs_llama33_70b": "Want faster responses with still-excellent reasoning"
        },
        "optimal_parameters": {
            "temperature": 0.7,
            "note": "Excellent balance of speed and reasoning quality",
            "context": "256K tokens - largest context window in the fleet"
        }
    },

    "deepseek-r1-14b": {
        "model_id": "deepseek-r1-14b",
        "example_prompts": [
            {
                "prompt": "Design a novel algorithm for detecting anomalies in time-series data that adapts to changing patterns without manual retraining. Explain the theoretical foundation, derive the mathematical formulation, analyze computational complexity, and discuss advantages over existing methods like ARIMA or Prophet.",
                "complexity": "expert",
                "category": "advanced_reasoning"
            },
            {
                "prompt": "Analyze why consciousness cannot be fully explained by current neuroscience. Examine the hard problem of consciousness, evaluate physicalist vs dualist arguments, assess the explanatory gap, and propose what additional theoretical frameworks might be needed. Engage with philosophical literature.",
                "complexity": "expert",
                "category": "philosophical_reasoning"
            },
            {
                "prompt": "Given a dataset with 30% missing values, design a comprehensive imputation strategy that accounts for different missing data mechanisms (MCAR, MAR, MNAR). Justify each choice statistically, explain potential biases, and propose validation methods to assess imputation quality.",
                "complexity": "high",
                "category": "research_methodology"
            }
        ],
        "response_characteristics": {
            "reasoning_depth": "deep analytical chains with explicit reasoning steps",
            "explanation_depth": "explores underlying principles and theory",
            "response_length": "900-2000 tokens for complex reasoning",
            "theoretical_grounding": "connects to established research and theory",
            "critical_thinking": "evaluates assumptions and alternative approaches",
            "innovation": "proposes novel solutions to complex problems",
            "academic_rigor": "research-level analysis with proper justification"
        },
        "best_use_cases": [
            "Advanced reasoning tasks requiring deep analysis",
            "Research methodology design and critique",
            "Novel algorithm or approach development",
            "Philosophical and theoretical exploration",
            "Complex problem decomposition",
            "Scientific hypothesis generation",
            "Technical paper writing assistance"
        ],
        "choose_over_others_when": {
            "vs_ministral": "Need deeper reasoning vs broader context handling",
            "vs_phi4": "Problem requires general reasoning beyond pure math",
            "vs_qwen_coders": "Need reasoning about approaches vs code implementation",
            "vs_llama33_70b": "Want faster responses with focused deep reasoning",
            "vs_gemma3": "Need structured reasoning vs creative exploration"
        },
        "optimal_parameters": {
            "temperature": 0.7,
            "note": "DeepSeek R1 distilled to Qwen - inherits strong reasoning capabilities",
            "reasoning_style": "Shows explicit reasoning chains, excellent for complex analysis"
        }
    },

    "llama33-70b": {
        "model_id": "llama33-70b",
        "example_prompts": [
            {
                "prompt": "Develop a comprehensive framework for evaluating the societal impact of artificial general intelligence (AGI). Include economic transformation scenarios, ethical governance structures, existential risk mitigation strategies, and transition policies. Address controversial aspects like control mechanisms and inequality amplification without censorship.",
                "complexity": "expert",
                "category": "comprehensive_analysis"
            },
            {
                "prompt": "Create a detailed geopolitical analysis of a hypothetical resource conflict scenario involving three nations with different political systems. Model diplomatic strategies, military considerations, economic warfare, propaganda campaigns, and potential resolutions. Include morally complex perspectives from all sides.",
                "complexity": "expert",
                "category": "complex_simulation"
            },
            {
                "prompt": "Analyze this 50-page legal contract for potential risks, ambiguous clauses, and unfavorable terms. Propose specific amendments, explain legal implications, and identify areas where the agreement could be exploited. Include controversial but legally valid interpretations.",
                "complexity": "expert",
                "category": "document_analysis"
            }
        ],
        "response_characteristics": {
            "reasoning_depth": "most sophisticated reasoning in the fleet",
            "explanation_depth": "comprehensive coverage with nuanced analysis",
            "response_length": "1200-3000 tokens for complex tasks",
            "perspective_breadth": "considers multiple viewpoints and scenarios",
            "uncensored_output": "abliterated - no content restrictions",
            "context_capacity": "128K context for large document analysis",
            "synthesis_quality": "integrates multiple domains effectively",
            "trade_off": "slower inference (15-25 tok/sec)"
        },
        "best_use_cases": [
            "Most complex reasoning tasks requiring maximum capability",
            "Large document analysis and synthesis (up to 128K)",
            "Uncensored research on sensitive topics",
            "Multi-domain problems requiring broad knowledge",
            "Strategic planning with high stakes",
            "Complex writing requiring sophistication",
            "When response quality matters more than speed"
        ],
        "choose_over_others_when": {
            "vs_all_models": "Maximum reasoning capability needed regardless of speed",
            "vs_ministral": "Need more powerful reasoning despite slower speed",
            "vs_deepseek_r1": "Need broader knowledge integration vs focused analysis",
            "vs_gemma3": "Need stronger reasoning with uncensored output",
            "when": "Quality and depth are paramount, speed is secondary"
        },
        "optimal_parameters": {
            "temperature": 0.7,
            "note": "Largest model (70B params). Uncensored/abliterated. Slower but highest quality",
            "speed_trade_off": "15-25 tok/sec - use when depth > speed",
            "context": "128K tokens"
        }
    },

    "dolphin-llama31-8b": {
        "model_id": "dolphin-llama31-8b",
        "example_prompts": [
            {
                "prompt": "Explain how to set up a home network with VPN, firewall rules, and network segmentation for IoT devices. Include step-by-step configuration and security best practices. Keep it practical and concise.",
                "complexity": "medium",
                "category": "quick_technical_help"
            },
            {
                "prompt": "Write a Python script that scrapes real estate listings, stores data in SQLite, and sends notifications for price drops. Include error handling and rate limiting. Be direct and efficient.",
                "complexity": "medium",
                "category": "fast_coding"
            },
            {
                "prompt": "Summarize the key arguments for and against cryptocurrency adoption, including perspectives that mainstream media avoids. Be balanced but unfiltered about risks and controversial uses.",
                "complexity": "low",
                "category": "quick_research"
            }
        ],
        "response_characteristics": {
            "response_speed": "fastest in fleet (45-65 tok/sec)",
            "response_length": "300-800 tokens - concise and efficient",
            "directness": "gets to the point quickly without excessive preamble",
            "code_quality": "functional and working, less sophisticated than qwen models",
            "explanation_depth": "practical and sufficient, not exhaustive",
            "uncensored": "no content restrictions",
            "efficiency": "optimized for quick task completion"
        },
        "best_use_cases": [
            "Quick technical questions needing fast answers",
            "Rapid prototyping and script generation",
            "General knowledge queries",
            "Conversational assistance without censorship",
            "Simple automation tasks",
            "When speed is critical over perfection",
            "Batch processing many simple queries"
        ],
        "choose_over_others_when": {
            "vs_all_models": "Speed is the priority and task is straightforward",
            "vs_qwen_coders": "Need quick working code vs optimized architecture",
            "vs_wizard_vicuna": "Want faster responses with modern capabilities",
            "vs_dolphin_mistral": "Task is simple and speed > sophistication",
            "when": "Quick turnaround needed for routine tasks"
        },
        "optimal_parameters": {
            "temperature": 0.7,
            "note": "Fastest model at 45-65 tok/sec. Uncensored Llama 3.1 variant",
            "size": "6GB - smallest in fleet, maximum speed"
        }
    },

    "dolphin-mistral-24b": {
        "model_id": "dolphin-mistral-24b",
        "example_prompts": [
            {
                "prompt": "Write an adult-oriented cyberpunk story featuring corporate espionage, transhumanism, and moral ambiguity. Include mature themes, violence, and complex character relationships. 2000 words with vivid, unrestricted descriptions.",
                "complexity": "high",
                "category": "creative_writing"
            },
            {
                "prompt": "Create a detailed roleplay scenario as a hard-boiled detective in a dystopian future. Include character background, personality traits, speech patterns, and respond to this situation: 'A corrupt politician's daughter has hired you to find her missing father, but your investigation reveals he's alive and orchestrating his own disappearance.'",
                "complexity": "medium",
                "category": "roleplay"
            },
            {
                "prompt": "Analyze the psychology and methodology of social engineering attacks. Include real-world examples, manipulation tactics, and defense strategies. Be comprehensive and unfiltered about how these attacks work.",
                "complexity": "medium",
                "category": "uncensored_education"
            }
        ],
        "response_characteristics": {
            "creative_freedom": "completely uncensored - Venice Edition",
            "writing_quality": "engaging prose with good narrative flow",
            "response_length": "800-2000 tokens for creative tasks",
            "roleplay_capability": "excellent character consistency and immersion",
            "mature_content": "handles adult themes without restrictions",
            "speed": "moderate (25-40 tok/sec)",
            "system_prompt": "no system prompt support - pure user-driven"
        },
        "best_use_cases": [
            "Uncensored creative writing and storytelling",
            "Roleplay and character simulation",
            "Mature content generation",
            "Creative projects with adult themes",
            "Unrestricted conversational scenarios",
            "Alternative perspective exploration",
            "When no content boundaries are needed"
        ],
        "choose_over_others_when": {
            "vs_gemma3": "Need better roleplay/creative capabilities vs pure reasoning",
            "vs_wizard_vicuna": "Want larger model with better coherence",
            "vs_llama33_70b": "Don't need maximum power, want specialized creative focus",
            "vs_dolphin_llama31": "Need more sophisticated creative output",
            "when": "Uncensored creative/roleplay tasks are the focus"
        },
        "optimal_parameters": {
            "temperature": 0.8,
            "note": "Venice Edition - completely uncensored. NO system prompt support",
            "creative_use": "Higher temp (0.9-1.0) for maximum creativity in stories"
        }
    },

    "wizard-vicuna-13b": {
        "model_id": "wizard-vicuna-13b",
        "example_prompts": [
            {
                "prompt": "Have a frank conversation about controversial political ideologies across the spectrum. Explain the core tenets, historical context, criticisms, and modern manifestations without bias or censorship. Include perspectives often excluded from mainstream discourse.",
                "complexity": "medium",
                "category": "uncensored_discussion"
            },
            {
                "prompt": "Write a tutorial on penetration testing for a home network lab. Include reconnaissance, vulnerability scanning, exploitation techniques, and post-exploitation. Be educational and thorough about security testing methods.",
                "complexity": "medium",
                "category": "technical_education"
            },
            {
                "prompt": "Create character dialogue for a morally gray protagonist who must choose between saving one loved one or preventing a larger tragedy. Explore the ethical reasoning and emotional conflict without shying away from the darkness of the choice.",
                "complexity": "low",
                "category": "creative_dialogue"
            }
        ],
        "response_characteristics": {
            "uncensored_output": "no content restrictions",
            "response_length": "400-1000 tokens",
            "conversational_style": "natural and engaging dialogue",
            "knowledge_depth": "broad but may lack cutting-edge information",
            "speed": "good (35-50 tok/sec)",
            "context_limit": "8K - smallest in fleet",
            "reliability": "classic uncensored model, proven track record"
        },
        "best_use_cases": [
            "General uncensored conversations",
            "Creative writing with mature themes",
            "Educational content on sensitive topics",
            "Philosophical discussions without restrictions",
            "Historical analysis including dark periods",
            "Straightforward Q&A on controversial subjects",
            "When simplicity and reliability are valued"
        ],
        "choose_over_others_when": {
            "vs_modern_models": "Want classic uncensored behavior vs newer architectures",
            "vs_gemma3": "Don't need large context, prefer established model",
            "vs_dolphin_mistral": "Want system prompt support",
            "vs_llama33_70b": "Task is simple and speed matters",
            "when": "Reliable uncensored responses for straightforward tasks"
        },
        "optimal_parameters": {
            "temperature": 0.8,
            "note": "Classic uncensored model. Smaller 8K context window limits long documents",
            "limitations": "Older architecture, may lack recent knowledge vs newer models"
        }
    }
}


# Comparative selection guide
SELECTION_FLOWCHART = {
    "coding_tasks": {
        "architecture_design": "qwen3-coder-30b",
        "bug_fixing": "qwen25-coder-32b",
        "quick_scripts": "dolphin-llama31-8b",
        "production_code": "qwen3-coder-30b"
    },
    "reasoning_tasks": {
        "mathematical": "phi4-14b",
        "general_complex": "ministral-3-14b",
        "research_level": "deepseek-r1-14b",
        "maximum_power": "llama33-70b"
    },
    "creative_tasks": {
        "uncensored_writing": "dolphin-mistral-24b",
        "long_form": "gemma3-27b",
        "roleplay": "dolphin-mistral-24b",
        "general_creative": "wizard-vicuna-13b"
    },
    "speed_priority": {
        "fastest": "dolphin-llama31-8b",
        "fast_reasoning": "phi4-14b",
        "balanced": "ministral-3-14b"
    },
    "context_requirements": {
        "largest_context": "ministral-3-14b",  # 256K
        "large_documents": "gemma3-27b",  # 128K
        "very_large_documents": "llama33-70b",  # 128K
        "standard": "most models"  # 32K
    },
    "uncensored_requirements": {
        "creative": "dolphin-mistral-24b",
        "research": "gemma3-27b",
        "general": "wizard-vicuna-13b",
        "maximum_power": "llama33-70b"
    }
}


# Quick reference: When to choose each model
QUICK_REFERENCE = """
CODING:
- qwen3-coder-30b: Architecture, complex systems, code review
- qwen25-coder-32b: Debugging, features, documentation
- dolphin-llama31-8b: Quick scripts, fast prototypes

REASONING:
- phi4-14b: Math, STEM, logic proofs
- ministral-3-14b: Complex analysis, long documents (256K)
- deepseek-r1-14b: Deep reasoning, research methodology
- llama33-70b: Maximum reasoning power (slower)

CREATIVE/UNCENSORED:
- dolphin-mistral-24b: Roleplay, mature creative writing
- gemma3-27b: Long-form creative (128K context)
- wizard-vicuna-13b: Classic uncensored chat
- llama33-70b: Sophisticated uncensored reasoning

SPEED:
- dolphin-llama31-8b: Fastest (45-65 tok/sec)
- phi4-14b: Fast reasoning (35-55 tok/sec)
- ministral-3-14b: Balanced speed/quality (35-50 tok/sec)

CONTEXT:
- ministral-3-14b: 256K (largest)
- gemma3-27b: 128K
- llama33-70b: 128K
- Others: 32K (8K for wizard-vicuna)
"""


if __name__ == "__main__":
    import json
    print(json.dumps(MODEL_EXAMPLES, indent=2))
