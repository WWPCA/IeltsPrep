"""
Tests for payment_country_check module.
Run with: python test_payment_country_check.py
"""
import unittest
from unittest.mock import patch, MagicMock
from payment_country_check import get_effective_country_code, check_country_restriction

class TestPaymentCountryCheck(unittest.TestCase):
    """Tests for payment_country_check.py functions."""
    
    @patch('payment_country_check.session')
    def test_get_effective_country_code_no_simulation(self, mock_session):
        """Test getting effective country code with no simulation."""
        # Setup mock session
        mock_session.get.return_value = None
        
        # Test
        country_code, is_simulated = get_effective_country_code('US')
        
        # Verify
        self.assertEqual(country_code, 'US')
        self.assertFalse(is_simulated)
    
    @patch('payment_country_check.session')
    def test_get_effective_country_code_with_simulation(self, mock_session):
        """Test getting effective country code with simulation."""
        # Setup mock session with simulated country
        def mock_session_get(key):
            if key == 'simulated_country':
                return True
            elif key == 'country_code':
                return 'RU'
            return None
        
        mock_session.get.side_effect = mock_session_get
        
        # Test
        country_code, is_simulated = get_effective_country_code('US')
        
        # Verify - should return the simulated country code
        self.assertEqual(country_code, 'RU')
        self.assertTrue(is_simulated)
    
    @patch('payment_country_check.get_effective_country_code')
    def test_check_country_restriction_allowed(self, mock_get_code):
        """Test country check for an allowed country."""
        # Setup
        mock_get_code.return_value = ('US', False)
        mock_is_restricted = MagicMock(return_value=False)
        
        # Test - should not raise exception
        check_country_restriction('US', mock_is_restricted)
        
        # Verify
        mock_get_code.assert_called_once_with('US')
        mock_is_restricted.assert_called_once_with('US')
    
    @patch('payment_country_check.get_effective_country_code')
    def test_check_country_restriction_restricted(self, mock_get_code):
        """Test country check for a restricted country."""
        # Setup
        mock_get_code.return_value = ('RU', False)
        mock_is_restricted = MagicMock(return_value=True)
        
        # Test - should raise ValueError
        with self.assertRaises(ValueError):
            check_country_restriction('RU', mock_is_restricted)
        
        # Verify
        mock_get_code.assert_called_once_with('RU')
        mock_is_restricted.assert_called_once_with('RU')
    
    @patch('payment_country_check.get_effective_country_code')
    def test_check_country_restriction_simulated(self, mock_get_code):
        """Test country check for a simulated country."""
        # Setup - US real country but RU simulated (restricted)
        mock_get_code.return_value = ('RU', True)
        mock_is_restricted = MagicMock(return_value=True)
        
        # Test - should raise ValueError
        with self.assertRaises(ValueError):
            check_country_restriction('US', mock_is_restricted)
        
        # Verify
        mock_get_code.assert_called_once_with('US')
        mock_is_restricted.assert_called_once_with('RU')
    
    @patch('payment_country_check.get_effective_country_code')
    def test_check_country_restriction_none(self, mock_get_code):
        """Test country check for None country code."""
        # Test - should not raise exception
        check_country_restriction(None, MagicMock())
        
        # Verify
        mock_get_code.assert_not_called()

if __name__ == '__main__':
    unittest.main()