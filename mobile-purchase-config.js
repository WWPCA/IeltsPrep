/**
 * IELTS GenAI Prep - Mobile In-App Purchase Configuration
 * Defines products for Apple App Store and Google Play Store
 */

// Product IDs for App Store Connect and Google Play Console - 4 Individual Assessment Products
export const PURCHASE_PRODUCTS = {
  // Academic Assessment Products
  ACADEMIC_WRITING: {
    ios: 'com.ieltsaiprep.academic.writing',
    android: 'academic_writing_assessment',
    price: '$36.00',
    title: 'Academic Writing Assessment',
    description: 'IELTS Academic Writing assessment with Task 1 (graphs/charts) and Task 2 (essays)'
  },
  
  ACADEMIC_SPEAKING: {
    ios: 'com.ieltsaiprep.academic.speaking',
    android: 'academic_speaking_assessment',
    price: '$36.00',
    title: 'Academic Speaking Assessment',
    description: 'IELTS Academic Speaking assessment with Maya AI examiner covering all 3 parts'
  },
  
  // General Training Assessment Products
  GENERAL_WRITING: {
    ios: 'com.ieltsaiprep.general.writing',
    android: 'general_writing_assessment',
    price: '$36.00',
    title: 'General Writing Assessment',
    description: 'IELTS General Training Writing assessment with Task 1 (letters) and Task 2 (essays)'
  },
  
  GENERAL_SPEAKING: {
    ios: 'com.ieltsaiprep.general.speaking',
    android: 'general_speaking_assessment',
    price: '$36.00',
    title: 'General Speaking Assessment',
    description: 'IELTS General Training Speaking assessment with Maya AI examiner covering all 3 parts'
  }
};

// Purchase validation endpoint
export const PURCHASE_VALIDATION_ENDPOINT = 'https://ieltsaiprep.com/api/validate-purchase';

// Tax compliance note
export const TAX_COMPLIANCE_NOTE = `
All purchases are processed through Apple App Store or Google Play Store.
Platform fees and taxes are automatically calculated and collected.
No additional tax registration required for global sales.
`;

/**
 * App Store Connect Configuration Steps:
 * 1. Create products with above iOS product IDs
 * 2. Set pricing tier for $36 and $50 USD
 * 3. Configure auto-renewable or non-consumable products
 * 4. Add localized descriptions
 * 5. Submit for review
 */

/**
 * Google Play Console Configuration Steps:  
 * 1. Create managed products with above Android product IDs
 * 2. Set base price in USD ($36.00 and $50.00)
 * 3. Google automatically converts to local currencies
 * 4. Add product descriptions
 * 5. Activate products
 */