"""Static seed data used by init_db() to populate default job roles,
role-specific skills, and career roadmaps when the database is empty.
"""

CORE_SKILLS_BY_ROLE = _core_skills_by_role = {
    "Software Engineering": {"Python", "Java", "Git", "Data Structures", "Algorithms", "SQL"},
    "Frontend Development": {"JavaScript", "React", "HTML", "CSS", "TypeScript", "Git"},
    "Backend Development": {"Python", "Node.js", "SQL", "REST APIs", "Docker", "Git"},
    "Data Science": {"Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Statistics"},
    "DevOps": {"Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git"},
    "Mobile Development": {"React Native", "Flutter", "Swift", "Kotlin", "Git", "REST APIs"},
    "Full Stack Development": {"JavaScript", "React", "Node.js", "Python", "SQL", "Git"},
    "Cybersecurity": {"Networking", "Linux", "Python", "SIEM", "Penetration Testing", "Encryption"},
}

DEFAULT_ROLES = default_roles = [
    ("Software Engineering", "Design, develop, and maintain software systems", "Engineering"),
    ("Frontend Development", "Build user interfaces and client-side applications", "Engineering"),
    ("Backend Development", "Develop server-side logic and APIs", "Engineering"),
    ("Data Science", "Analyze data and build machine learning models", "Data"),
    ("DevOps", "Manage infrastructure, CI/CD, and deployment", "Engineering"),
    ("Mobile Development", "Build mobile applications for iOS and Android", "Engineering"),
    ("Full Stack Development", "Develop both frontend and backend applications", "Engineering"),
    ("Cybersecurity", "Protect systems and networks from security threats", "Security"),
    ("Product Management", "Define product vision, strategy, and roadmap", "Product"),
    ("Business Analysis", "Analyze business needs and translate to technical requirements", "Business"),
    ("Technical Writing", "Create clear documentation for technical audiences", "Content"),
    ("IT Support", "Provide technical assistance and maintain IT systems", "Operations"),
    ("Network Administration", "Manage and maintain network infrastructure", "Operations"),
    ("Cloud Engineering", "Design and manage cloud-based infrastructure", "Engineering"),
    ("Data Engineering", "Build and maintain data pipelines and infrastructure", "Data"),
    ("Machine Learning", "Develop and deploy machine learning models", "Data"),
    ("Cloud Architecture", "Design scalable cloud solutions and architectures", "Engineering"),
    ("Web Development", "Build and maintain web applications", "Engineering"),
    ("UI/UX Design", "Design user interfaces and experiences", "Design"),
    ("Android Development", "Build applications for the Android platform", "Engineering"),
    ("iOS Development", "Build applications for the Apple ecosystem", "Engineering"),
    ("Quality Assurance", "Ensure software quality through testing", "Engineering"),
]

