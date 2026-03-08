"""
Unit Tests for Business Logic Module
Tests for tax calculations, discount rules, invoice totals, and other pure logic functions
"""

import unittest
from decimal import Decimal
from datetime import date, timedelta
import sys
import os

# Add parent directory to path to import business_logic
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from business_logic import (
    TaxCalculator, DiscountCalculator, InvoiceCalculator,
    LineItem, Customer, DiscountRule, TaxCategory, DiscountType,
    calculate_markup_price, calculate_margin_percentage, calculate_break_even_quantity,
    create_sample_line_items, create_sample_discount_rules
)

class TestTaxCalculator(unittest.TestCase):
    """Test tax calculation functionality"""
    
    def setUp(self):
        self.tax_calc = TaxCalculator()
    
    def test_standard_tax_calculation(self):
        """Test standard tax rate calculation"""
        amount = Decimal('100.00')
        tax = self.tax_calc.calculate_tax(amount, TaxCategory.STANDARD)
        expected = Decimal('8.50')  # 8.5%
        self.assertEqual(tax, expected)
    
    def test_food_tax_calculation(self):
        """Test food tax rate calculation"""
        amount = Decimal('50.00')
        tax = self.tax_calc.calculate_tax(amount, TaxCategory.FOOD)
        expected = Decimal('2.50')  # 5.0%
        self.assertEqual(tax, expected)
    
    def test_medical_tax_calculation(self):
        """Test medical items are tax-free"""
        amount = Decimal('100.00')
        tax = self.tax_calc.calculate_tax(amount, TaxCategory.MEDICAL)
        expected = Decimal('0.00')  # 0.0%
        self.assertEqual(tax, expected)
    
    def test_luxury_tax_calculation(self):
        """Test luxury tax rate calculation"""
        amount = Decimal('1000.00')
        tax = self.tax_calc.calculate_tax(amount, TaxCategory.LUXURY)
        expected = Decimal('120.00')  # 12.0%
        self.assertEqual(tax, expected)
    
    def test_zero_amount_tax(self):
        """Test tax calculation on zero amount"""
        amount = Decimal('0.00')
        tax = self.tax_calc.calculate_tax(amount, TaxCategory.STANDARD)
        expected = Decimal('0.00')
        self.assertEqual(tax, expected)
    
    def test_negative_amount_tax(self):
        """Test tax calculation on negative amount"""
        amount = Decimal('-10.00')
        tax = self.tax_calc.calculate_tax(amount, TaxCategory.STANDARD)
        expected = Decimal('0.00')
        self.assertEqual(tax, expected)
    
    def test_line_item_tax_calculation(self):
        """Test tax calculation for line items"""
        line_item = LineItem(1, "Test Product", 2, Decimal('50.00'), TaxCategory.STANDARD)
        tax = self.tax_calc.calculate_line_tax(line_item)
        expected = Decimal('8.50')  # (2 * 50.00) * 0.085
        self.assertEqual(tax, expected)
    
    def test_line_item_with_discount_tax(self):
        """Test tax calculation for line items with discount"""
        line_item = LineItem(1, "Test Product", 2, Decimal('50.00'), 
                            TaxCategory.STANDARD, Decimal('10.00'))
        tax = self.tax_calc.calculate_line_tax(line_item)
        expected = Decimal('7.65')  # (100.00 - 10.00) * 0.085
        self.assertEqual(tax, expected)
    
    def test_effective_tax_rate_calculation(self):
        """Test effective tax rate for multiple line items"""
        line_items = [
            LineItem(1, "Standard Item", 1, Decimal('100.00'), TaxCategory.STANDARD),
            LineItem(2, "Food Item", 1, Decimal('50.00'), TaxCategory.FOOD),
            LineItem(3, "Medical Item", 1, Decimal('25.00'), TaxCategory.MEDICAL),
        ]
        
        effective_rate = self.tax_calc.get_effective_tax_rate(line_items)
        # (8.50 + 2.50 + 0.00) / (100.00 + 50.00 + 25.00) = 11.00 / 175.00 = 0.0629
        expected = Decimal('0.0629')
        self.assertEqual(effective_rate, expected)

