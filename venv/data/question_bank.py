QUESTION_BANK = {
    "Software Developer": {
        1: [
            ("What is the time complexity of binary search?", "O(log n)"),
            ("What is the difference between an array and a linked list?", "Arrays use contiguous memory; linked lists use connected nodes"),
            ("What is a stack data structure?", "LIFO (Last In First Out) data structure"),
            ("What is the purpose of version control?", "Track code changes over time"),
            ("What is a compiler?", "Translates high-level code to machine code"),
            ("What is debugging?", "Finding and fixing code errors"),
            ("What is a mutex?", "Lock mechanism for thread synchronization"),
            ("What is a deadlock?", "Processes waiting indefinitely for resources")
        ],
        2: [
            ("Explain dynamic programming.", "Breaking complex problems into simpler subproblems"),
            ("What is a race condition?", "Multiple threads accessing shared resources simultaneously"),
            ("What is the difference between BFS and DFS?", "BFS explores breadth-first; DFS explores depth-first"),
            ("What is dependency injection?", "Providing objects with their dependencies externally"),
            ("Explain the concept of recursion.", "Function calling itself to solve smaller instances"),
            ("What is unit testing?", "Testing individual components in isolation"),
            ("What is a semaphore?", "Variable controlling access to shared resources"),
            ("What is multithreading?", "Running multiple threads in a single process")
        ],
        3: [
            ("How does garbage collection work?", "Automatically identifies and removes unused objects from memory"),
            ("Explain memory management in low-level programming.", "Manual allocation and deallocation of memory resources"),
            ("What is the CAP theorem?", "Distributed systems can only guarantee two of: consistency, availability, partition tolerance"),
            ("Explain microservices architecture.", "Breaking applications into small, independent services"),
            ("What is an API?", "Interface for communication between software components"),
            ("What is latency?", "Delay in data transmission")
        ]
    },

    "Full Stack Developer": {
        1: [
            ("What is the difference between HTML and HTML5?", "HTML5 adds semantic elements and new APIs"),
            ("What is CSS Flexbox?", "A layout model for flexible designs"),
            ("What is the purpose of DOCTYPE in HTML?", "Declares the HTML version to browsers"),
            ("What is the box model in CSS?", "Content, padding, border, and margin"),
            ("What is JavaScript hoisting?", "Moving declarations to the top of their scope"),
            ("What is responsive design?", "Making websites adapt to different screen sizes"),
            ("What is a callback function?", "Function passed as an argument to another function"),
            ("What is middleware in Express.js?", "Functions that process requests before response")
        ],
        2: [
            ("How does React's virtual DOM work?", "Creates memory representation of UI to minimize DOM updates"),
            ("What is REST API?", "Web services standard using HTTP methods"),
            ("What is webpack?", "JavaScript bundler for browser use"),
            ("Explain JWT authentication.", "Uses encoded tokens for verification"),
            ("What is CORS?", "Controls cross-origin resource access"),
            ("What are React hooks?", "Functions for state and lifecycle in functional components"),
            ("What is SSR?", "Server-side rendering"),
            ("What is JSX?", "JavaScript XML syntax for React")
        ],
        3: [
            ("Explain Server-Side Rendering.", "Rendering pages on server for better load time and SEO"),
            ("How does Node.js event loop work?", "Manages asynchronous operations non-blockingly"),
            ("What is Redux and its flow?", "Central state management through actions and reducers"),
            ("Explain database sharding.", "Splitting databases across multiple servers"),
            ("What is a CDN?", "Content delivery network"),
            ("What is hydration in React?", "Attaching event listeners to server-rendered markup")
        ]
    },

    "Python Developer": {
        1: [
            ("What is the difference between list and tuple?", "Lists are mutable; tuples are immutable"),
            ("How do you define a function in Python?", "Using 'def' keyword"),
            ("What are Python decorators?", "Functions that modify other functions"),
            ("What is PIP in Python?", "Package installer"),
            ("What is a dictionary in Python?", "Key-value pair data structure"),
            ("What is list comprehension?", "Compact way to create lists in one line")
        ],
        2: [
            ("What are lambda functions?", "Anonymous single-expression functions"),
            ("How does Python memory management work?", "Reference counting and garbage collection"),
            ("What is the difference between methods and functions?", "Methods belong to objects; functions are independent"),
            ("What are generators in Python?", "Iterables created using 'yield'"),
            ("What is duck typing?", "Checking behavior rather than type"),
            ("Explain context managers.", "Resource handlers using 'with' statement")
        ],
        3: [
            ("What is the Global Interpreter Lock?", "Allows only one thread to execute Python bytecode at once"),
            ("Explain deep copy vs shallow copy.", "New objects recursively vs references to original objects"),
            ("How does asyncio work?", "Enables asynchronous I/O with coroutines"),
            ("What are metaclasses?", "Classes that create classes")
        ]
    },

    "AI/ML Developer": {
        1: [
            ("What is supervised learning?", "Training with labeled data"),
            ("What is the difference between classification and regression?", "Predicting categories vs continuous values"),
            ("What is overfitting?", "Model learning noise in training data"),
            ("What is feature scaling?", "Normalizing features to similar ranges"),
            ("What is a neural network?", "Computing system inspired by biological neurons"),
            ("What is cross-validation?", "Testing on different data subsets")
        ],
        2: [
            ("Explain gradient descent.", "Optimizing parameters by minimizing error gradually"),
            ("What is the difference between CNN and RNN?", "CNNs for spatial data; RNNs for sequences"),
            ("What is transfer learning?", "Reusing pre-trained models"),
            ("Explain reinforcement learning.", "Training through environment interaction and rewards"),
            ("What is backpropagation?", "Updating weights based on prediction errors"),
            ("What is ensemble learning?", "Combining multiple models")
        ],
        3: [
            ("Explain attention mechanism.", "Helps models focus on relevant input parts"),
            ("What is the transformer architecture?", "Uses self-attention for efficient sequence processing"),
            ("How does BERT work?", "Pre-trains on masked language modeling"),
            ("What is federated learning?", "Training across devices while keeping data private")
        ]
    },

    "Web Developer": {
        1: [
            ("What is CSS specificity?", "Determines which CSS rules apply"),
            ("What is semantic HTML?", "Using tags that describe their content"),
            ("What is event bubbling?", "Event propagation from child to parent elements"),
            ("What is localStorage?", "Browser data persistence"),
            ("What is a media query?", "CSS rules based on device characteristics"),
            ("What is the DOM?", "HTML as a tree structure for manipulation")
        ],
        2: [
            ("What is progressive rendering?", "Loading content gradually"),
            ("Explain async and defer in scripts.", "Controls script loading and execution timing"),
            ("What are service workers?", "Enable offline functionality and background tasks"),
            ("What is code splitting?", "Breaking JavaScript into smaller bundles"),
            ("What is tree shaking?", "Removing unused code from bundles"),
            ("What is CSS-in-JS?", "Writing CSS within JavaScript")
        ],
        3: [
            ("How does HTTP/2 work?", "Multiplexes requests and compresses headers"),
            ("Explain web workers.", "Background threads separate from UI"),
            ("What is WebAssembly?", "Running low-level code in browsers at near-native speed"),
            ("What is micro-frontend architecture?", "Independently deployable frontend features")
        ]
    }
}