DEFAULT_ROLE_SKILLS = default_role_skills = {
    "Software Engineering": {
        "required": ["Python", "Java", "Git", "Data Structures", "Algorithms", "SQL"],
        "nice_to_have": ["OOP", "Testing", "CI/CD", "Docker", "REST APIs", "Linux", "Design Patterns", "Debugging", "Agile"],
    },
    "Frontend Development": {
        "required": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Git"],
        "nice_to_have": ["REST APIs", "Responsive Design", "Vue.js", "Next.js", "Redux", "Webpack", "Accessibility", "Figma", "Jest"],
    },
    "Backend Development": {
        "required": ["Python", "Node.js", "SQL", "REST APIs", "Docker", "Git"],
        "nice_to_have": ["PostgreSQL", "Linux", "Redis", "MongoDB", "FastAPI", "Flask", "Microservices", "Authentication", "Caching"],
    },
    "Data Science": {
        "required": ["Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Statistics"],
        "nice_to_have": ["R", "TensorFlow", "PyTorch", "Scikit-learn", "Data Visualization", "NLP", "Jupyter", "Feature Engineering", "A/B Testing"],
    },
    "DevOps": {
        "required": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git"],
        "nice_to_have": ["Terraform", "Ansible", "Jenkins", "Prometheus", "Grafana", "Nginx", "Bash", "Monitoring", "Load Balancing"],
    },
    "Mobile Development": {
        "required": ["React Native", "Flutter", "Swift", "Kotlin", "Git", "REST APIs"],
        "nice_to_have": ["Firebase", "UI/UX", "iOS", "Android", "State Management", "Testing", "Push Notifications", "App Store", "Performance"],
    },
    "Full Stack Development": {
        "required": ["JavaScript", "React", "Node.js", "Python", "SQL", "Git"],
        "nice_to_have": ["Docker", "REST APIs", "PostgreSQL", "MongoDB", "Redis", "TypeScript", "Express", "Authentication", "Deployment"],
    },
    "Cybersecurity": {
        "required": ["Networking", "Linux", "Python", "SIEM", "Penetration Testing", "Encryption"],
        "nice_to_have": ["Firewalls", "Compliance", "Incident Response", "Vulnerability Assessment", "Nmap", "Wireshark", "Cryptography", "Forensics", "Active Directory"],
    },
    "Product Management": {
        "required": ["Product Strategy", "Agile", "User Research", "Roadmapping", "Stakeholder Management", "Data Analysis"],
        "nice_to_have": ["SQL", "A/B Testing", "Jira", "Figma", "Market Research", "OKRs", "Go-to-Market", "Metrics", "Wireframing"],
    },
    "Business Analysis": {
        "required": ["Requirements Gathering", "SQL", "Process Modeling", "Stakeholder Management", "Data Analysis", "Documentation"],
        "nice_to_have": ["UML", "BPMN", "Jira", "Confluence", "Wireframing", "Agile", "Visio", "Python", "ETL"],
    },
    "Technical Writing": {
        "required": ["Documentation", "Markdown", "API Documentation", "Content Strategy", "Editing", "Grammar"],
        "nice_to_have": ["Git", "HTML", "DITA", "MadCap Flare", "Screenshots", "Video Tutorials", "Style Guides", "Information Architecture", "Localization"],
    },
    "IT Support": {
        "required": ["Windows", "Linux", "Networking", "Active Directory", "Troubleshooting", "Hardware"],
        "nice_to_have": ["Azure", "Office 365", "Scripting", "Virtualization", "Ticketing Systems", "Security", "CompTIA A+", "Remote Support", "Backup"],
    },
    "Network Administration": {
        "required": ["TCP/IP", "DNS", "DHCP", "Firewalls", "Linux", "Routing"],
        "nice_to_have": ["Cisco", "VLANs", "VPN", "Network Monitoring", "Cloud Networking", "Security", "Load Balancing", "Wireshark", "CompTIA Network+"],
    },
    "Cloud Engineering": {
        "required": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"],
        "nice_to_have": ["Azure", "GCP", "Ansible", "Monitoring", "Security", "Networking", "Serverless", "Infrastructure as Code", "Cost Optimization"],
    },
    "Data Engineering": {
        "required": ["Python", "SQL", "Apache Spark", "ETL", "Data Modeling", "AWS"],
        "nice_to_have": ["Airflow", "Kafka", "Redshift", "Snowflake", "dbt", "Hadoop", "Data Lake", "Delta Lake", "Data Quality"],
    },
    "Machine Learning": {
        "required": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "SQL", "Statistics"],
        "nice_to_have": ["Scikit-learn", "NLP", "Computer Vision", "MLOps", "Feature Engineering", "Deep Learning", "AWS SageMaker", "MLflow", "Docker"],
    },
    "Cloud Architecture": {
        "required": ["AWS", "Azure", "System Design", "Networking", "Security", "Terraform"],
        "nice_to_have": ["Microservices", "Serverless", "Containers", "Cost Optimization", "Disaster Recovery", "Compliance", "Load Balancing", "CDN", "Multi-Cloud"],
    },
    "Web Development": {
        "required": ["JavaScript", "HTML", "CSS", "React", "Node.js", "Git"],
        "nice_to_have": ["TypeScript", "Next.js", "PostgreSQL", "MongoDB", "Docker", "REST APIs", "Testing", "CI/CD", "Performance"],
    },
    "UI/UX Design": {
        "required": ["Figma", "User Research", "Wireframing", "Prototyping", "Interaction Design", "Usability Testing"],
        "nice_to_have": ["Adobe XD", "Sketch", "Design Systems", "HTML/CSS", "Accessibility", "Information Architecture", "User Personas", "Journey Mapping", "Motion Design"],
    },
    "Android Development": {
        "required": ["Kotlin", "Android Studio", "Jetpack Compose", "REST APIs", "Git", "Material Design"],
        "nice_to_have": ["Java", "Room DB", "Coroutines", "Retrofit", "MVVM", "Firebase", "Testing", "Play Store", "Push Notifications"],
    },
    "iOS Development": {
        "required": ["Swift", "SwiftUI", "UIKit", "REST APIs", "Git", "Xcode"],
        "nice_to_have": ["CoreData", "Combine", "ARKit", "Core ML", "App Store", "AutoLayout", "Networking", "Testing", "Performance"],
    },
    "Quality Assurance": {
        "required": ["Test Automation", "Selenium", "API Testing", "SQL", "Bug Tracking", "Agile"],
        "nice_to_have": ["Cypress", "Jest", "Postman", "CI/CD", "Performance Testing", "Security Testing", "Test Plans", "Regression Testing", "Jira"],
    },
}

