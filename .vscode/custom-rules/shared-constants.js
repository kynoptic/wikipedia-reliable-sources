// @ts-check

/**
 * A centralized collection of terms with special casing rules or that should be ignored by certain linting rules.
 * This helps maintain consistency across different custom rules.
 */

/**
 * A dictionary of terms that have a specific, required capitalization.
 * This includes technical terms, acronyms, and proper nouns.
 * The key is the lowercase version of the term for easy lookup, and the value is the correct casing.
 * This is used by the `sentence-case-heading` rule.
 * @type {Readonly<Record<string, string>>}
 */
export const specialCasedTerms = Object.freeze({
  // Technical Terms & Acronyms
  api: 'API',
  aws: 'AWS',
  cdc: 'CDC',
  cdn: 'CDN',
  cli: 'CLI',
  css: 'CSS',
  dns: 'DNS',
  es6: 'ES6',
  fbi: 'FBI',
  gcp: 'GCP',
  graphql: 'GraphQL',
  http: 'HTTP',
  https: 'HTTPS',
  ibm: 'IBM',
  iot: 'IoT',
  jwt: 'JWT',
  json: 'JSON',
  mfa: 'MFA',
  ml: 'ML',
  nasa: 'NASA',
  oauth2: 'OAuth2',
  rest: 'REST',
  sdk: 'SDK',
  sso: 'SSO',
  sql: 'SQL',
  ssl: 'SSL',
  tls: 'TLS',
  ui: 'UI',
  unesco: 'UNESCO',
  unicef: 'UNICEF',
  url: 'URL',
  ux: 'UX',
  vpn: 'VPN',
  xml: 'XML',

  // Programming Languages & Frameworks
  angular: 'Angular',
  'c#': 'C#',
  'c++': 'C++',
  go: 'Go',
  java: 'Java',
  javascript: 'JavaScript',
  kotlin: 'Kotlin',
  nodejs: 'Node.js',
  php: 'PHP',
  python: 'Python',
  'react.js': 'React.js', // Common variant
  react: 'React',
  ruby: 'Ruby',
  rust: 'Rust',
  scala: 'Scala',
  swift: 'Swift',
  typescript: 'TypeScript',
  vue: 'Vue',

  // Databases
  mongodb: 'MongoDB',
  mysql: 'MySQL',
  postgresql: 'PostgreSQL',
  redis: 'Redis',

  // Proper Nouns & Brand Names
  '2fa': '2FA',
  adobe: 'Adobe',
  agile: 'Agile',
  ai: 'AI',
  amazon: 'Amazon',
  android: 'Android',
  apple: 'Apple',
  azure: 'Azure',
  chatgpt: 'ChatGPT',
  covid: 'COVID',
  docker: 'Docker',
  'dr. patel': 'Dr. Patel',
  facebook: 'Facebook',
  gdpr: 'GDPR',
  gemini: 'Gemini',
  git: 'Git',
  github: 'GitHub',
  gitlab: 'GitLab',
  glossary: 'Glossary',
  'google cloud': 'Google Cloud',
  google: 'Google',
  hipaa: 'HIPAA',
  ios: 'iOS',
  japanese: 'Japanese',
  jenkins: 'Jenkins',
  jira: 'Jira',
  kanban: 'Kanban',
  kubernetes: 'Kubernetes',
  linux: 'Linux',
  macos: 'macOS',
  markdown: 'Markdown',
  'machine learning': 'Machine Learning',
  michael: 'Michael',
  microsoft: 'Microsoft',
  npm: 'npm',
  paris: 'Paris',
  'pci dss': 'PCI DSS',
  postman: 'Postman',
  prettier: 'Prettier',
  'red hat': 'Red Hat',
  salesforce: 'Salesforce',
  scrum: 'Scrum',
  slack: 'Slack',
  socrates: 'Socrates',
  'single sign-on': 'Single Sign-On',
  swagger: 'Swagger',
  terraform: 'Terraform',
  ubuntu: 'Ubuntu',
  'user experience': 'User Experience',
  'user interface': 'User Interface',
  'vs code': 'VS Code',
  vscode: 'VS Code',
  windows: 'Windows',
  yarn: 'Yarn',
  zoloft: 'Zoloft',
  'amazon web services': 'Amazon Web Services',
  'api gateway': 'API Gateway',
  'artificial intelligence': 'Artificial Intelligence',
  'aws lambda': 'AWS Lambda',
  'azure functions': 'Azure Functions',
  'ci/cd': 'CI/CD',
  'google cloud platform': 'Google Cloud Platform',
  'github actions': 'GitHub Actions',
  'gitlab ci': 'GitLab CI',
  'load balancer': 'Load Balancer',
  'natural language processing': 'Natural Language Processing',
  'microsoft azure': 'Microsoft Azure',
  devops: 'DevOps',
  eslint: 'ESLint',
  webpack: 'Webpack',
  confluence: 'Confluence',
  debian: 'Debian',
  html: 'HTML', // To correct 'Html' in fixtures
  iaas: 'IaaS', // From docs example
  paas: 'PaaS', // From docs example
  'rest api': 'REST API',
  saas: 'SaaS', // From docs example
  'sql server': 'SQL Server',

  // Geographic names
  andes: 'Andes',
});

/**
 * A set of terms that should be ignored by the `backtick-code-elements` rule.
 * This includes all special-cased terms from the dictionary above.
 * @type {Readonly<Set<string>>}
 */
export const backtickIgnoredTerms = new Set(Object.values(specialCasedTerms));
backtickIgnoredTerms.add('github.com');
backtickIgnoredTerms.add('ulca.edu');
backtickIgnoredTerms.add('pass/fail');
backtickIgnoredTerms.add('e.g');
backtickIgnoredTerms.add('i.e');
backtickIgnoredTerms.add('CI/CD');
backtickIgnoredTerms.add('Describe/test');
