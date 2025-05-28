# IELTS AI Prep: GDPR Compliance Framework

## Executive Summary

This document outlines the comprehensive GDPR compliance framework implemented in IELTS GenAI Prep, featuring TrueScore® and Elaris® - the world's ONLY GenAI assessor tools for IELTS test preparation. The platform has been designed with privacy and data protection as core principles, ensuring compliance with the General Data Protection Regulation (GDPR) from day one.

This GDPR framework demonstrates our commitment to best practices in data protection globally and provides robust privacy protections for all users regardless of their location.

## Table of Contents

1. [Legal Basis for Processing](#legal-basis-for-processing) (GDPR Articles 6, 7, 9)
2. [Data Protection Principles](#data-protection-principles) (GDPR Article 5)
3. [User Rights Implementation](#user-rights-implementation) (GDPR Articles 12-22)
4. [Technical & Organizational Measures](#technical--organizational-measures) (GDPR Article 32)
5. [Data Processing Activities](#data-processing-activities) (GDPR Article 30)
6. [Data Retention Policies](#data-retention-policies) (GDPR Article 5(1)(e))
7. [Data Breach Management](#data-breach-management) (GDPR Articles 33, 34)
8. [Privacy by Design & Default](#privacy-by-design--default) (GDPR Article 25)
9. [International Data Transfers](#international-data-transfers) (GDPR Articles 44-50)
10. [Documentation & Accountability](#documentation--accountability) (GDPR Article 5(2), 24)

## Legal Basis for Processing

*Compliant with GDPR Articles 6 (Lawfulness of processing), 7 (Conditions for consent), and 9 (Processing of special categories of data)*

The IELTS GenAI Prep application processes personal data under the following legal bases:

| Processing Activity | Legal Basis | Implementation |
|---------------------|-------------|----------------|
| Account creation | Contract | User accepts Terms of Service during registration |
| Payment processing | Contract | Required for delivering purchased assessment packages |
| Assessment delivery | Contract | Core functionality users have paid for |
| Contact form communications | Consent | User initiates contact through contact form |
| Marketing communications | Consent | Separate opt-in checkbox during registration |
| Speaking assessments | Explicit Consent | Special notification before speaking tests |
| Analytics & improvement | Legitimate Interest | Privacy-focused, minimal data collection |

### Consent Management System

*Compliant with GDPR Article 7 (Conditions for consent)*

1. **Granular Consent**: All consent is collected through separate, unticked checkboxes
2. **Specific Purpose**: Each consent request clearly states the purpose
3. **Withdrawable**: Simple interface to withdraw consent in user dashboard (Article 7(3))
4. **Documented**: All consent events are timestamped and stored securely (Article 7(1))

## Data Protection Principles

*Compliant with GDPR Article 5 (Principles relating to processing of personal data)*

### 1. Lawfulness, Fairness, and Transparency 
*Article 5(1)(a)*

- **Privacy Policy**: Comprehensive, easily accessible policy in plain language
- **Layered Notices**: Summary notices with links to detailed information
- **Process Documentation**: Internal documentation of all data flows

### 2. Purpose Limitation
*Article 5(1)(b)*

- **Defined Purposes**: Clear documentation of all data processing purposes
- **Function Separation**: Technical controls preventing purpose creep
- **Purpose Review**: Regular audits to ensure alignment with stated purposes

### 3. Data Minimization
*Article 5(1)(c)*

- **Minimal Collection**: Only data necessary for service provision is collected
- **Field Justification**: Documentation justifying every data field collected
- **Default Settings**: Privacy-enhancing default settings

### 4. Accuracy
*Article 5(1)(d)*

- **User-Controlled**: Self-service profile management for users
- **Verification Process**: Email verification for account information
- **Update Mechanisms**: Regular prompts to verify information accuracy

### 5. Storage Limitation
*Article 5(1)(e)*

- **Retention Policies**: Clear timeframes for all data categories
- **Automatic Deletion**: Scheduled purging of expired data
- **Transcript Deletion**: Speaking transcripts deleted after 6 months
- **Account Deletion**: Complete data removal upon account termination

### 6. Integrity and Confidentiality
*Article 5(1)(f) and Article 32*

- **Encryption**: All data encrypted at rest and in transit
- **Access Controls**: Role-based access controls for all systems
- **Security Testing**: Regular penetration testing and vulnerability assessments

### 7. Accountability
*Article 5(2) and Article 24*

- **DPO Role**: Designated Data Protection Officer for oversight (Article 37)
- **ROPA Maintenance**: Regularly updated Record of Processing Activities (Article 30)
- **Staff Training**: Comprehensive privacy training for all personnel

## User Rights Implementation

*Compliant with GDPR Articles 12-22 (Rights of the data subject)*

The application provides direct mechanisms for users to exercise their GDPR rights:

### 1. Right to Access
*Article 15*
- **My Data Dashboard**: Centralized page showing all user data
- **Data Export**: One-click JSON/CSV export of all personal data
- **Processing Transparency**: Clear listing of how data is used

### 2. Right to Rectification
*Article 16*
- **Edit Profile**: Self-service correction of account information
- **Data Verification**: Process to verify and update assessment information

### 3. Right to Erasure
*Article 17 (Right to be forgotten)*
- **Account Deletion**: One-click process to initiate account deletion
- **Partial Deletion**: Options to delete specific data categories
- **Verification System**: Two-factor authentication for deletion requests

### 4. Right to Restriction of Processing
*Article 18*
- **Processing Pause**: Ability to temporarily restrict processing
- **Flagging System**: Backend markers for processing restrictions

### 5. Right to Data Portability
*Article 20*
- **Structured Format**: Export in machine-readable formats (JSON/CSV)
- **Complete Dataset**: All user-provided data included in exports
- **Direct Transfer**: Option to transfer data to another provider (where feasible)

### 6. Right to Object
*Article 21*
- **Processing Objection**: Clear mechanism to object to processing
- **Automated Decisions**: System to request human review of automated decisions
- **Marketing Opt-Out**: One-click unsubscribe from all communications

### 7. Rights Related to Automated Decision Making
*Article 22*
- **Transparency**: Clear indication when automated assessment is used
- **Human Review**: Option to request human verification of AI assessments
- **Logic Explanation**: Documentation explaining assessment algorithms

## Technical & Organizational Measures

*Compliant with GDPR Article 32 (Security of processing)*

### Technical Measures

1. **Encryption**
   - TLS 1.3 for all communications
   - AES-256 encryption for data at rest
   - Encrypted database backups

2. **Access Controls**
   - Role-based access control (RBAC)
   - Multi-factor authentication for staff
   - Principle of least privilege enforcement
   - Session management with secure timeouts

3. **Advanced Security Protection (2025 Implementation)**
   - **Rate limiting**: Protection against brute force attacks with configurable limits
   - **Account lockout protection**: Automatic temporary account locks after multiple failed attempts
   - **Enhanced input validation**: Comprehensive validation against injection attacks and malicious input
   - **Session security monitoring**: Real-time detection of session hijacking attempts
   - **API endpoint protection**: Rate limiting and abuse detection for all assessment endpoints
   - **Security event logging**: Comprehensive logging of all security-related events for audit trails

4. **Attack Prevention Systems**
   - **SQL injection protection**: Pattern detection and blocking of malicious database queries
   - **Cross-site scripting (XSS) prevention**: Input sanitization and output encoding
   - **Cross-site request forgery (CSRF) protection**: Token-based request validation
   - **Denial of service mitigation**: Request size limits and rate limiting
   - **Suspicious activity detection**: Automated monitoring of URL patterns and request anomalies

5. **Data Validation and Sanitization**
   - **Password complexity enforcement**: Mandatory uppercase, lowercase, numbers, and special characters
   - **Email format validation**: RFC-compliant email address verification
   - **Content filtering**: Removal of potentially malicious scripts and code from user inputs
   - **File upload security**: Comprehensive validation of uploaded assessment materials

6. **Monitoring and Logging**
   - Access logs with anomaly detection
   - Processing activity audit trails
   - GDPR-specific logging events
   - **Security incident tracking**: Real-time monitoring and alerting for security events
   - **Failed authentication logging**: Detailed tracking of login attempts and failures

7. **Data Isolation**
   - Separate database schemas for sensitive data
   - Logical separation of processing environments
   - Containerized application components

### Organizational Measures

1. **Governance Structure**
   - Designated Data Protection responsibilities
   - Regular privacy reviews and updates
   - Executive-level privacy oversight

2. **Policies and Procedures**
   - GDPR compliance policy
   - Data security policy
   - Breach notification procedure
   - Subject rights procedure

3. **Training and Awareness**
   - GDPR training for all staff
   - Role-specific privacy training
   - Regular privacy awareness updates

4. **Third-Party Management**
   - Vendor assessment process
   - GDPR-compliant contracts
   - Regular compliance verification

## Data Processing Activities

*Compliant with GDPR Article 30 (Records of processing activities)*

### Record of Processing Activities (ROPA)

The platform maintains a comprehensive ROPA including:

1. **User Registration & Authentication**
   - Personal data: Email, name, password (hashed)
   - Purpose: Account creation and access control
   - Retention: Until account deletion
   - Security: Encryption, access controls

2. **Payment Processing**
   - Personal data: Name, country, payment information
   - Purpose: Processing assessment package purchases
   - Processors: Stripe (PCI-DSS compliant)
   - Retention: As required by financial regulations

3. **Assessment Delivery**
   - Personal data: Test responses, performance data
   - Purpose: Providing IELTS assessment practice using TrueScore® and Elaris® GenAI technology
   - Retention: Assessment access until used, results retained permanently for user access
   - Access: User and authorized system processes only

4. **Speaking Assessment Processing**
   - Personal data: Voice recordings, transcripts
   - Purpose: Assessment and feedback
   - Special measures: Explicit consent, temporary processing
   - Retention: Audio deleted after processing, transcripts after 6 months

5. **AI-Powered Assessment**
   - Personal data: Test responses, writing samples
   - Purpose: Automated scoring and feedback using TrueScore® and Elaris® GenAI technology
   - Processing: Advanced AI models with privacy safeguards
   - Retention: Results retained permanently for user access

6. **Contact Form Communications**
   - Personal data: Name, email address, message content
   - Purpose: Customer support and inquiry response
   - Processing: Professional email system with auto-reply functionality
   - Retention: Until inquiry resolution, then deleted

## Data Retention Policies

*Compliant with GDPR Article 5(1)(e) (Storage limitation)*

The platform implements granular retention policies for different data categories:

| Data Category | Retention Period | Justification | Deletion Method |
|---------------|------------------|---------------|-----------------|
| Account information | Until account deletion + 30 days | Service provision | Secure erasure |
| Payment records | 7 years | Legal obligation (tax) | Archived, limited access |
| Assessment packages | Until assessments are used | Service provision | Secure erasure after use |
| Voice recordings | Deleted after processing | Data minimization | Immediate deletion |
| Transcripts | 6 months | Educational purpose | Automatic deletion |
| Assessment results | Permanent (until account deletion) | Ongoing user access | Secure erasure on account deletion |
| Contact form data | Until inquiry resolution | Customer service | Secure erasure after resolution |
| Session logs | 90 days | Security | Automatic deletion |
| Marketing preferences | Until consent withdrawal | Consent-based | Immediate update |

### Implementation

- **Automated Deletion**: Scheduled jobs remove data according to retention schedule
- **Soft Delete**: Initial deletion marks data as inaccessible but recoverable for 30 days
- **Hard Delete**: Permanent removal after recovery period
- **Audit Trail**: Records of deletion events retained for compliance purposes

## Data Breach Management

*Compliant with GDPR Articles 33 (Notification of a personal data breach to the supervisory authority) and 34 (Communication of a personal data breach to the data subject)*

The platform has a comprehensive data breach response plan:

### Detection

- **Automated Monitoring**: Security tools to detect unauthorized access
- **Anomaly Detection**: Pattern analysis to identify unusual data activities
- **Staff Reporting**: Clear protocols for internal breach reporting

### Automated Breach Detection System

*Compliant with GDPR Article 33 (72-hour notification requirement)*

The platform includes an automated breach detection system that:

1. **Continuous Monitoring**: Utilizes security tools to detect unusual database access, unauthorized API calls, and potential data exposure
2. **Alert Classification**: Automatically classifies potential incidents by severity and likelihood
3. **Immediate Notification**: Sends real-time alerts to the designated Data Protection team
4. **Evidence Collection**: Automatically preserves evidence of the potential breach
5. **Impact Assessment**: Provides preliminary assessment of affected data and users
6. **Administrator Dashboard**: Displays breach details with approval buttons for official reporting

### Response Protocol

1. **Containment**: Immediate steps to contain the breach through automated and manual processes
2. **Assessment**: Evaluation of breach scope and impact using the automated assessment and manual verification
3. **Notification to Authorities**: Upon administrator approval, automated submission to relevant DPAs (within 72 hours)
4. **Communication to Data Subjects**: Automated preparation of communications to affected users (required under Article 34)
5. **Remediation**: Implementation of technical fixes and security enhancements
6. **Documentation**: Comprehensive breach records maintained in a secure breach register

### Supervisory Authority Reporting

*Compliant with GDPR Article 33 (Notification of a personal data breach to the supervisory authority)*

The platform maintains current contact details and reporting methods for Data Protection Authorities in relevant jurisdictions:

| Country | Supervisory Authority | Reporting Method | Contact Details |
|---------|------------------------|------------------|-----------------|
| Canada | Office of the Privacy Commissioner | Web form | [priv.gc.ca](https://www.priv.gc.ca/en/report-a-concern/) |
| USA | Federal Trade Commission | Online portal | [ftccomplaintassistant.gov](https://www.ftccomplaintassistant.gov/) |
| India | Data Protection Authority of India | Email notification | [info@dpai.gov.in](mailto:info@dpai.gov.in) |
| Nepal | Ministry of Communication and Information Technology | Email notification | [info@mocit.gov.np](mailto:info@mocit.gov.np) |
| Kuwait | Communication and Information Technology Regulatory Authority | Web portal | [citra.gov.kw](https://www.citra.gov.kw/) |
| Qatar | Ministry of Transport and Communications | Email notification | [info@motc.gov.qa](mailto:info@motc.gov.qa) |

For potential EU/UK expansion in the future:
| EU/UK | European Data Protection Board | One-stop-shop mechanism | [edpb.europa.eu](https://edpb.europa.eu/) |
| UK | Information Commissioner's Office | Online portal | [ico.org.uk/report-a-breach](https://ico.org.uk/report-a-breach/) |

### Data Subject Notification

*Compliant with GDPR Article 34 (Communication of a personal data breach to the data subject)*

When a breach is likely to result in a high risk to individuals' rights and freedoms, the platform:

1. **Required Notification**: Automatically prepares communications to affected users without undue delay
2. **Notification Channels**: Employs multiple channels (email, in-app notification, SMS) to ensure receipt
3. **Content Requirements**: Provides clear description of the breach nature, contact details of DPO, likely consequences, and measures taken
4. **Plain Language**: Ensures all communications use clear, plain language appropriate for non-technical users
5. **Action Guidance**: Includes specific steps users should take to protect themselves
6. **Notification Exemptions**: Documents situations where notification may not be required (data encrypted, risk mitigation measures, disproportionate effort)

### Notification Templates and Automation

- **Authority Notification**: Pre-prepared, jurisdiction-specific templates for DPA reporting with auto-fill of incident details
- **User Communication**: Tailored notifications based on breach type and affected data categories
- **Website Notice**: Public breach notification templates when required by supervisory authorities
- **Approval Workflow**: Administrator review and approval before automated submission
- **Submission Tracking**: Documentation of all communications for compliance verification

## Privacy by Design & Default

*Compliant with GDPR Article 25 (Data protection by design and by default)*

Privacy is embedded into the platform's development process:

### Design Phase

- **Privacy Impact Assessments**: Conducted for all new features
- **Data Mapping**: Visual mapping of data flows and processing
- **Risk Assessment**: Identification of privacy risks and mitigations

### Development Phase

- **Privacy Requirements**: Explicit privacy requirements in user stories
- **Code Reviews**: Privacy-focused reviews in development process
- **Automated Testing**: Privacy compliance verification in CI/CD

### Default Settings

- **Minimal Collection**: Only essential data collected by default
- **Limited Retention**: Conservative default retention periods
- **Restricted Access**: Narrow access controls by default
- **Secure Communication**: Encryption enabled by default

## International Data Transfers

*Compliant with GDPR Articles 44-50 (Transfers of personal data to third countries or international organisations)*

The platform implements robust data transfer protections:

### Transfer Mechanisms

- **Adequacy Decisions**: Preferred operation in adequate jurisdictions
- **Standard Contractual Clauses**: Used with processors where needed
- **Technical Safeguards**: End-to-end encryption for all transfers

### Geographic Considerations

- **Data Localization**: Primary storage in user's region where possible
- **Transfer Transparency**: Clear documentation of all cross-border transfers
- **Transfer Impact Assessments**: Conducted for all international data flows

### Technical Implementation

- **Regional Storage**: Configured for data residency requirements
- **Transfer Controls**: Restrictions on cross-region replication
- **Compliance Documentation**: Data protection agreements with all processors

## Documentation & Accountability

*Compliant with GDPR Article 5(2) (Accountability) and Article 24 (Responsibility of the controller)*

The platform maintains comprehensive documentation:

### Policy Documentation

- **Privacy Policy**: User-facing privacy information
- **Terms of Service**: Legal terms including data processing
- **Cookie Policy**: Detailed information on cookie usage
- **Acceptable Use Policy**: Boundaries for platform usage

### Internal Documentation

- **Data Protection Impact Assessments**: For high-risk processing
- **Record of Processing Activities**: Detailed ROPA documentation
- **Legitimate Interest Assessments**: For processing under legitimate interest
- **Security Procedures**: Documentation of security measures

### Evidence Collection

- **Consent Records**: Timestamped consent actions
- **Data Subject Requests**: Complete record of all requests and responses
- **Staff Training**: Records of all data protection training
- **Compliance Reviews**: Regular internal audit documentation

## Cloud Infrastructure GDPR Implementation

The cloud deployment maintains GDPR compliance through:

### Data Residency Controls

- **Regional Storage**: Data stored in specified regions only
- **Residency Policies**: Technical enforcement of location restrictions
- **Transfer Controls**: Strict control of cross-region transfers

### Security Features

- **Customer-Managed Encryption Keys**: Control over encryption
- **Data Isolation**: Secure data isolation within cloud infrastructure
- **Access Transparency**: Logging of all administrative access

### Documentation

- **Data Processing Addendum**: GDPR-compliant terms with cloud providers
- **Technical Documentation**: Data protection controls and procedures
- **Compliance Certifications**: ISO 27001, 27017, 27018, SOC 2/3

## Conclusion

IELTS GenAI Prep, featuring TrueScore® and Elaris® - the world's ONLY GenAI assessor tools for IELTS test preparation - has implemented a comprehensive GDPR compliance framework covering all aspects of the regulation. This framework ensures that:

1. User privacy and data protection are built into the core of the platform (Article 5)
2. Assessment package purchases and processing are handled with complete transparency and user control
3. Users worldwide benefit from strong privacy protections regardless of their location
4. Contact form communications and customer support maintain professional privacy standards

The framework is regularly reviewed and updated to reflect evolving interpretations of GDPR requirements, changes in the application's functionality, and emerging best practices in data protection.

## GDPR Article Coverage Matrix

The following matrix shows how our implementation covers the key GDPR articles:

| GDPR Article | Article Title | Implementation |
|--------------|---------------|----------------|
| Article 5 | Principles relating to processing of personal data | Data Protection Principles section |
| Article 6 | Lawfulness of processing | Legal Basis for Processing section |
| Article 7 | Conditions for consent | Consent Management System section |
| Article 8 | Conditions applicable to child's consent | Age verification (16+) during registration |
| Article 9 | Processing of special categories of personal data | Special handling of biometric data (voice) |
| Articles 12-14 | Transparency information | Privacy Policy, layered notices |
| Article 15 | Right of access | My Data Dashboard feature |
| Article 16 | Right to rectification | Profile editing features |
| Article 17 | Right to erasure | Account and data deletion features |
| Article 18 | Right to restriction of processing | Processing pause features |
| Article 20 | Right to data portability | Data export in structured formats |
| Article 21 | Right to object | Processing objection mechanisms |
| Article 22 | Automated decision-making | Human review of AI assessments |
| Article 24 | Responsibility of the controller | Accountability framework |
| Article 25 | Data protection by design and by default | Privacy by Design section |
| Article 30 | Records of processing activities | ROPA documentation |
| Article 32 | Security of processing | Technical & Organizational Measures |
| Articles 33-34 | Breach notification | Data Breach Management section |
| Articles 37-39 | Data Protection Officer | DPO designation |
| Articles 44-50 | Transfers to third countries | International Data Transfers section |

This matrix demonstrates our comprehensive approach to GDPR compliance, addressing each relevant article through specific implementation details.