DEFAULT_ROADMAPS = default_roadmaps = {
    "Software Engineering": {
        "title": "Software Engineering Career Path",
        "description": "Master the fundamentals of software engineering",
        "duration_weeks": 24,
        "steps": [
            {"step": 1, "title": "Programming Fundamentals", "description": "Learn core programming concepts", "duration_weeks": 4, "skills": "Python,OOP,Data Structures", "resources": "https://www.youtube.com/results?search_query=python+programming+fundamentals"},
            {"step": 2, "title": "Version Control", "description": "Master Git and collaboration workflows", "duration_weeks": 2, "skills": "Git,GitHub,Branching", "resources": "https://www.youtube.com/results?search_query=git+tutorial"},
            {"step": 3, "title": "Testing & Quality", "description": "Write reliable, tested code", "duration_weeks": 3, "skills": "Unit Testing,TDD,Debugging", "resources": "https://www.youtube.com/results?search_query=software+testing"},
            {"step": 4, "title": "System Design", "description": "Design scalable software systems", "duration_weeks": 5, "skills": "Architecture,Design Patterns,APIs", "resources": "https://www.youtube.com/results?search_query=system+design"},
        ]
    },
    "Frontend Development": {
        "title": "Frontend Developer Roadmap",
        "description": "Build modern, responsive web interfaces",
        "duration_weeks": 20,
        "steps": [
            {"step": 1, "title": "HTML & CSS", "description": "Master web fundamentals", "duration_weeks": 3, "skills": "HTML5,CSS3,Flexbox,Grid", "resources": "https://www.youtube.com/results?search_query=html+css+tutorial"},
            {"step": 2, "title": "JavaScript", "description": "Learn modern JavaScript", "duration_weeks": 4, "skills": "JavaScript,ES6+,DOM", "resources": "https://www.youtube.com/results?search_query=javascript+tutorial"},
            {"step": 3, "title": "React", "description": "Build component-based UIs", "duration_weeks": 5, "skills": "React,Hooks,State Management", "resources": "https://www.youtube.com/results?search_query=react+tutorial"},
            {"step": 4, "title": "Performance", "description": "Optimize web applications", "duration_weeks": 3, "skills": "Lighthouse,Webpack,Optimization", "resources": "https://www.youtube.com/results?search_query=web+performance"},
        ]
    },
    "Backend Development": {
        "title": "Backend Developer Roadmap",
        "description": "Build robust server-side applications",
        "duration_weeks": 22,
        "steps": [
            {"step": 1, "title": "Programming Basics", "description": "Learn a backend language", "duration_weeks": 4, "skills": "Python,Node.js,Go", "resources": "https://www.youtube.com/results?search_query=backend+programming"},
            {"step": 2, "title": "Databases", "description": "Master data persistence", "duration_weeks": 4, "skills": "SQL,PostgreSQL,MongoDB", "resources": "https://www.youtube.com/results?search_query=database+tutorial"},
            {"step": 3, "title": "APIs", "description": "Design and build APIs", "duration_weeks": 4, "skills": "REST,GraphQL,Authentication", "resources": "https://www.youtube.com/results?search_query=rest+api+tutorial"},
            {"step": 4, "title": "DevOps Basics", "description": "Deploy and scale applications", "duration_weeks": 4, "skills": "Docker,Linux,CI/CD", "resources": "https://www.youtube.com/results?search_query=devops+tutorial"},
        ]
    },
    "Data Science": {
        "title": "Data Science Career Path",
        "description": "Analyze data and build ML models",
        "duration_weeks": 26,
        "steps": [
            {"step": 1, "title": "Python for Data", "description": "Learn data manipulation", "duration_weeks": 4, "skills": "Python,Pandas,NumPy", "resources": "https://www.youtube.com/results?search_query=python+data+science"},
            {"step": 2, "title": "Statistics", "description": "Master statistical concepts", "duration_weeks": 4, "skills": "Statistics,Probability,Hypothesis Testing", "resources": "https://www.youtube.com/results?search_query=statistics+for+data+science"},
            {"step": 3, "title": "Machine Learning", "description": "Build predictive models", "duration_weeks": 6, "skills": "Scikit-learn,ML Algorithms,Model Evaluation", "resources": "https://www.youtube.com/results?search_query=machine+learning+tutorial"},
            {"step": 4, "title": "Deep Learning", "description": "Neural networks and advanced ML", "duration_weeks": 6, "skills": "TensorFlow,PyTorch,Neural Networks", "resources": "https://www.youtube.com/results?search_query=deep+learning+tutorial"},
        ]
    },
    "DevOps": {
        "title": "DevOps Engineer Roadmap",
        "description": "Master infrastructure and deployment",
        "duration_weeks": 24,
        "steps": [
            {"step": 1, "title": "Linux & Networking", "description": "Master OS fundamentals", "duration_weeks": 4, "skills": "Linux,Bash,Networking", "resources": "https://www.youtube.com/results?search_query=linux+tutorial"},
            {"step": 2, "title": "Containers", "description": "Learn containerization", "duration_weeks": 4, "skills": "Docker,Kubernetes,Container Orchestration", "resources": "https://www.youtube.com/results?search_query=docker+kubernetes+tutorial"},
            {"step": 3, "title": "CI/CD", "description": "Automate deployments", "duration_weeks": 4, "skills": "GitHub Actions,Jenkins,Pipelines", "resources": "https://www.youtube.com/results?search_query=ci+cd+tutorial"},
            {"step": 4, "title": "Cloud", "description": "Master cloud platforms", "duration_weeks": 5, "skills": "AWS,Azure,GCP,Terraform", "resources": "https://www.youtube.com/results?search_query=aws+cloud+tutorial"},
        ]
    },
    "Mobile Development": {
        "title": "Mobile Developer Roadmap",
        "description": "Build cross-platform mobile apps",
        "duration_weeks": 22,
        "steps": [
            {"step": 1, "title": "Mobile Fundamentals", "description": "Learn mobile development concepts", "duration_weeks": 3, "skills": "Mobile UX,App Architecture,State", "resources": "https://www.youtube.com/results?search_query=mobile+development+basics"},
            {"step": 2, "title": "React Native / Flutter", "description": "Build cross-platform apps", "duration_weeks": 6, "skills": "React Native,Flutter,Dart", "resources": "https://www.youtube.com/results?search_query=react+native+tutorial"},
            {"step": 3, "title": "Backend Integration", "description": "Connect to APIs and services", "duration_weeks": 4, "skills": "REST APIs,Firebase,Authentication", "resources": "https://www.youtube.com/results?search_query=mobile+backend+integration"},
            {"step": 4, "title": "Publishing", "description": "Deploy to app stores", "duration_weeks": 3, "skills": "App Store,Play Store,App Optimization", "resources": "https://www.youtube.com/results?search_query=app+store+publishing"},
        ]
    },
    "Full Stack Development": {
        "title": "Full Stack Developer Roadmap",
        "description": "Master both frontend and backend",
        "duration_weeks": 28,
        "steps": [
            {"step": 1, "title": "Frontend Basics", "description": "Learn HTML, CSS, JavaScript", "duration_weeks": 4, "skills": "HTML,CSS,JavaScript,React", "resources": "https://www.youtube.com/results?search_query=frontend+web+development"},
            {"step": 2, "title": "Backend Basics", "description": "Learn server-side programming", "duration_weeks": 4, "skills": "Node.js,Express,REST APIs", "resources": "https://www.youtube.com/results?search_query=nodejs+backend+tutorial"},
            {"step": 3, "title": "Databases", "description": "Master data storage", "duration_weeks": 4, "skills": "SQL,MongoDB,Redis", "resources": "https://www.youtube.com/results?search_query=database+tutorial"},
            {"step": 4, "title": "Full Stack Projects", "description": "Build complete applications", "duration_weeks": 6, "skills": "Authentication,Deployment,Testing", "resources": "https://www.youtube.com/results?search_query=full+stack+project"},
        ]
    },
    "Cybersecurity": {
        "title": "Cybersecurity Career Path",
        "description": "Protect systems from security threats",
        "duration_weeks": 26,
        "steps": [
            {"step": 1, "title": "Networking Security", "description": "Master network fundamentals", "duration_weeks": 4, "skills": "TCP/IP,Firewalls,VPNs", "resources": "https://www.youtube.com/results?search_query=network+security+tutorial"},
            {"step": 2, "title": "Operating Systems", "description": "Secure Linux and Windows", "duration_weeks": 4, "skills": "Linux,Windows,Hardening", "resources": "https://www.youtube.com/results?search_query=linux+security"},
            {"step": 3, "title": "Ethical Hacking", "description": "Learn penetration testing", "duration_weeks": 6, "skills": "Kali Linux,Metasploit,Nmap", "resources": "https://www.youtube.com/results?search_query=ethical+hacking+tutorial"},
            {"step": 4, "title": "Security Operations", "description": "Implement security frameworks", "duration_weeks": 5, "skills": "SIEM,Incident Response,Compliance", "resources": "https://www.youtube.com/results?search_query=security+operations"},
        ]
    },
    "Product Management": {
        "title": "Product Management Career Path",
        "description": "Lead product strategy and execution",
        "duration_weeks": 20,
        "steps": [
            {"step": 1, "title": "Product Fundamentals", "description": "Learn core PM concepts", "duration_weeks": 3, "skills": "Product Strategy,Market Research,User Personas", "resources": "https://www.youtube.com/results?search_query=product+management+basics"},
            {"step": 2, "title": "Discovery & Research", "description": "Master user research methods", "duration_weeks": 4, "skills": "User Interviews,A/B Testing,Data Analysis", "resources": "https://www.youtube.com/results?search_query=user+research+product"},
            {"step": 3, "title": "Execution & Delivery", "description": "Ship products effectively", "duration_weeks": 4, "skills": "Agile,Scrum,Jira,Roadmapping", "resources": "https://www.youtube.com/results?search_query=agile+product+management"},
            {"step": 4, "title": "Growth & Strategy", "description": "Drive product growth", "duration_weeks": 5, "skills": "OKRs,Go-to-Market,Metrics,Stakeholder Management", "resources": "https://www.youtube.com/results?search_query=product+growth+strategy"},
        ]
    },
    "Business Analysis": {
        "title": "Business Analysis Career Path",
        "description": "Bridge business needs and technical solutions",
        "duration_weeks": 18,
        "steps": [
            {"step": 1, "title": "BA Fundamentals", "description": "Learn requirements engineering", "duration_weeks": 3, "skills": "Requirements Gathering,Documentation,Stakeholder Analysis", "resources": "https://www.youtube.com/results?search_query=business+analysis+basics"},
            {"step": 2, "title": "Process Modeling", "description": "Map business processes", "duration_weeks": 3, "skills": "UML,BPMN,Flowcharts,Process Mapping", "resources": "https://www.youtube.com/results?search_query=process+modeling+business"},
            {"step": 3, "title": "Data & Analysis", "description": "Use data for decision making", "duration_weeks": 4, "skills": "SQL,Data Analysis,Excel,Wireframing", "resources": "https://www.youtube.com/results?search_query=data+analysis+business"},
            {"step": 4, "title": "Advanced BA", "description": "Master strategic analysis", "duration_weeks": 4, "skills": "ETL,Confluence,Jira,Agile", "resources": "https://www.youtube.com/results?search_query=advanced+business+analysis"},
        ]
    },
    "Technical Writing": {
        "title": "Technical Writing Career Path",
        "description": "Create clear, effective technical documentation",
        "duration_weeks": 16,
        "steps": [
            {"step": 1, "title": "Writing Fundamentals", "description": "Master technical writing basics", "duration_weeks": 3, "skills": "Documentation,Markdown,Editing,Grammar", "resources": "https://www.youtube.com/results?search_query=technical+writing+basics"},
            {"step": 2, "title": "API Documentation", "description": "Write API references and guides", "duration_weeks": 3, "skills": "API Documentation,OpenAPI,Swagger,Code Samples", "resources": "https://www.youtube.com/results?search_query=api+documentation"},
            {"step": 3, "title": "Content Strategy", "description": "Plan and organize documentation", "duration_weeks": 4, "skills": "Content Strategy,Information Architecture,Style Guides", "resources": "https://www.youtube.com/results?search_query=content+strategy+technical"},
            {"step": 4, "title": "Advanced Topics", "description": "Specialize in advanced documentation", "duration_weeks": 4, "skills": "DITA,Localization,Video Tutorials,Screenshots", "resources": "https://www.youtube.com/results?search_query=advanced+technical+writing"},
        ]
    },
    "IT Support": {
        "title": "IT Support Career Path",
        "description": "Provide technical assistance and maintain systems",
        "duration_weeks": 18,
        "steps": [
            {"step": 1, "title": "Hardware & OS", "description": "Master computer fundamentals", "duration_weeks": 3, "skills": "Hardware,Windows,Linux,CompTIA A+", "resources": "https://www.youtube.com/results?search_query=it+support+hardware"},
            {"step": 2, "title": "Networking", "description": "Learn network basics", "duration_weeks": 3, "skills": "Networking,TCP/IP,DNS,DHCP", "resources": "https://www.youtube.com/results?search_query=it+networking+basics"},
            {"step": 3, "title": "Active Directory & Cloud", "description": "Manage users and cloud services", "duration_weeks": 4, "skills": "Active Directory,Office 365,Azure,Remote Support", "resources": "https://www.youtube.com/results?search_query=active+directory+tutorial"},
            {"step": 4, "title": "Security & Scripting", "description": "Automate and secure IT", "duration_weeks": 4, "skills": "Security,Scripting,Backup,Ticketing Systems", "resources": "https://www.youtube.com/results?search_query=it+security+scripting"},
        ]
    },
    "Network Administration": {
        "title": "Network Administration Career Path",
        "description": "Manage and secure network infrastructure",
        "duration_weeks": 22,
        "steps": [
            {"step": 1, "title": "Networking Fundamentals", "description": "Master network protocols and concepts", "duration_weeks": 4, "skills": "TCP/IP,OSI Model,Subnetting,DNS", "resources": "https://www.youtube.com/results?search_query=networking+fundamentals"},
            {"step": 2, "title": "Routers & Switches", "description": "Configure network devices", "duration_weeks": 4, "skills": "Cisco,Routing,Switching,VLANs", "resources": "https://www.youtube.com/results?search_query=cisco+routing+switching"},
            {"step": 3, "title": "Security", "description": "Secure network infrastructure", "duration_weeks": 4, "skills": "Firewalls,VPN,Network Monitoring,Wireshark", "resources": "https://www.youtube.com/results?search_query=network+security+firewall"},
            {"step": 4, "title": "Cloud & Advanced", "description": "Modern network management", "duration_weeks": 5, "skills": "Cloud Networking,Load Balancing,CompTIA Network+", "resources": "https://www.youtube.com/results?search_query=cloud+networking"},
        ]
    },
    "Cloud Engineering": {
        "title": "Cloud Engineering Career Path",
        "description": "Build and manage cloud infrastructure",
        "duration_weeks": 24,
        "steps": [
            {"step": 1, "title": "Cloud Fundamentals", "description": "Learn cloud computing concepts", "duration_weeks": 3, "skills": "AWS,Azure,GCP,Cloud Concepts", "resources": "https://www.youtube.com/results?search_query=cloud+computing+basics"},
            {"step": 2, "title": "Containers & Orchestration", "description": "Master containerization", "duration_weeks": 4, "skills": "Docker,Kubernetes,Container Registry", "resources": "https://www.youtube.com/results?search_query=docker+kubernetes+tutorial"},
            {"step": 3, "title": "Infrastructure as Code", "description": "Automate infrastructure", "duration_weeks": 4, "skills": "Terraform,Ansible,CloudFormation", "resources": "https://www.youtube.com/results?search_query=terraform+iac"},
            {"step": 4, "title": "Monitoring & Security", "description": "Secure and monitor cloud", "duration_weeks": 5, "skills": "Monitoring,Security,CI/CD,Cost Optimization", "resources": "https://www.youtube.com/results?search_query=cloud+monitoring+security"},
        ]
    },
    "Data Engineering": {
        "title": "Data Engineering Career Path",
        "description": "Build robust data pipelines and infrastructure",
        "duration_weeks": 24,
        "steps": [
            {"step": 1, "title": "Programming & SQL", "description": "Master data fundamentals", "duration_weeks": 4, "skills": "Python,SQL,Data Modeling,ETL", "resources": "https://www.youtube.com/results?search_query=data+engineering+basics"},
            {"step": 2, "title": "Big Data Technologies", "description": "Learn distributed processing", "duration_weeks": 5, "skills": "Apache Spark,Hadoop,Data Lake", "resources": "https://www.youtube.com/results?search_query=apache+spark+big+data"},
            {"step": 3, "title": "Pipeline Orchestration", "description": "Build automated pipelines", "duration_weeks": 4, "skills": "Airflow,Kafka,Delta Lake", "resources": "https://www.youtube.com/results?search_query=apache+airflow+tutorial"},
            {"step": 4, "title": "Cloud & Warehousing", "description": "Deploy to cloud data platforms", "duration_weeks": 5, "skills": "Snowflake,Redshift,dbt,Data Quality", "resources": "https://www.youtube.com/results?search_query=snowflake+data+warehouse"},
        ]
    },
    "Machine Learning": {
        "title": "Machine Learning Career Path",
        "description": "Develop and deploy intelligent systems",
        "duration_weeks": 26,
        "steps": [
            {"step": 1, "title": "ML Foundations", "description": "Learn core ML concepts", "duration_weeks": 4, "skills": "Python,Statistics,Linear Algebra,ML Algorithms", "resources": "https://www.youtube.com/results?search_query=machine+learning+fundamentals"},
            {"step": 2, "title": "Deep Learning", "description": "Master neural networks", "duration_weeks": 5, "skills": "TensorFlow,PyTorch,Neural Networks,CNN", "resources": "https://www.youtube.com/results?search_query=deep+learning+tutorial"},
            {"step": 3, "title": "Specializations", "description": "Specialize in NLP or CV", "duration_weeks": 5, "skills": "NLP,Computer Vision,Transformers,Feature Engineering", "resources": "https://www.youtube.com/results?search_query=nlp+computer+vision"},
            {"step": 4, "title": "MLOps & Deployment", "description": "Deploy models to production", "duration_weeks": 5, "skills": "MLOps,MLflow,Docker,AWS SageMaker", "resources": "https://www.youtube.com/results?search_query=mlops+deployment"},
        ]
    },
    "Cloud Architecture": {
        "title": "Cloud Architecture Career Path",
        "description": "Design scalable, resilient cloud solutions",
        "duration_weeks": 26,
        "steps": [
            {"step": 1, "title": "Architecture Fundamentals", "description": "Learn system design principles", "duration_weeks": 4, "skills": "System Design,Networking,Security,Architecture Patterns", "resources": "https://www.youtube.com/results?search_query=cloud+architecture+fundamentals"},
            {"step": 2, "title": "Multi-Cloud Mastery", "description": "Master AWS, Azure, and GCP", "duration_weeks": 5, "skills": "AWS,Azure,GCP,Multi-Cloud", "resources": "https://www.youtube.com/results?search_query=multi+cloud+architecture"},
            {"step": 3, "title": "Advanced Patterns", "description": "Implement advanced architectures", "duration_weeks": 5, "skills": "Microservices,Serverless,Containers,CDN", "resources": "https://www.youtube.com/results?search_query=microservices+serverless+architecture"},
            {"step": 4, "title": "Governance & Optimization", "description": "Optimize cost and compliance", "duration_weeks": 5, "skills": "Cost Optimization,Compliance,Disaster Recovery,Load Balancing", "resources": "https://www.youtube.com/results?search_query=cloud+cost+optimization"},
        ]
    },
    "Web Development": {
        "title": "Web Development Career Path",
        "description": "Build modern, responsive web applications",
        "duration_weeks": 22,
        "steps": [
            {"step": 1, "title": "Web Fundamentals", "description": "Master HTML, CSS, and JavaScript", "duration_weeks": 3, "skills": "HTML,CSS,JavaScript,Responsive Design", "resources": "https://www.youtube.com/results?search_query=web+development+basics"},
            {"step": 2, "title": "Frontend Frameworks", "description": "Learn React and modern tools", "duration_weeks": 4, "skills": "React,TypeScript,Next.js,State Management", "resources": "https://www.youtube.com/results?search_query=react+web+development"},
            {"step": 3, "title": "Backend & Databases", "description": "Add server-side capabilities", "duration_weeks": 4, "skills": "Node.js,PostgreSQL,MongoDB,REST APIs", "resources": "https://www.youtube.com/results?search_query=nodejs+backend+tutorial"},
            {"step": 4, "title": "Deployment & Testing", "description": "Ship production applications", "duration_weeks": 3, "skills": "Docker,CI/CD,Testing,Performance", "resources": "https://www.youtube.com/results?search_query=web+app+deployment"},
        ]
    },
    "UI/UX Design": {
        "title": "UI/UX Design Career Path",
        "description": "Create intuitive, beautiful user experiences",
        "duration_weeks": 20,
        "steps": [
            {"step": 1, "title": "Design Fundamentals", "description": "Learn core design principles", "duration_weeks": 3, "skills": "Color Theory,Typography,Layout,Design Principles", "resources": "https://www.youtube.com/results?search_query=ui+ux+design+fundamentals"},
            {"step": 2, "title": "UX Research", "description": "Understand your users", "duration_weeks": 3, "skills": "User Research,User Personas,Journey Mapping,Usability Testing", "resources": "https://www.youtube.com/results?search_query=ux+research+methods"},
            {"step": 3, "title": "Prototyping Tools", "description": "Master design tools", "duration_weeks": 4, "skills": "Figma,Adobe XD,Prototyping,Wireframing", "resources": "https://www.youtube.com/results?search_query=figma+tutorial"},
            {"step": 4, "title": "Design Systems", "description": "Build scalable design systems", "duration_weeks": 4, "skills": "Design Systems,Component Libraries,Accessibility,Interaction Design", "resources": "https://www.youtube.com/results?search_query=design+systems"},
        ]
    },
    "Android Development": {
        "title": "Android Development Career Path",
        "description": "Build native Android applications",
        "duration_weeks": 22,
        "steps": [
            {"step": 1, "title": "Kotlin Basics", "description": "Learn the Android language", "duration_weeks": 3, "skills": "Kotlin,OOP,Data Types,Functions", "resources": "https://www.youtube.com/results?search_query=kotlin+android+tutorial"},
            {"step": 2, "title": "Android UI", "description": "Build beautiful interfaces", "duration_weeks": 4, "skills": "Android Studio,Jetpack Compose,Material Design,XML", "resources": "https://www.youtube.com/results?search_query=jetpack+compose+tutorial"},
            {"step": 3, "title": "Architecture & Data", "description": "Build robust apps", "duration_weeks": 5, "skills": "MVVM,Room DB,Retrofit,Coroutines", "resources": "https://www.youtube.com/results?search_query=android+architecture+mvvm"},
            {"step": 4, "title": "Publishing & Polish", "description": "Ship to Play Store", "duration_weeks": 3, "skills": "Play Store,Testing,Push Notifications,Firebase", "resources": "https://www.youtube.com/results?search_query=google+play+store+publishing"},
        ]
    },
    "iOS Development": {
        "title": "iOS Development Career Path",
        "description": "Build apps for the Apple ecosystem",
        "duration_weeks": 22,
        "steps": [
            {"step": 1, "title": "Swift Fundamentals", "description": "Learn iOS development language", "duration_weeks": 3, "skills": "Swift,Optionals,Protocols,Generics", "resources": "https://www.youtube.com/results?search_query=swift+ios+tutorial"},
            {"step": 2, "title": "SwiftUI & UIKit", "description": "Build iOS interfaces", "duration_weeks": 4, "skills": "SwiftUI,UIKit,AutoLayout,Navigation", "resources": "https://www.youtube.com/results?search_query=swiftui+tutorial"},
            {"step": 3, "title": "Data & Networking", "description": "Connect to services", "duration_weeks": 4, "skills": "CoreData,URLSession,JSON Parsing,Combine", "resources": "https://www.youtube.com/results?search_query=ios+networking+coredata"},
            {"step": 4, "title": "App Store & Polish", "description": "Ship to the App Store", "duration_weeks": 3, "skills": "App Store,Performance,Testing,ARKit", "resources": "https://www.youtube.com/results?search_query=ios+app+store+publishing"},
        ]
    },
    "Quality Assurance": {
        "title": "Quality Assurance Career Path",
        "description": "Ensure software quality through testing",
        "duration_weeks": 20,
        "steps": [
            {"step": 1, "title": "Testing Fundamentals", "description": "Learn testing concepts", "duration_weeks": 3, "skills": "Test Cases,Bug Tracking,Agile,Test Plans", "resources": "https://www.youtube.com/results?search_query=software+testing+basics"},
            {"step": 2, "title": "Manual Testing", "description": "Master manual QA techniques", "duration_weeks": 3, "skills": "Regression Testing,Exploratory Testing,Documentation", "resources": "https://www.youtube.com/results?search_query=manual+testing+tutorial"},
            {"step": 3, "title": "Test Automation", "description": "Automate test suites", "duration_weeks": 5, "skills": "Selenium,Cypress,Jest,API Testing", "resources": "https://www.youtube.com/results?search_query=selenium+test+automation"},
            {"step": 4, "title": "Advanced Testing", "description": "Performance and security testing", "duration_weeks": 4, "skills": "Performance Testing,Security Testing,CI/CD,Postman", "resources": "https://www.youtube.com/results?search_query=performance+testing+jmeter"},
        ]
    },
}
