"""
Tests for payment_country_check module.
Run with: python test_payment_country_check.py
"""
import unittest
from unittest.mock import patch, MagicMock
from payment_country_check import get_effective_country_code, check_country_restriction

class TestPaymentCountryCheck(unittest.TestCase):
    """Tests for payment_country_check.py functions."""
    
    def test_get_effective_country_code_no_simulation(self):
        """Test getting effective country code with no simulation."""
        # Test with empty session dict (no simulation)
        country_code, is_simulated = get_effective_country_code('US', session_dict={})
        
        # Verify
        self.assertEqual(country_code, 'US')
        self.assertFalse(is_simulated)
    
    def test_get_effective_country_code_with_simulation(self):
        """Test getting effective country code with simulation."""
        # Setup mock session dict with simulated country
        session_dict = {
            'simulated_country': True,
            'country_code': 'RU'
        }
        
        # Test
        country_code, is_simulated = get_effective_country_code('US', session_dict=session_dict)
        
        # Verify - should return the simulated country code
        self.assertEqual(country_code, 'RU')
        self.assertTrue(is_simulated)
    
    def test_check_country_restriction_allowed(self):
        """Test country check for an allowed country."""
        # Setup - Create mock function for is_country_restricted
        mock_is_restricted = MagicMock(return_value=False)
        
        # Test with US as non-restricted country
        # Should not raise exception
        check_country_restriction('US', mock_is_restricted, session_dict={})
        
        # Verify
        mock_is_restricted.assert_called_once_with('US')
    
    def test_check_country_restriction_restricted(self):
        """Test country check for a restricted country."""
        # Setup - Create mock function for is_country_restricted
        mock_is_restricted = MagicMock(return_value=True)
        
        # Test with RU as restricted country
        # Should raise ValueError
        with self.assertRaises(ValueError):
            check_country_restriction('RU', mock_is_restricted, session_dict={})
        
        # Verify
        mock_is_restricted.assert_called_once_with('RU')
    
    def test_check_country_restriction_simulated(self):
        """Test country check for a simulated country."""
        # Setup - Create mock function for is_country_restricted
        mock_is_restricted = MagicMock()
        # Define behavior: RU is restricted, US is allowed
        mock_is_restricted.side_effect = lambda country: country == 'RU'
        
        # Create session dict for simulation
        session_dict = {
            'simulated_country': True,
            'country_code': 'RU'  # Simulating Russia (restricted)
        }
        
        # Test with US as real country but RU as simulated (restricted)
        # Should raise ValueError
        with self.assertRaises(ValueError):
            check_country_restriction('US', mock_is_restricted, session_dict=session_dict)
        
        # Verify
        mock_is_restricted.assert_called_once_with('RU')
    
    def test_check_country_restriction_none(self):
        """Test country check for None country code."""
        # Setup
        mock_is_restricted = MagicMock()
        
        # Test with None country code - should not raise exception or call the restriction check
        check_country_restriction(None, mock_is_restricted, session_dict={})
        
        # Verify
        mock_is_restricted.assert_not_called()

if __name__ == '__main__':
    unittest.main()