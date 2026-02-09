"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.casingTerms = exports.backtickIgnoredTerms = void 0;
// @ts-check

/**
 * A centralized collection of terms with special casing rules or that should be ignored by certain linting rules.
 * This helps maintain consistency across different custom rules.
 */

/**
 * A unified dictionary of all terms with specific casing requirements.
 * Includes proper nouns, technical terms, acronyms, and brand names.
 * The key is the lowercase version of the term for easy lookup, and the value is the correct casing.
 * Used by all rules that need to enforce or recognize special casing.
 * @type {Record<string, string>}
 */
const casingTerms = exports.casingTerms = {
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
  eslint: 'ESLint',
  go: 'Go',
  java: 'Java',
  javascript: 'JavaScript',
  jest: 'Jest',
  jsdoc: 'JSDoc',
  kotlin: 'Kotlin',
  'node.js': 'Node.js',
  php: 'PHP',
  python: 'Python',
  'react.js': 'React.js',
  react: 'React',
  ruby: 'Ruby',
  rust: 'Rust',
  scala: 'Scala',
  swift: 'Swift',
  typescript: 'TypeScript',
  vue: 'Vue',
  webpack: 'Webpack',
  // Databases
  mongodb: 'MongoDB',
  mysql: 'MySQL',
  postgresql: 'PostgreSQL',
  redis: 'Redis',
  'sql server': 'SQL Server',
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
  codeberg: 'Codeberg',
  confluence: 'Confluence',
  covid: 'COVID',
  debian: 'Debian',
  devops: 'DevOps',
  diátaxis: 'Diátaxis',
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
  html: 'HTML',
  iaas: 'IaaS',
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
  paas: 'PaaS',
  paris: 'Paris',
  'pci dss': 'PCI DSS',
  postman: 'Postman',
  prettier: 'Prettier',
  'red hat': 'Red Hat',
  'rest api': 'REST API',
  saas: 'SaaS',
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
  // Multi-word terms
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
  // Geographic names
  andes: 'Andes',
  mit: 'MIT'
};

/**
 * Additional terms to ignore in the `backtick-code-elements` rule, not covered by casingTerms.
 * @type {readonly string[]}
 */
const additionalBacktickIgnoredTerms = ['github.com', 'ulca.edu', 'pass/fail', 'e.g', 'i.e', 'CI/CD', 'Describe/test'];
/**
 * A set of terms that should be ignored by the `backtick-code-elements` rule.
 * This includes all special-cased terms from the dictionary above plus a few domain-specific exceptions.
 * @type {Readonly<Set<string>>}
 */
const backtickIgnoredTerms = exports.backtickIgnoredTerms = new Set([...Object.values(casingTerms), ...additionalBacktickIgnoredTerms]);