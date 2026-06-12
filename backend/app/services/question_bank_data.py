"""Predefined question bank data organized by interview type, topic, and difficulty.

This module contains the static question data used as fallback when Gemini API
is unavailable. Separated from service logic per code organization requirements.
"""

QUESTION_BANK: dict[str, dict[str, dict[str, list[dict[str, str]]]]] = {
    "hr": {
        "general": {
            "beginner": [
                {
                    "text": "Tell me about yourself and your background.",
                    "follow_up": "What motivated you to pursue this career path?",
                },
                {
                    "text": "Why are you interested in this role?",
                    "follow_up": "What specifically about our company appeals to you?",
                },
                {
                    "text": "What are your greatest strengths?",
                    "follow_up": "Can you give an example of when you used this strength?",
                },
                {
                    "text": "Where do you see yourself in five years?",
                    "follow_up": "How does this role align with your long-term goals?",
                },
                {
                    "text": "Why are you leaving your current position?",
                    "follow_up": "What would make you stay at a company long-term?",
                },
                {
                    "text": "What is your greatest weakness?",
                    "follow_up": "What steps have you taken to improve in this area?",
                },
                {
                    "text": "What do you know about our company?",
                    "follow_up": "How do you think you can contribute to our mission?",
                },
            ],
            "intermediate": [
                {
                    "text": "Describe a time you handled a conflict with a coworker.",
                    "follow_up": "What did you learn from that experience?",
                },
                {
                    "text": "How do you prioritize tasks when you have multiple deadlines?",
                    "follow_up": "What tools or methods do you use for time management?",
                },
                {
                    "text": "Tell me about a time you received constructive criticism.",
                    "follow_up": "How did you implement the feedback?",
                },
                {
                    "text": "Describe your ideal work environment.",
                    "follow_up": "How do you adapt when the environment isn't ideal?",
                },
                {
                    "text": "How do you handle stress and pressure at work?",
                    "follow_up": "Can you give a specific example?",
                },
            ],
            "advanced": [
                {
                    "text": "Describe a situation where you had to make a difficult decision with incomplete information.",
                    "follow_up": "How do you evaluate risk in ambiguous situations?",
                },
                {
                    "text": "Tell me about a time you influenced a team decision without formal authority.",
                    "follow_up": "What strategies do you use to build consensus?",
                },
                {
                    "text": "Describe how you have mentored or developed junior team members.",
                    "follow_up": "What is your philosophy on professional development?",
                },
                {
                    "text": "Tell me about a failure you experienced and how you recovered.",
                    "follow_up": "How has this experience shaped your approach to risk?",
                },
            ],
        },
    },
    "behavioral": {
        "general": {
            "beginner": [
                {
                    "text": "Tell me about a time you worked effectively as part of a team.",
                    "follow_up": "What was your specific role in the team?",
                },
                {
                    "text": "Describe a situation where you had to learn something quickly.",
                    "follow_up": "What strategies did you use to learn efficiently?",
                },
                {
                    "text": "Give an example of when you set a goal and achieved it.",
                    "follow_up": "What obstacles did you face along the way?",
                },
                {
                    "text": "Tell me about a time you helped a colleague.",
                    "follow_up": "How did this impact your own workload?",
                },
                {
                    "text": "Describe a project you are particularly proud of.",
                    "follow_up": "What would you do differently if you could do it again?",
                },
            ],
            "intermediate": [
                {
                    "text": "Describe a time you had to adapt to a significant change at work.",
                    "follow_up": "How do you generally respond to unexpected changes?",
                },
                {
                    "text": "Tell me about a time you disagreed with a team decision.",
                    "follow_up": "How did you handle the disagreement constructively?",
                },
                {
                    "text": "Give an example of when you took initiative beyond your job description.",
                    "follow_up": "What motivated you to go above and beyond?",
                },
                {
                    "text": "Describe a situation where you had to manage competing priorities.",
                    "follow_up": "How did you decide what to prioritize?",
                },
                {
                    "text": "Tell me about a time you received feedback that was hard to hear.",
                    "follow_up": "How did you apply that feedback moving forward?",
                },
            ],
            "advanced": [
                {
                    "text": "Describe a time you led a cross-functional initiative.",
                    "follow_up": "How did you align different stakeholder interests?",
                },
                {
                    "text": "Tell me about a situation where you had to deliver bad news to stakeholders.",
                    "follow_up": "How did you manage expectations afterwards?",
                },
                {
                    "text": "Give an example of when you identified and solved a systemic problem.",
                    "follow_up": "How did you measure the impact of your solution?",
                },
                {
                    "text": "Tell me about leading a team through a crisis or high-pressure situation.",
                    "follow_up": "What leadership principles guided your actions?",
                },
            ],
        },
    },
    "technical": {
        "data structures": {
            "beginner": [
                {
                    "text": "Explain the difference between an array and a linked list.",
                    "follow_up": "When would you choose one over the other?",
                },
                {
                    "text": "What is a stack and how does it work?",
                    "follow_up": "Can you name a real-world application of stacks?",
                },
                {
                    "text": "Describe what a hash table is and how it handles collisions.",
                    "follow_up": "What is the time complexity of hash table operations?",
                },
                {
                    "text": "What is a queue? Explain FIFO ordering.",
                    "follow_up": "How would you implement a queue using two stacks?",
                },
                {
                    "text": "What is a binary tree? How does it differ from a binary search tree?",
                    "follow_up": "What are the traversal methods for a binary tree?",
                },
            ],
            "intermediate": [
                {
                    "text": "Explain how a balanced BST maintains O(log n) operations.",
                    "follow_up": "Compare AVL trees and Red-Black trees.",
                },
                {
                    "text": "Describe the implementation and use cases of a priority queue.",
                    "follow_up": "How is a heap used to implement a priority queue?",
                },
                {
                    "text": "Explain the trie data structure and its advantages for string operations.",
                    "follow_up": "What is the space complexity of a trie?",
                },
                {
                    "text": "How would you design an LRU cache?",
                    "follow_up": "What data structures would you combine and why?",
                },
                {
                    "text": "Explain graph representation methods and their trade-offs.",
                    "follow_up": "When would you use an adjacency matrix vs adjacency list?",
                },
            ],
            "advanced": [
                {
                    "text": "Design a data structure that supports insert, delete, and getRandom in O(1).",
                    "follow_up": "How would you handle duplicates?",
                },
                {
                    "text": "Explain B-trees and their use in database indexing.",
                    "follow_up": "How does a B+ tree differ and why is it preferred for disk storage?",
                },
                {
                    "text": "Describe skip lists and their probabilistic guarantees.",
                    "follow_up": "How do skip lists compare to balanced BSTs?",
                },
                {
                    "text": "Explain consistent hashing and its applications in distributed systems.",
                    "follow_up": "How do virtual nodes improve load balancing?",
                },
            ],
        },
        "algorithms": {
            "beginner": [
                {
                    "text": "Explain the difference between linear search and binary search.",
                    "follow_up": "What are the prerequisites for binary search?",
                },
                {
                    "text": "Describe how bubble sort works and its time complexity.",
                    "follow_up": "Why is bubble sort rarely used in practice?",
                },
                {
                    "text": "What is recursion? Give an example of a recursive algorithm.",
                    "follow_up": "What are the risks of deep recursion?",
                },
                {
                    "text": "Explain Big O notation and why it matters.",
                    "follow_up": "What is the difference between O(n) and O(n log n)?",
                },
                {
                    "text": "How does a breadth-first search work on a graph?",
                    "follow_up": "What problems is BFS well-suited for?",
                },
            ],
            "intermediate": [
                {
                    "text": "Explain dynamic programming and when to use it.",
                    "follow_up": "Walk through the knapsack problem approach.",
                },
                {
                    "text": "Describe the merge sort algorithm and prove its time complexity.",
                    "follow_up": "How does merge sort compare to quicksort in practice?",
                },
                {
                    "text": "Explain Dijkstra's algorithm for shortest paths.",
                    "follow_up": "When does Dijkstra's algorithm fail? What alternatives exist?",
                },
                {
                    "text": "What is the two-pointer technique? Give an example.",
                    "follow_up": "How does sliding window differ from two pointers?",
                },
                {
                    "text": "Explain backtracking with the N-Queens problem.",
                    "follow_up": "How do you prune the search space effectively?",
                },
            ],
            "advanced": [
                {
                    "text": "Explain amortized analysis with examples from common data structures.",
                    "follow_up": "Compare aggregate, accounting, and potential methods.",
                },
                {
                    "text": "Describe the A* algorithm and how the heuristic affects performance.",
                    "follow_up": "What properties must the heuristic satisfy for optimality?",
                },
                {
                    "text": "Explain the concept of NP-completeness and give examples.",
                    "follow_up": "How do you approach NP-hard problems in practice?",
                },
                {
                    "text": "Design an algorithm for finding strongly connected components.",
                    "follow_up": "Compare Tarjan's and Kosaraju's algorithms.",
                },
                {
                    "text": "Explain the Floyd-Warshall algorithm and its applications.",
                    "follow_up": "How would you detect negative cycles?",
                },
            ],
        },
        "python": {
            "beginner": [
                {
                    "text": "Explain the difference between a list and a tuple in Python.",
                    "follow_up": "When would you choose a tuple over a list?",
                },
                {
                    "text": "What are Python decorators and how do they work?",
                    "follow_up": "Write a simple decorator that logs function calls.",
                },
                {
                    "text": "Explain list comprehensions and generator expressions.",
                    "follow_up": "When would you prefer a generator over a list comprehension?",
                },
                {
                    "text": "What is the GIL in Python and how does it affect concurrency?",
                    "follow_up": "How do you achieve parallelism in Python?",
                },
                {
                    "text": "Explain the difference between shallow copy and deep copy.",
                    "follow_up": "When might you encounter issues with shallow copies?",
                },
            ],
            "intermediate": [
                {
                    "text": "Explain Python's memory management and garbage collection.",
                    "follow_up": "What are reference cycles and how does Python handle them?",
                },
                {
                    "text": "Describe async/await in Python and the event loop.",
                    "follow_up": "When should you use asyncio vs threading vs multiprocessing?",
                },
                {
                    "text": "Explain metaclasses in Python and when you would use them.",
                    "follow_up": "How do class decorators compare to metaclasses?",
                },
                {
                    "text": "What are context managers and how do you implement one?",
                    "follow_up": "Explain the contextlib module and its utilities.",
                },
                {
                    "text": "Describe Python's descriptor protocol.",
                    "follow_up": "How do properties use descriptors under the hood?",
                },
            ],
            "advanced": [
                {
                    "text": "Explain Python's import system and module resolution.",
                    "follow_up": "How do you handle circular imports?",
                },
                {
                    "text": "Describe how to profile and optimize Python code.",
                    "follow_up": "What tools do you use for memory profiling?",
                },
                {
                    "text": "Explain the internals of Python's dict implementation.",
                    "follow_up": "How did the dict implementation change in Python 3.6+?",
                },
                {
                    "text": "Design a thread-safe singleton pattern in Python.",
                    "follow_up": "What are the pitfalls of singletons in testing?",
                },
                {
                    "text": "Explain how to build a custom async iterator in Python.",
                    "follow_up": "What are async generators and how do they differ?",
                },
            ],
        },
        "javascript": {
            "beginner": [
                {
                    "text": "Explain the difference between var, let, and const.",
                    "follow_up": "What is hoisting in JavaScript?",
                },
                {
                    "text": "What is a closure in JavaScript? Give an example.",
                    "follow_up": "How are closures used in practice?",
                },
                {
                    "text": "Explain the event loop in JavaScript.",
                    "follow_up": "What is the difference between microtasks and macrotasks?",
                },
                {
                    "text": "What is the difference between == and === in JavaScript?",
                    "follow_up": "What type coercion rules does == apply?",
                },
                {
                    "text": "Explain prototypal inheritance in JavaScript.",
                    "follow_up": "How does class syntax relate to prototypes?",
                },
            ],
            "intermediate": [
                {
                    "text": "Explain Promises and the async/await pattern.",
                    "follow_up": "How do you handle errors in async/await?",
                },
                {
                    "text": "What is the module system in JavaScript? Compare CommonJS and ES modules.",
                    "follow_up": "How does tree shaking work with ES modules?",
                },
                {
                    "text": "Explain the this keyword and its binding rules.",
                    "follow_up": "How do arrow functions affect this binding?",
                },
                {
                    "text": "Describe the Observer pattern and its use in JavaScript.",
                    "follow_up": "How does the EventEmitter pattern relate?",
                },
                {
                    "text": "What are WeakMap and WeakSet? When would you use them?",
                    "follow_up": "How do they help with memory management?",
                },
            ],
            "advanced": [
                {
                    "text": "Explain the JavaScript engine's optimization techniques (V8).",
                    "follow_up": "What is hidden class optimization?",
                },
                {
                    "text": "Describe how to implement a reactive state management system.",
                    "follow_up": "Compare Proxy-based reactivity with getter/setter approaches.",
                },
                {
                    "text": "Explain SharedArrayBuffer and Atomics for multi-threaded JS.",
                    "follow_up": "What synchronization primitives are available?",
                },
                {
                    "text": "Design a custom bundler's module resolution algorithm.",
                    "follow_up": "How do you handle circular dependencies?",
                },
                {
                    "text": "Explain the Proxy and Reflect APIs with practical use cases.",
                    "follow_up": "How would you implement an ORM using Proxy?",
                },
            ],
        },
        "react": {
            "beginner": [
                {
                    "text": "Explain the virtual DOM and how React uses it.",
                    "follow_up": "How does reconciliation work in React?",
                },
                {
                    "text": "What are React hooks? Explain useState and useEffect.",
                    "follow_up": "What are the rules of hooks?",
                },
                {
                    "text": "Explain props vs state in React.",
                    "follow_up": "When should you lift state up?",
                },
                {
                    "text": "What is JSX and how does it get transformed?",
                    "follow_up": "Can you use React without JSX?",
                },
                {
                    "text": "Explain component lifecycle in React.",
                    "follow_up": "How do hooks map to lifecycle methods?",
                },
            ],
            "intermediate": [
                {
                    "text": "Explain React's context API and when to use it.",
                    "follow_up": "What are the performance implications of context?",
                },
                {
                    "text": "How do you optimize React component performance?",
                    "follow_up": "Explain React.memo, useMemo, and useCallback.",
                },
                {
                    "text": "Describe error boundaries in React.",
                    "follow_up": "What errors do error boundaries NOT catch?",
                },
                {
                    "text": "Explain code splitting and lazy loading in React.",
                    "follow_up": "How does React.lazy work with Suspense?",
                },
                {
                    "text": "What is React's concurrent mode and what problems does it solve?",
                    "follow_up": "How do transitions work in React 18?",
                },
            ],
            "advanced": [
                {
                    "text": "Explain React Server Components and their benefits.",
                    "follow_up": "How do RSCs interact with client components?",
                },
                {
                    "text": "Design a scalable state management architecture for a large React app.",
                    "follow_up": "Compare Redux, Zustand, and Jotai approaches.",
                },
                {
                    "text": "Explain React's fiber architecture and scheduling.",
                    "follow_up": "How does time-slicing improve perceived performance?",
                },
                {
                    "text": "How would you implement a virtual scroll for 100k+ items in React?",
                    "follow_up": "What measurement strategies handle variable-height items?",
                },
                {
                    "text": "Design a compound component pattern with full TypeScript support.",
                    "follow_up": "How do you handle complex shared state in compound components?",
                },
            ],
        },
        "general": {
            "beginner": [
                {
                    "text": "Explain the difference between HTTP and HTTPS.",
                    "follow_up": "How does TLS/SSL work?",
                },
                {
                    "text": "What is REST and what are its principles?",
                    "follow_up": "How does REST differ from GraphQL?",
                },
                {
                    "text": "What is the difference between SQL and NoSQL databases?",
                    "follow_up": "When would you choose one over the other?",
                },
                {
                    "text": "Explain what an API is and how it works.",
                    "follow_up": "What makes a good API design?",
                },
            ],
            "intermediate": [
                {
                    "text": "Explain microservices architecture and its trade-offs.",
                    "follow_up": "How do you handle inter-service communication?",
                },
                {
                    "text": "Describe SOLID principles with examples.",
                    "follow_up": "Which principle do you find most impactful?",
                },
                {
                    "text": "Explain caching strategies and cache invalidation.",
                    "follow_up": "What is the cache stampede problem?",
                },
                {
                    "text": "What are design patterns? Explain three commonly used ones.",
                    "follow_up": "When can design patterns become anti-patterns?",
                },
            ],
            "advanced": [
                {
                    "text": "Design a system for handling 1 million concurrent users.",
                    "follow_up": "How do you identify and resolve bottlenecks?",
                },
                {
                    "text": "Explain the CAP theorem and its implications for distributed systems.",
                    "follow_up": "How do modern databases navigate CAP trade-offs?",
                },
                {
                    "text": "Describe event-driven architecture and event sourcing.",
                    "follow_up": "How do you handle eventual consistency?",
                },
                {
                    "text": "Design an observability stack for a microservices platform.",
                    "follow_up": "How do you correlate traces across services?",
                },
            ],
        },
    },
    "custom": {
        "general": {
            "beginner": [
                {
                    "text": "Tell me about a project you have worked on recently.",
                    "follow_up": "What challenges did you face?",
                },
                {
                    "text": "What technologies are you most comfortable with?",
                    "follow_up": "How do you stay updated with new technologies?",
                },
                {
                    "text": "Describe your development workflow.",
                    "follow_up": "How do you ensure code quality?",
                },
                {
                    "text": "What interests you about this particular role?",
                    "follow_up": "How does it align with your career goals?",
                },
            ],
            "intermediate": [
                {
                    "text": "Describe a technical challenge you solved creatively.",
                    "follow_up": "What alternatives did you consider?",
                },
                {
                    "text": "How do you approach debugging complex issues?",
                    "follow_up": "What tools and techniques do you use?",
                },
                {
                    "text": "Tell me about a time you improved a system's performance.",
                    "follow_up": "How did you measure the improvement?",
                },
                {
                    "text": "How do you handle technical debt in a project?",
                    "follow_up": "How do you balance new features vs. refactoring?",
                },
            ],
            "advanced": [
                {
                    "text": "How would you architect a new system from scratch for your domain?",
                    "follow_up": "What trade-offs would you make and why?",
                },
                {
                    "text": "How do you ensure security in applications you build?",
                    "follow_up": "What security incidents have you dealt with?",
                },
                {
                    "text": "Tell me about a time you mentored a team through a complex technical challenge.",
                    "follow_up": "How did you balance teaching with delivery timelines?",
                },
                {
                    "text": "How do you approach system design for scalability and reliability?",
                    "follow_up": "What failure modes do you plan for?",
                },
            ],
        },
    },
}