class TestDiscountCalculator(unittest.TestCase):
    """Test discount calculation functionality"""
    
    def setUp(self):
        self.discount_calc = DiscountCalculator()
    
    def test_percentage_discount_calculation(self):
        """Test percentage discount calculation"""
        amount = Decimal('100.00')
        percentage = Decimal('10')
        discount = self.discount_calc.calculate_percentage_discount(amount, percentage)
        expected = Decimal('10.00')
        self.assertEqual(discount, expected)
    
    def test_percentage_discount_edge_cases(self):
        """Test percentage discount edge cases"""
        amount = Decimal('100.00')
        
        # 0% discount
        discount = self.discount_calc.calculate_percentage_discount(amount, Decimal('0'))
        self.assertEqual(discount, Decimal('0.00'))
        
        # 100% discount
        discount = self.discount_calc.calculate_percentage_discount(amount, Decimal('100'))
        self.assertEqual(discount, Decimal('100.00'))
    
    def test_invalid_percentage_discount(self):
        """Test invalid percentage values"""
        amount = Decimal('100.00')
        
        with self.assertRaises(ValueError):
            self.discount_calc.calculate_percentage_discount(amount, Decimal('-5'))
        
        with self.assertRaises(ValueError):
            self.discount_calc.calculate_percentage_discount(amount, Decimal('105'))
    
    def test_bulk_discount_calculation(self):
        """Test bulk quantity discount calculation"""
        quantity = 15
        unit_price = Decimal('10.00')
        min_quantity = 10
        discount_percentage = Decimal('15')
        
        discount = self.discount_calc.calculate_bulk_discount(
            quantity, unit_price, min_quantity, discount_percentage
        )
        expected = Decimal('22.50')  # (15 * 10.00) * 0.15
        self.assertEqual(discount, expected)
    
    def test_bulk_discount_below_minimum(self):
        """Test bulk discount when quantity is below minimum"""
        quantity = 5
        unit_price = Decimal('10.00')
        min_quantity = 10
        discount_percentage = Decimal('15')
        
        discount = self.discount_calc.calculate_bulk_discount(
            quantity, unit_price, min_quantity, discount_percentage
        )
        expected = Decimal('0.00')
        self.assertEqual(discount, expected)
    
    def test_customer_tier_discounts(self):
        """Test customer tier-based discounts"""
        amount = Decimal('100.00')
        
        # Regular customer (0%)
        customer = Customer(1, "John Doe", "regular")
        discount = self.discount_calc.calculate_customer_tier_discount(customer, amount)
        self.assertEqual(discount, Decimal('0.00'))
        
        # Premium customer (5%)
        customer = Customer(2, "Jane Smith", "premium")
        discount = self.discount_calc.calculate_customer_tier_discount(customer, amount)
        self.assertEqual(discount, Decimal('5.00'))
        
        # VIP customer (10%)
        customer = Customer(3, "Bob Johnson", "vip")
        discount = self.discount_calc.calculate_customer_tier_discount(customer, amount)
        self.assertEqual(discount, Decimal('10.00'))
        
        # Wholesale customer (15%)
        customer = Customer(4, "ABC Corp", "wholesale")
        discount = self.discount_calc.calculate_customer_tier_discount(customer, amount)
        self.assertEqual(discount, Decimal('15.00'))
    
    def test_discount_rule_application(self):
        """Test discount rule application"""
        line_items = [
            LineItem(1, "Product A", 2, Decimal('50.00')),
            LineItem(2, "Product B", 1, Decimal('30.00')),
        ]
        
        # Percentage discount rule
        rule = DiscountRule(
            discount_type=DiscountType.PERCENTAGE,
            value=Decimal('10'),
            min_amount=Decimal('100')
        )
        
        discount = self.discount_calc.apply_discount_rule(rule, line_items)
        expected = Decimal('13.00')  # (100 + 30) * 0.10
        self.assertEqual(discount, expected)
    
    def test_discount_rule_minimum_amount_not_met(self):
        """Test discount rule when minimum amount is not met"""
        line_items = [
            LineItem(1, "Product A", 1, Decimal('25.00')),
        ]
        
        rule = DiscountRule(
            discount_type=DiscountType.PERCENTAGE,
            value=Decimal('10'),
            min_amount=Decimal('100')
        )
        
        discount = self.discount_calc.apply_discount_rule(rule, line_items)
        expected = Decimal('0.00')
        self.assertEqual(discount, expected)
    
    def test_fixed_amount_discount_rule(self):
        """Test fixed amount discount rule"""
        line_items = [
            LineItem(1, "Product A", 1, Decimal('100.00')),
        ]
        
        rule = DiscountRule(
            discount_type=DiscountType.FIXED_AMOUNT,
            value=Decimal('25.00')
        )
        
        discount = self.discount_calc.apply_discount_rule(rule, line_items)
        expected = Decimal('25.00')
        self.assertEqual(discount, expected)
    
    def test_fixed_amount_discount_exceeds_total(self):
        """Test fixed amount discount when it exceeds the total"""
        line_items = [
            LineItem(1, "Product A", 1, Decimal('20.00')),
        ]
        
        rule = DiscountRule(
            discount_type=DiscountType.FIXED_AMOUNT,
            value=Decimal('50.00')
        )
        
        discount = self.discount_calc.apply_discount_rule(rule, line_items)
        expected = Decimal('20.00')  # Should not exceed the total amount
        self.assertEqual(discount, expected)
    
    def test_customer_tier_discount_rule(self):
        """Test customer tier discount rule"""
        line_items = [
            LineItem(1, "Product A", 1, Decimal('100.00')),
        ]
        
        customer = Customer(1, "VIP Customer", "vip")
        
        rule = DiscountRule(
            discount_type=DiscountType.CUSTOMER_TIER,
            value=Decimal('10'),
            customer_tier="vip"
        )
        
        discount = self.discount_calc.apply_discount_rule(rule, line_items, customer)
        expected = Decimal('10.00')  # VIP gets 10% discount
        self.assertEqual(discount, expected)
    
    def test_expired_discount_rule(self):
        """Test expired discount rule"""
        line_items = [
            LineItem(1, "Product A", 1, Decimal('100.00')),
        ]
        
        # Create expired rule
        yesterday = date.today() - timedelta(days=1)
        rule = DiscountRule(
            discount_type=DiscountType.PERCENTAGE,
            value=Decimal('10'),
            valid_to=yesterday
        )
        
        discount = self.discount_calc.apply_discount_rule(rule, line_items)
        expected = Decimal('0.00')
        self.assertEqual(discount, expected)
    
    def test_future_discount_rule(self):
        """Test future discount rule"""
        line_items = [
            LineItem(1, "Product A", 1, Decimal('100.00')),
        ]
        
        # Create future rule
        tomorrow = date.today() + timedelta(days=1)
        rule = DiscountRule(
            discount_type=DiscountType.PERCENTAGE,
            value=Decimal('10'),
            valid_from=tomorrow
        )
        
        discount = self.discount_calc.apply_discount_rule(rule, line_items)
        expected = Decimal('0.00')
        self.assertEqual(discount, expected)

