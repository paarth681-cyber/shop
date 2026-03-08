#!/usr/bin/env python3
"""
Complete System Demonstration - Shop Manager Pro with AI
Shows all features working together
"""

import sys
import os
import sqlite3
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_database_stats():
    """Show database statistics"""
    print("📊 Database Statistics")
    print("-" * 30)
    
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    
    # Count records
    tables = ['users', 'products', 'customers', 'suppliers', 'sales', 'sale_lines']
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table.capitalize()}: {count}")
    
    # Show sales summary
    cur.execute("SELECT SUM(total_amount), COUNT(*) FROM sales")
    total_sales, num_sales = cur.fetchone()
    print(f"\n  Total Sales Value: ${total_sales:,.2f}")
    print(f"  Number of Transactions: {num_sales}")
    
    # Show recent sales
    cur.execute("""
        SELECT DATE(date), SUM(total_amount), COUNT(*) 
        FROM sales 
        WHERE date >= date('now', '-7 days')
        GROUP BY DATE(date)
        ORDER BY date DESC
        LIMIT 5
    """)
    
    print(f"\n  Recent Daily Sales:")
    for row in cur.fetchall():
        print(f"    {row[0]}: ${row[1]:,.2f} ({row[2]} transactions)")
    
    conn.close()

def demo_ai_search():
    """Demonstrate AI search capabilities"""
    print("\n🔍 AI Smart Search Demo")
    print("-" * 30)
    
    from ai_engine import get_ai_engine
    
    ai = get_ai_engine()
    ai.initialize()
    
    # Demo different types of searches
    searches = [
        ("Exact match", "Gaming Laptop"),
        ("Partial match", "wireless"),
        ("Category search", "gaming"),
        ("Feature search", "4K"),
        ("Fuzzy match", "speaker bluetooth")
    ]
    
    for search_type, query in searches:
        print(f"\n  {search_type}: '{query}'")
        results = ai.smart_search(query, use_nlp=True, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                name = result.get('name', 'N/A')
                price = result.get('price', 0)
                relevance = result.get('relevance_score', 0)
                stock = result.get('quantity', 0)
                print(f"    {i}. {name} - ${price:.2f} (stock: {stock}, relevance: {relevance:.3f})")
        else:
            print("    No results found")

def demo_ml_forecasting():
    """Demonstrate ML forecasting capabilities"""
    print("\n📊 ML Sales Forecasting Demo")
    print("-" * 30)
    
    from ai_engine import get_ai_engine
    
    ai = get_ai_engine()
    ai.initialize()
    
    # Generate forecasts for different periods
    periods = [7, 14, 30]
    
    for days in periods:
        print(f"\n  {days}-Day Forecast:")
        forecast = ai.ml_forecaster.forecast_sales(days)
        
        if "error" not in forecast:
            summary = forecast['summary']
            print(f"    Total Predicted: ${summary['total_predicted_sales']:,.2f}")
            print(f"    Daily Average: ${summary['avg_daily_prediction']:,.2f}")
            print(f"    Trend: {summary['trend']} (confidence: {summary['confidence']:.1%})")
            print(f"    Growth Rate: ${summary['growth_rate']:.2f}/day")
            
            # Show first few days
            print(f"    Next 3 days:")
            for i, pred in enumerate(forecast['forecasts'][:3]):
                date_obj = datetime.strptime(pred['date'], '%Y-%m-%d')
                day_name = date_obj.strftime('%A')
                print(f"      {pred['date']} ({day_name}): ${pred['predicted_sales']:,.2f}")
        else:
            print(f"    Error: {forecast['error']}")

def demo_nlp_recommendations():
    """Demonstrate product recommendation system"""
    print("\n🎯 AI Product Recommendations Demo")
    print("-" * 30)
    
    from ai_engine import get_ai_engine
    
    ai = get_ai_engine()
    ai.initialize()
    
    # Get products for recommendation testing
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM products LIMIT 3")
    products = cur.fetchall()
    conn.close()
    
    for product_id, product_name in products:
        print(f"\n  Recommendations for '{product_name}':")
        recommendations = ai.nlp_engine.get_recommendations(product_id, limit=3)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                name = rec.get('name', 'N/A')
                price = rec.get('price', 0)
                similarity = rec.get('similarity_score', 0)
                print(f"    {i}. {name} - ${price:.2f} (similarity: {similarity:.3f})")
        else:
            print("    No similar products found")

def demo_business_insights():
    """Demonstrate business analytics"""
    print("\n📈 Business Intelligence Demo")
    print("-" * 30)
    
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    
    # Top products by revenue
    print("\n  Top Products by Revenue:")
    cur.execute("""
        SELECT p.name, SUM(sl.line_total) as revenue, SUM(sl.qty) as units_sold
        FROM sale_lines sl
        JOIN products p ON sl.product_id = p.id
        JOIN sales s ON sl.sale_id = s.id
        GROUP BY p.id, p.name
        ORDER BY revenue DESC
        LIMIT 5
    """)
    
    for i, (name, revenue, units) in enumerate(cur.fetchall(), 1):
        print(f"    {i}. {name}: ${revenue:,.2f} ({units} units)")
    
    # Sales by day of week
    print("\n  Sales by Day of Week:")
    cur.execute("""
        SELECT 
            CASE cast(strftime('%w', date) as integer)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                WHEN 6 THEN 'Saturday'
            END as day_name,
            AVG(total_amount) as avg_sale,
            COUNT(*) as num_sales
        FROM sales
        GROUP BY strftime('%w', date)
        ORDER BY strftime('%w', date)
    """)
    
    for day_name, avg_sale, num_sales in cur.fetchall():
        print(f"    {day_name}: ${avg_sale:.2f} avg ({num_sales} sales)")
    
    # Customer analysis
    print("\n  Customer Analysis:")
    cur.execute("""
        SELECT 
            c.name,
            COUNT(s.id) as num_orders,
            SUM(s.total_amount) as total_spent,
            AVG(s.total_amount) as avg_order
        FROM customers c
        JOIN sales s ON c.id = s.customer_id
        WHERE c.name != 'Walk-in Customer'
        GROUP BY c.id, c.name
        ORDER BY total_spent DESC
        LIMIT 5
    """)
    
    for name, orders, total, avg_order in cur.fetchall():
        print(f"    {name}: {orders} orders, ${total:,.2f} total (${avg_order:.2f} avg)")
    
    conn.close()

def demo_system_capabilities():
    """Show overall system capabilities"""
    print("\n🤖 System Capabilities Overview")
    print("-" * 30)
    
    from ai_engine import get_ai_engine
    
    ai = get_ai_engine()
    ai.initialize()
    
    caps = ai.get_capabilities()
    
    print(f"  AI Engine Status: {caps['status'].upper()}")
    print(f"  Features Available:")
    
    for feature, info in caps.items():
        if isinstance(info, dict):
            status_icon = "✅" if info['available'] else "❌"
            print(f"    {status_icon} {feature.replace('_', ' ').title()}")
            print(f"        {info['description']}")
            if info['available']:
                features = ", ".join(info['features'])
                print(f"        Capabilities: {features}")

def main():
    """Main demonstration function"""
    print("🚀 Shop Manager Pro - Complete System Demo")
    print("="*60)
    print("This demonstration shows the AI-enhanced Shop Manager Pro")
    print("system with all components working together.")
    print("="*60)
    
    # Show database stats
    show_database_stats()
    
    # Demo AI capabilities
    demo_system_capabilities()
    
    # Demo AI search
    demo_ai_search()
    
    # Demo ML forecasting
    demo_ml_forecasting()
    
    # Demo recommendations
    demo_nlp_recommendations()
    
    # Demo business insights
    demo_business_insights()
    
    print("\n" + "="*60)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("✅ Database with 60 days of realistic sales data")
    print("✅ AI-powered semantic product search")
    print("✅ Machine learning sales forecasting")
    print("✅ Product recommendation engine")
    print("✅ Business intelligence and analytics")
    print("✅ Professional PyQt6 user interface")
    print("\nTo run the full application:")
    print("  python shop_manager_pro_qt.py")
    print("\nLogin credentials:")
    print("  Admin: admin / admin123")
    print("  Manager: manager / manager123")
    print("  Cashier: cashier / cashier123")
    print("\nThe 🤖 AI Assistant tab contains all AI features!")

if __name__ == "__main__":
    main()