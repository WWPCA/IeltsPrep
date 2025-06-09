/**
 * IELTS GenAI Prep - Mobile In-App Purchase Configuration
 * Defines products for Apple App Store and Google Play Store
 */

// Product IDs for App Store Connect and Google Play Console
export const PURCHASE_PRODUCTS = {
  // Academic Assessment Products
  ACADEMIC_SINGLE: {
    ios: 'com.ieltsaiprep.academic.single',
    android: 'academic_single_assessment',
    price: '$36.00',
    title: 'Academic Single Assessment',
    description: 'Complete IELTS Academic assessment with reading, writing, and speaking tests'
  },
  
  ACADEMIC_DOUBLE: {
    ios: 'com.ieltsaiprep.academic.double',
    android: 'academic_double_assessment',
    price: '$50.00',
    title: 'Academic Double Package',
    description: 'Two IELTS Academic assessments with reading, writing, and speaking tests'
  },
  
  // General Training Assessment Products
  GENERAL_SINGLE: {
    ios: 'com.ieltsaiprep.general.single',
    android: 'general_single_assessment',
    price: '$36.00',
    title: 'General Training Single Assessment',
    description: 'Complete IELTS General Training assessment with reading, writing, and speaking tests'
  },
  
  GENERAL_DOUBLE: {
    ios: 'com.ieltsaiprep.general.double',
    android: 'general_double_assessment',
    price: '$50.00',
    title: 'General Training Double Package',
    description: 'Two IELTS General Training assessments with reading, writing, and speaking tests'
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