class TestInvoiceCalculator(unittest.TestCase):
    """Test complete invoice calculation functionality"""
    
    def setUp(self):
        self.invoice_calc = InvoiceCalculator()
    
    def test_basic_invoice_calculation(self):
        """Test basic invoice calculation without discounts"""
        line_items = [
            LineItem(1, "Product A", 2, Decimal('50.00'), TaxCategory.STANDARD),
            LineItem(2, "Product B", 1, Decimal('30.00'), TaxCategory.STANDARD),
        ]
        
        result = self.invoice_calc.calculate_invoice(line_items)
        
        expected_subtotal = Decimal('130.00')  # (2*50) + (1*30)
        expected_tax = Decimal('11.05')        # 130.00 * 0.085
        expected_total = Decimal('141.05')     # 130.00 + 11.05
        
        self.assertEqual(result.subtotal, expected_subtotal)
        self.assertEqual(result.tax_amount, expected_tax)
        self.assertEqual(result.total_amount, expected_total)
        self.assertEqual(result.discount_amount, Decimal('0.00'))
    
    def test_invoice_with_line_item_discounts(self):
        """Test invoice calculation with line item discounts"""
        line_items = [
            LineItem(1, "Product A", 2, Decimal('50.00'), TaxCategory.STANDARD, Decimal('10.00')),
            LineItem(2, "Product B", 1, Decimal('30.00'), TaxCategory.STANDARD),
        ]
        
        result = self.invoice_calc.calculate_invoice(line_items)
        
        expected_subtotal = Decimal('130.00')  # (2*50) + (1*30)
        expected_discount = Decimal('10.00')   # Line item discount
        expected_taxable = Decimal('120.00')   # 130.00 - 10.00
        expected_tax = Decimal('10.20')        # (90.00 * 0.085) + (30.00 * 0.085)
        expected_total = Decimal('130.20')     # 120.00 + 10.20
        
        self.assertEqual(result.subtotal, expected_subtotal)
        self.assertEqual(result.discount_amount, expected_discount)
        self.assertEqual(result.taxable_amount, expected_taxable)
        self.assertEqual(result.tax_amount, expected_tax)
        self.assertEqual(result.total_amount, expected_total)
    
    def test_invoice_with_discount_rules(self):
        """Test invoice calculation with discount rules"""
        line_items = [
            LineItem(1, "Product A", 1, Decimal('100.00'), TaxCategory.STANDARD),
        ]
        
        discount_rules = [
            DiscountRule(
                discount_type=DiscountType.PERCENTAGE,
                value=Decimal('10'),
                min_amount=Decimal('50')
            )
        ]
        
        result = self.invoice_calc.calculate_invoice(line_items, discount_rules)
        
        expected_subtotal = Decimal('100.00')
        expected_discount = Decimal('10.00')   # 10% of 100.00
        expected_taxable = Decimal('90.00')    # 100.00 - 10.00
        expected_tax = Decimal('7.65')         # 90.00 * 0.085
        expected_total = Decimal('97.65')      # 90.00 + 7.65
        
        self.assertEqual(result.subtotal, expected_subtotal)
        self.assertEqual(result.discount_amount, expected_discount)
        self.assertEqual(result.taxable_amount, expected_taxable)
        self.assertEqual(result.tax_amount, expected_tax)
        self.assertEqual(result.total_amount, expected_total)
    
    def test_invoice_with_mixed_tax_categories(self):
        """Test invoice calculation with mixed tax categories"""
        line_items = [
            LineItem(1, "Electronics", 1, Decimal('100.00'), TaxCategory.STANDARD),
            LineItem(2, "Food", 1, Decimal('50.00'), TaxCategory.FOOD),
            LineItem(3, "Medicine", 1, Decimal('25.00'), TaxCategory.MEDICAL),
        ]
        
        result = self.invoice_calc.calculate_invoice(line_items)
        
        expected_subtotal = Decimal('175.00')
        expected_tax = Decimal('11.00')        # (100*0.085) + (50*0.05) + (25*0.00)
        expected_total = Decimal('186.00')
        
        self.assertEqual(result.subtotal, expected_subtotal)
        self.assertEqual(result.tax_amount, expected_tax)
        self.assertEqual(result.total_amount, expected_total)
    
    def test_empty_invoice_calculation(self):
        """Test invoice calculation with no line items"""
        result = self.invoice_calc.calculate_invoice([])
        
        self.assertEqual(result.subtotal, Decimal('0.00'))
        self.assertEqual(result.discount_amount, Decimal('0.00'))
        self.assertEqual(result.taxable_amount, Decimal('0.00'))
        self.assertEqual(result.tax_amount, Decimal('0.00'))
        self.assertEqual(result.total_amount, Decimal('0.00'))
        self.assertEqual(len(result.line_items), 0)
    
    def test_change_calculation(self):
        """Test change calculation"""
        total_amount = Decimal('97.65')
        amount_paid = Decimal('100.00')
        
        change = self.invoice_calc.calculate_change(total_amount, amount_paid)
        expected = Decimal('2.35')
        
        self.assertEqual(change, expected)
    
    def test_negative_change_calculation(self):
        """Test change calculation when payment is insufficient"""
        total_amount = Decimal('100.00')
        amount_paid = Decimal('90.00')
        
        change = self.invoice_calc.calculate_change(total_amount, amount_paid)
        expected = Decimal('-10.00')
        
        self.assertEqual(change, expected)
    
    def test_split_payment_calculation(self):
        """Test split payment calculation"""
        total_amount = Decimal('100.00')
        num_ways = 3
        
        amounts = self.invoice_calc.split_payment(total_amount, num_ways)
        
        # Should split as evenly as possible
        self.assertEqual(len(amounts), 3)
        self.assertEqual(sum(amounts), total_amount)
        # First person might pay slightly more due to rounding
        self.assertTrue(all(amount >= Decimal('33.33') for amount in amounts))
        self.assertTrue(all(amount <= Decimal('33.34') for amount in amounts))
    
    def test_split_payment_invalid_ways(self):
        """Test split payment with invalid number of ways"""
        total_amount = Decimal('100.00')
        
        with self.assertRaises(ValueError):
            self.invoice_calc.split_payment(total_amount, 0)
        
        with self.assertRaises(ValueError):
            self.invoice_calc.split_payment(total_amount, -1)

