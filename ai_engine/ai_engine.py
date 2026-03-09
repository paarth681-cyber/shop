"""
Shop Manager Pro - AI Engine
Integrated AI tools for sales forecasting, NLP search, and GPT assistance
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Optional, Any
import re
import json
import math
from collections import Counter
import requests
import threading
import time
from logs.logger_config import log_info, log_error, log_user_action


class MLForecaster:
    """Machine Learning forecasting engine for sales prediction"""
    
    def __init__(self, db_path: str = "shop.db"):
        self.db_path = db_path
        self.models = {}
        
    def get_historical_data(self, days_back: int = 365) -> pd.DataFrame:
        """Get historical sales data for analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            query = """
                SELECT 
                    DATE(s.date) as sale_date,
                    COUNT(s.id) as transaction_count,
                    SUM(s.total_amount) as total_sales,
                    AVG(s.total_amount) as avg_transaction,
                    SUM(sl.qty) as total_items_sold
                FROM sales s
                LEFT JOIN sale_lines sl ON s.id = sl.sale_id
                WHERE s.date >= ?
                GROUP BY DATE(s.date)
                ORDER BY sale_date
            """
            
            df = pd.read_sql_query(query, conn, params=(start_date.strftime('%Y-%m-%d'),))
            conn.close()
            
            if len(df) > 0:
                df['sale_date'] = pd.to_datetime(df['sale_date'])
                df['day_of_week'] = df['sale_date'].dt.dayofweek
                df['month'] = df['sale_date'].dt.month
                df['day_of_month'] = df['sale_date'].dt.day
                
            log_info(f"Retrieved {len(df)} days of historical data for ML forecasting")
            return df
            
        except Exception as e:
            log_error(f"Failed to get historical data: {e}")
            return pd.DataFrame()
    
    def simple_moving_average(self, data: List[float], window: int = 7) -> List[float]:
        """Calculate simple moving average"""
        if len(data) < window:
            return data
        
        ma = []
        for i in range(len(data)):
            if i < window - 1:
                ma.append(data[i])
            else:
                window_avg = sum(data[i-window+1:i+1]) / window
                ma.append(window_avg)
        
        return ma
    
    def exponential_smoothing(self, data: List[float], alpha: float = 0.3) -> List[float]:
        """Exponential smoothing for trend analysis"""
        if not data:
            return []
        
        result = [data[0]]
        for i in range(1, len(data)):
            smoothed = alpha * data[i] + (1 - alpha) * result[i-1]
            result.append(smoothed)
        
        return result
    
    def detect_trend(self, data: List[float]) -> Dict[str, Any]:
        """Detect trend in data using linear regression"""
        if len(data) < 2:
            return {"trend": "insufficient_data", "slope": 0, "confidence": 0}
        
        x = list(range(len(data)))
        n = len(data)
        
        # Calculate linear regression
        sum_x = sum(x)
        sum_y = sum(data)
        sum_xy = sum(x[i] * data[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate R-squared for confidence
        y_pred = [intercept + slope * x[i] for i in range(n)]
        ss_res = sum((data[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((data[i] - sum_y/n) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        
        return {
            "trend": trend,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "confidence": min(r_squared, 1.0)
        }
    
    def forecast_sales(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate sales forecast for specified days ahead"""
        try:
            df = self.get_historical_data()
            
            if len(df) < 7:
                return {
                    "error": "Insufficient historical data",
                    "message": "Need at least 7 days of sales data for forecasting"
                }
            
            # Prepare data
            sales_data = df['total_sales'].fillna(0).tolist()
            
            # Apply smoothing
            smoothed_data = self.exponential_smoothing(sales_data)
            
            # Detect trend
            trend_info = self.detect_trend(smoothed_data)
            
            # Generate forecasts
            forecasts = []
            last_value = smoothed_data[-1] if smoothed_data else 0
            
            for i in range(1, days_ahead + 1):
                # Simple linear projection with trend
                forecast_value = last_value + (trend_info["slope"] * i)
                
                # Add seasonal adjustment (simple day-of-week pattern)
                if len(df) >= 14:  # Need at least 2 weeks for pattern
                    day_of_week = (df.iloc[-1]['day_of_week'] + i) % 7
                    weekly_pattern = df.groupby('day_of_week')['total_sales'].mean()
                    if day_of_week in weekly_pattern.index:
                        seasonal_factor = weekly_pattern[day_of_week] / weekly_pattern.mean()
                        forecast_value *= seasonal_factor
                
                # Ensure non-negative forecast
                forecast_value = max(0, forecast_value)
                
                forecast_date = datetime.now() + timedelta(days=i)
                forecasts.append({
                    "date": forecast_date.strftime('%Y-%m-%d'),
                    "predicted_sales": round(forecast_value, 2),
                    "confidence": trend_info["confidence"]
                })
            
            # Calculate summary statistics
            total_forecast = sum(f["predicted_sales"] for f in forecasts)
            avg_daily_forecast = total_forecast / len(forecasts) if forecasts else 0
            historical_avg = df['total_sales'].mean() if len(df) > 0 else 0
            
            result = {
                "forecasts": forecasts,
                "summary": {
                    "total_predicted_sales": round(total_forecast, 2),
                    "avg_daily_prediction": round(avg_daily_forecast, 2),
                    "historical_avg_daily": round(historical_avg, 2),
                    "trend": trend_info["trend"],
                    "confidence": round(trend_info["confidence"], 2),
                    "growth_rate": round(trend_info["slope"], 2)
                },
                "model_info": {
                    "data_points_used": len(df),
                    "forecast_method": "exponential_smoothing_with_trend",
                    "seasonal_adjustment": "day_of_week_pattern"
                }
            }
            
            log_user_action("ml_forecast_generated", f"days_ahead: {days_ahead}, confidence: {trend_info['confidence']:.2f}")
            return result
            
        except Exception as e:
            log_error(f"ML forecasting error: {e}")
            return {
                "error": "Forecasting failed",
                "message": str(e)
            }


class NLPEngine:
    """Natural Language Processing engine for intelligent search"""
    
    def __init__(self, db_path: str = "shop.db"):
        self.db_path = db_path
        self.product_vectors = {}
        self.vocabulary = {}
        self.idf_scores = {}
        
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if not text:
            return []
        
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def build_vocabulary(self, documents: List[str]) -> Dict[str, int]:
        """Build vocabulary from documents"""
        word_counts = Counter()
        
        for doc in documents:
            tokens = self.tokenize(doc)
            word_counts.update(tokens)
        
        # Create vocabulary with words appearing at least twice
        vocabulary = {}
        idx = 0
        for word, count in word_counts.items():
            if count >= 2:  # Filter rare words
                vocabulary[word] = idx
                idx += 1
        
        return vocabulary
    
    def calculate_tf(self, document: str, vocabulary: Dict[str, int]) -> np.ndarray:
        """Calculate term frequency vector"""
        tokens = self.tokenize(document)
        tf_vector = np.zeros(len(vocabulary))
        
        if not tokens:
            return tf_vector
        
        token_counts = Counter(tokens)
        
        for token, count in token_counts.items():
            if token in vocabulary:
                tf_vector[vocabulary[token]] = count / len(tokens)
        
        return tf_vector
    
    def calculate_idf(self, documents: List[str], vocabulary: Dict[str, int]) -> Dict[str, float]:
        """Calculate inverse document frequency"""
        idf_scores = {}
        n_docs = len(documents)
        
        for word, idx in vocabulary.items():
            # Count documents containing this word
            doc_count = sum(1 for doc in documents if word in self.tokenize(doc))
            
            # Calculate IDF
            idf = math.log(n_docs / (doc_count + 1))  # +1 for smoothing
            idf_scores[word] = idf
        
        return idf_scores
    
    def calculate_tfidf(self, document: str) -> np.ndarray:
        """Calculate TF-IDF vector for a document"""
        tf_vector = self.calculate_tf(document, self.vocabulary)
        tfidf_vector = np.zeros(len(self.vocabulary))
        
        for word, idx in self.vocabulary.items():
            tfidf_vector[idx] = tf_vector[idx] * self.idf_scores.get(word, 0)
        
        return tfidf_vector
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def build_product_index(self):
        """Build search index for products"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, sku, name, description, sell_price, quantity
                FROM products
                ORDER BY id
            """)
            
            products = cursor.fetchall()
            conn.close()
            
            if not products:
                log_info("No products found for NLP indexing")
                return
            
            # Create documents for each product
            documents = []
            product_info = []
            
            for product_id, sku, name, description, price, quantity in products:
                # Combine all searchable text
                document = f"{sku} {name} {description or ''}"
                documents.append(document)
                product_info.append({
                    'id': product_id,
                    'sku': sku,
                    'name': name,
                    'description': description,
                    'price': price,
                    'quantity': quantity
                })
            
            # Build vocabulary and calculate IDF
            self.vocabulary = self.build_vocabulary(documents)
            self.idf_scores = self.calculate_idf(documents, self.vocabulary)
            
            # Calculate TF-IDF vectors for all products
            self.product_vectors = {}
            for i, (doc, info) in enumerate(zip(documents, product_info)):
                tfidf_vector = self.calculate_tfidf(doc)
                self.product_vectors[info['id']] = {
                    'vector': tfidf_vector,
                    'info': info,
                    'document': doc
                }
            
            log_info(f"Built NLP index for {len(products)} products with {len(self.vocabulary)} terms")
            
        except Exception as e:
            log_error(f"Failed to build product search index: {e}")
    
    def intelligent_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform intelligent product search using NLP"""
        try:
            if not self.product_vectors:
                self.build_product_index()
            
            if not self.product_vectors:
                return []
            
            # Calculate query vector
            query_vector = self.calculate_tfidf(query)
            
            # Calculate similarities
            results = []
            for product_id, product_data in self.product_vectors.items():
                similarity = self.cosine_similarity(query_vector, product_data['vector'])
                
                if similarity > 0:  # Only include relevant results
                    result = product_data['info'].copy()
                    result['relevance_score'] = round(similarity, 4)
                    result['match_explanation'] = self.explain_match(query, product_data['document'], similarity)
                    results.append(result)
            
            # Sort by relevance
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            log_user_action("nlp_search_performed", f"query: '{query}', results: {len(results)}")
            return results[:limit]
            
        except Exception as e:
            log_error(f"NLP search error: {e}")
            return []
    
    def explain_match(self, query: str, document: str, similarity: float) -> str:
        """Explain why a product matched the search query"""
        query_tokens = self.tokenize(query)
        doc_tokens = self.tokenize(document)
        
        # Find matching terms
        matching_terms = set(query_tokens) & set(doc_tokens)
        
        if not matching_terms:
            return "General relevance match"
        
        if similarity > 0.5:
            return f"Strong match: {', '.join(matching_terms)}"
        elif similarity > 0.2:
            return f"Good match: {', '.join(matching_terms)}"
        else:
            return f"Partial match: {', '.join(matching_terms)}"
    
    def get_recommendations(self, product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get product recommendations based on similarity"""
        try:
            if not self.product_vectors or product_id not in self.product_vectors:
                return []
            
            target_vector = self.product_vectors[product_id]['vector']
            recommendations = []
            
            for pid, product_data in self.product_vectors.items():
                if pid != product_id:  # Don't recommend the same product
                    similarity = self.cosine_similarity(target_vector, product_data['vector'])
                    
                    if similarity > 0.1:  # Minimum similarity threshold
                        result = product_data['info'].copy()
                        result['similarity_score'] = round(similarity, 4)
                        recommendations.append(result)
            
            # Sort by similarity
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            log_user_action("product_recommendations_generated", f"product_id: {product_id}, recommendations: {len(recommendations)}")
            return recommendations[:limit]
            
        except Exception as e:
            log_error(f"Product recommendations error: {e}")
            return []


class GPTAssistant:
    """GPT-powered assistant for natural language queries and reports"""
    
    def __init__(self, db_path: str = "shop.db"):
        self.db_path = db_path
        self.api_key = None
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    def set_api_key(self, api_key: str):
        """Set OpenAI API key"""
        self.api_key = api_key
    
    def get_business_context(self) -> str:
        """Get current business data for context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get summary statistics
            context_data = {}
            
            # Sales summary
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_sale,
                    DATE(MIN(date)) as first_sale,
                    DATE(MAX(date)) as last_sale
                FROM sales
            """)
            sales_data = cursor.fetchone()
            
            # Product summary
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(quantity) as total_inventory,
                    AVG(sell_price) as avg_price,
                    COUNT(CASE WHEN quantity < 10 THEN 1 END) as low_stock_items
                FROM products
            """)
            product_data = cursor.fetchone()
            
            # Customer summary
            cursor.execute("SELECT COUNT(*) as total_customers FROM customers")
            customer_count = cursor.fetchone()[0]
            
            # Recent sales (last 30 days)
            cursor.execute("""
                SELECT 
                    COUNT(*) as recent_sales,
                    SUM(total_amount) as recent_revenue
                FROM sales 
                WHERE date >= date('now', '-30 days')
            """)
            recent_data = cursor.fetchone()
            
            conn.close()
            
            # Format context
            context = f"""
Business Data Context:
- Total Sales: {sales_data[0]} transactions
- Total Revenue: ${sales_data[1] or 0:.2f}
- Average Sale: ${sales_data[2] or 0:.2f}
- Sales Period: {sales_data[3] or 'N/A'} to {sales_data[4] or 'N/A'}
- Total Products: {product_data[0]}
- Total Inventory: {product_data[1] or 0} items
- Average Product Price: ${product_data[2] or 0:.2f}
- Low Stock Items: {product_data[3] or 0}
- Total Customers: {customer_count}
- Recent Sales (30 days): {recent_data[0]} transactions, ${recent_data[1] or 0:.2f}
"""
            
            return context
            
        except Exception as e:
            log_error(f"Failed to get business context: {e}")
            return "Business data context unavailable."
    
    def query_gpt(self, prompt: str, system_context: str = None) -> Dict[str, Any]:
        """Query GPT API with business context"""
        if not self.api_key:
            return {
                "error": "GPT API key not configured",
                "message": "Please set your OpenAI API key to use GPT features"
            }
        
        try:
            # Prepare messages
            messages = []
            
            if system_context:
                messages.append({
                    "role": "system",
                    "content": system_context
                })
            
            # Add business context
            business_context = self.get_business_context()
            messages.append({
                "role": "system",
                "content": f"You are an AI assistant for Shop Manager Pro, a retail management system. Here's the current business data:\n{business_context}"
            })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    log_user_action("gpt_query_successful", f"prompt_length: {len(prompt)}, response_length: {len(content)}")
                    
                    return {
                        "response": content,
                        "usage": result.get("usage", {}),
                        "model": result.get("model", "gpt-3.5-turbo")
                    }
                else:
                    return {"error": "No response from GPT", "message": "API returned empty response"}
            else:
                error_detail = response.json() if response.content else {"error": "Unknown error"}
                return {
                    "error": f"GPT API error: {response.status_code}",
                    "message": error_detail.get("error", {}).get("message", "Unknown API error")
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Request timeout", "message": "GPT API request timed out"}
        except Exception as e:
            log_error(f"GPT query error: {e}")
            return {"error": "GPT query failed", "message": str(e)}
    
    def generate_sales_report_summary(self, period_days: int = 30) -> str:
        """Generate AI-powered sales report summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get detailed sales data
            query = """
                SELECT 
                    DATE(s.date) as sale_date,
                    COUNT(s.id) as transactions,
                    SUM(s.total_amount) as daily_revenue,
                    AVG(s.total_amount) as avg_transaction
                FROM sales s
                WHERE s.date >= ?
                GROUP BY DATE(s.date)
                ORDER BY sale_date
            """
            
            df = pd.read_sql_query(query, conn, params=(start_date.strftime('%Y-%m-%d'),))
            
            # Get top products
            top_products_query = """
                SELECT 
                    p.name,
                    SUM(sl.qty) as units_sold,
                    SUM(sl.line_total) as revenue
                FROM sale_lines sl
                JOIN sales s ON sl.sale_id = s.id
                JOIN products p ON sl.product_id = p.id
                WHERE s.date >= ?
                GROUP BY p.id, p.name
                ORDER BY revenue DESC
                LIMIT 5
            """
            
            top_products = pd.read_sql_query(top_products_query, conn, params=(start_date.strftime('%Y-%m-%d'),))
            conn.close()
            
            # Prepare data summary for GPT
            if len(df) > 0:
                total_revenue = df['daily_revenue'].sum()
                total_transactions = df['transactions'].sum()
                avg_daily_revenue = df['daily_revenue'].mean()
                best_day_revenue = df['daily_revenue'].max()
                worst_day_revenue = df['daily_revenue'].min()
                
                data_summary = f"""
Sales Data Summary ({period_days} days):
- Total Revenue: ${total_revenue:.2f}
- Total Transactions: {total_transactions}
- Average Daily Revenue: ${avg_daily_revenue:.2f}
- Best Day Revenue: ${best_day_revenue:.2f}
- Worst Day Revenue: ${worst_day_revenue:.2f}
- Number of Active Days: {len(df)}

Top 5 Products by Revenue:
"""
                
                for _, product in top_products.iterrows():
                    data_summary += f"- {product['name']}: {product['units_sold']} units, ${product['revenue']:.2f}\n"
                
                # Query GPT for analysis
                prompt = f"""
Analyze this sales data and provide a comprehensive business report summary. Include:
1. Overall performance assessment
2. Key trends and insights
3. Areas of concern or opportunity
4. Actionable recommendations

{data_summary}

Please provide a professional, concise analysis suitable for management review.
"""
                
                result = self.query_gpt(prompt)
                
                if "response" in result:
                    return result["response"]
                else:
                    return f"GPT Analysis unavailable: {result.get('error', 'Unknown error')}"
            else:
                return f"No sales data available for the last {period_days} days."
                
        except Exception as e:
            log_error(f"Failed to generate AI sales report: {e}")
            return f"Error generating sales report: {str(e)}"
    
    def process_natural_query(self, user_query: str) -> str:
        """Process natural language business queries"""
        system_prompt = """
You are a business intelligence assistant for Shop Manager Pro. 
Respond to user questions about their retail business with helpful, actionable insights.
Keep responses concise but informative. If you need more specific data to answer accurately, suggest what information would be helpful.
Focus on practical business advice and insights.
"""
        
        result = self.query_gpt(user_query, system_prompt)
        
        if "response" in result:
            log_user_action("natural_query_processed", f"query_length: {len(user_query)}")
            return result["response"]
        else:
            return f"I apologize, but I couldn't process your query due to: {result.get('error', 'Unknown error')}"


class AIEngine:
    """Main AI Engine coordinating all AI capabilities"""
    
    def __init__(self, db_path: str = "shop.db"):
        self.db_path = db_path
        self.ml_forecaster = MLForecaster(db_path)
        self.nlp_engine = NLPEngine(db_path)
        self.gpt_assistant = GPTAssistant(db_path)
        self.initialized = False
        
        log_info("AI Engine initialized with ML, NLP, and GPT capabilities")
    
    def initialize(self, gpt_api_key: str = None):
        """Initialize AI components"""
        try:
            # Initialize NLP search index
            self.nlp_engine.build_product_index()
            
            # Set GPT API key if provided
            if gpt_api_key:
                self.gpt_assistant.set_api_key(gpt_api_key)
            
            self.initialized = True
            log_info("AI Engine fully initialized")
            
        except Exception as e:
            log_error(f"AI Engine initialization failed: {e}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get information about available AI capabilities"""
        return {
            "ml_forecasting": {
                "available": True,
                "description": "Sales forecasting using machine learning",
                "features": ["trend_analysis", "seasonal_patterns", "confidence_scoring"]
            },
            "nlp_search": {
                "available": len(self.nlp_engine.product_vectors) > 0,
                "description": "Intelligent product search using TF-IDF and cosine similarity",
                "features": ["semantic_search", "product_recommendations", "relevance_scoring"]
            },
            "gpt_assistant": {
                "available": self.gpt_assistant.api_key is not None,
                "description": "Natural language queries and automated reports",
                "features": ["natural_queries", "report_summaries", "business_insights"]
            },
            "status": "ready" if self.initialized else "initializing"
        }
    
    def smart_search(self, query: str, use_nlp: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform intelligent search with fallback options"""
        if use_nlp and len(self.nlp_engine.product_vectors) > 0:
            return self.nlp_engine.intelligent_search(query, limit)
        else:
            # Fallback to basic database search
            return self._basic_search(query, limit)
    
    def _basic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Basic database search fallback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            search_query = f"%{query.lower()}%"
            cursor.execute("""
                SELECT id, sku, name, description, sell_price, quantity
                FROM products
                WHERE LOWER(name) LIKE ? OR LOWER(sku) LIKE ? OR LOWER(description) LIKE ?
                ORDER BY 
                    CASE 
                        WHEN LOWER(name) LIKE ? THEN 1
                        WHEN LOWER(sku) LIKE ? THEN 2
                        ELSE 3
                    END,
                    name
                LIMIT ?
            """, (search_query, search_query, search_query, search_query, search_query, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "sku": row[1],
                    "name": row[2],
                    "description": row[3],
                    "price": row[4],
                    "quantity": row[5],
                    "relevance_score": 0.5,  # Default relevance for basic search
                    "match_explanation": "Basic text match"
                })
            
            conn.close()
            return results
            
        except Exception as e:
            log_error(f"Basic search failed: {e}")
            return []


# Singleton instance
_ai_engine_instance = None

def get_ai_engine(db_path: str = "shop.db") -> AIEngine:
    """Get singleton AI Engine instance"""
    global _ai_engine_instance
    if _ai_engine_instance is None:
        _ai_engine_instance = AIEngine(db_path)
    return _ai_engine_instance


if __name__ == "__main__":
    # Test the AI Engine
    ai = AIEngine()
    ai.initialize()
    
    print("=== AI Engine Test ===")
    print(f"Capabilities: {ai.get_capabilities()}")
    
    # Test ML forecasting
    print("\n=== ML Forecasting Test ===")
    forecast = ai.ml_forecaster.forecast_sales(7)
    if "error" not in forecast:
        print(f"7-day forecast: {forecast['summary']['total_predicted_sales']:.2f}")
    else:
        print(f"Forecast error: {forecast['error']}")
    
    # Test NLP search
    print("\n=== NLP Search Test ===")
    results = ai.smart_search("laptop computer")
    print(f"Search results: {len(results)} items found")
    for result in results[:3]:
        print(f"- {result['name']}: {result['relevance_score']}")