class TestUtilityFunctions(unittest.TestCase):
    """Test utility calculation functions"""
    
    def test_markup_price_calculation(self):
        """Test markup price calculation"""
        cost_price = Decimal('100.00')
        markup_percentage = Decimal('25')
        
        selling_price = calculate_markup_price(cost_price, markup_percentage)
        expected = Decimal('125.00')
        
        self.assertEqual(selling_price, expected)
    
    def test_margin_percentage_calculation(self):
        """Test profit margin percentage calculation"""
        cost_price = Decimal('80.00')
        selling_price = Decimal('100.00')
        
        margin = calculate_margin_percentage(cost_price, selling_price)
        expected = Decimal('20.00')  # (100-80)/100 * 100 = 20%
        
        self.assertEqual(margin, expected)
    
    def test_margin_percentage_zero_selling_price(self):
        """Test margin calculation with zero selling price"""
        cost_price = Decimal('80.00')
        selling_price = Decimal('0.00')
        
        margin = calculate_margin_percentage(cost_price, selling_price)
        expected = Decimal('0.00')
        
        self.assertEqual(margin, expected)
    
    def test_break_even_quantity_calculation(self):
        """Test break-even quantity calculation"""
        fixed_costs = Decimal('1000.00')
        unit_price = Decimal('50.00')
        variable_cost = Decimal('30.00')
        
        break_even = calculate_break_even_quantity(fixed_costs, unit_price, variable_cost)
        expected = 50  # 1000 / (50-30) = 50
        
        self.assertEqual(break_even, expected)
    
    def test_break_even_invalid_contribution_margin(self):
        """Test break-even calculation with invalid contribution margin"""
        fixed_costs = Decimal('1000.00')
        unit_price = Decimal('20.00')
        variable_cost = Decimal('30.00')  # Higher than unit price
        
        with self.assertRaises(ValueError):
            calculate_break_even_quantity(fixed_costs, unit_price, variable_cost)

class TestSampleData(unittest.TestCase):
    """Test sample data creation functions"""
    
    def test_sample_line_items_creation(self):
        """Test sample line items creation"""
        line_items = create_sample_line_items()
        
        self.assertIsInstance(line_items, list)
        self.assertGreater(len(line_items), 0)
        
        for item in line_items:
            self.assertIsInstance(item, LineItem)
            self.assertGreater(item.quantity, 0)
            self.assertGreater(item.unit_price, Decimal('0'))
    
    def test_sample_discount_rules_creation(self):
        """Test sample discount rules creation"""
        rules = create_sample_discount_rules()
        
        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)
        
        for rule in rules:
            self.assertIsInstance(rule, DiscountRule)
            self.assertIsInstance(rule.discount_type, DiscountType)
            self.assertGreater(rule.value, Decimal('0'))

class TestComplexScenarios(unittest.TestCase):
    """Test complex real-world scenarios"""
    
    def setUp(self):
        self.invoice_calc = InvoiceCalculator()
    
    def test_complex_invoice_scenario(self):
        """Test complex invoice with multiple discounts and tax categories"""
        # Create a complex scenario
        line_items = [
            LineItem(1, "MacBook Pro", 1, Decimal('2799.00'), TaxCategory.STANDARD),
            LineItem(2, "iPhone 15 Pro", 2, Decimal('1199.00'), TaxCategory.STANDARD, Decimal('100.00')),
            LineItem(3, "Organic Food", 3, Decimal('15.99'), TaxCategory.FOOD),
            LineItem(4, "Prescription Medicine", 1, Decimal('89.99'), TaxCategory.MEDICAL),
        ]
        
        # VIP customer
        customer = Customer(1, "VIP Customer", "vip")
        
        # Multiple discount rules
        discount_rules = [
            # 5% off orders over $1000
            DiscountRule(
                discount_type=DiscountType.PERCENTAGE,
                value=Decimal('5'),
                min_amount=Decimal('1000')
            ),
            # VIP customer additional discount
            DiscountRule(
                discount_type=DiscountType.CUSTOMER_TIER,
                value=Decimal('10'),
                customer_tier="vip"
            )
        ]
        
        result = self.invoice_calc.calculate_invoice(line_items, discount_rules, customer)
        
        # Verify the calculation is reasonable
        self.assertGreater(result.subtotal, Decimal('4000'))
        self.assertGreater(result.discount_amount, Decimal('200'))  # Should have significant discounts
        self.assertGreater(result.tax_amount, Decimal('100'))       # Should have reasonable tax
        self.assertGreater(result.total_amount, Decimal('3500'))    # Final total should be reasonable
        
        # Verify line items are properly calculated
        self.assertEqual(len(result.line_items), 4)
        
        # Check that medical items have no tax
        medical_item = next(item for item in result.line_items if item['product_id'] == 4)
        self.assertEqual(medical_item['tax_amount'], Decimal('0.00'))

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestTaxCalculator,
        TestDiscountCalculator,
        TestInvoiceCalculator,
        TestUtilityFunctions,
        TestSampleData,
        TestComplexScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")