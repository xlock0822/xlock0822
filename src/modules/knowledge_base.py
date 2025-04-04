from typing import Dict, List, Optional
import json
import os

class KnowledgeBase:
    def __init__(self):
        self.categories = {
            'products': self._load_products(),
            'services': self._load_services(),
            'faqs': self._load_faqs(),
            'troubleshooting': self._load_troubleshooting(),
            'policies': self._load_policies()
        }
        
    def _load_products(self) -> Dict:
        return {
            'basic_plan': {
                'name': 'Basic Plan',
                'description': 'Perfect for individuals and small projects',
                'price': '$19.99/month',
                'features': [
                    'Core functionality',
                    'Email support',
                    '5GB storage',
                    'Basic analytics'
                ],
                'comparison_points': {
                    'storage': '5GB',
                    'support': 'Email',
                    'users': '1-3',
                    'analytics': 'Basic'
                }
            },
            'pro_plan': {
                'name': 'Pro Plan',
                'description': 'Ideal for growing businesses',
                'price': '$49.99/month',
                'features': [
                    'All Basic features',
                    'Priority support',
                    '50GB storage',
                    'Advanced analytics',
                    'API access'
                ],
                'comparison_points': {
                    'storage': '50GB',
                    'support': 'Priority',
                    'users': '1-10',
                    'analytics': 'Advanced'
                }
            },
            'enterprise': {
                'name': 'Enterprise Plan',
                'description': 'Custom solutions for large organizations',
                'price': 'Custom pricing',
                'features': [
                    'All Pro features',
                    'Dedicated support',
                    'Unlimited storage',
                    'Custom analytics',
                    'Full API access',
                    'Custom integrations'
                ],
                'comparison_points': {
                    'storage': 'Unlimited',
                    'support': 'Dedicated',
                    'users': 'Unlimited',
                    'analytics': 'Custom'
                }
            }
        }

    def _load_services(self) -> Dict:
        return {
            'implementation': {
                'name': 'Implementation Services',
                'description': 'Full setup and integration of our solutions',
                'process': [
                    'Initial consultation',
                    'Requirements gathering',
                    'Custom configuration',
                    'Integration setup',
                    'Team training'
                ],
                'timeline': '2-4 weeks',
                'pricing': 'Custom quote based on requirements'
            },
            'training': {
                'name': 'Training Services',
                'description': 'Comprehensive training for your team',
                'options': [
                    'Basic user training',
                    'Admin training',
                    'Developer training',
                    'Custom workshops'
                ],
                'duration': '1-5 days',
                'pricing': 'Starting at $999 per session'
            },
            'support': {
                'name': 'Technical Support',
                'description': 'Multi-tier technical support options',
                'levels': {
                    'basic': {
                        'response_time': '24 hours',
                        'channels': ['Email'],
                        'hours': '9-5 EST'
                    },
                    'premium': {
                        'response_time': '4 hours',
                        'channels': ['Email', 'Phone', 'Chat'],
                        'hours': '24/7'
                    }
                }
            }
        }

    def _load_faqs(self) -> List[Dict]:
        return [
            {
                'question': 'How do I reset my password?',
                'answer': 'You can reset your password by clicking the "Forgot Password" link on the login page. Follow the instructions sent to your email.',
                'category': 'account',
                'related': ['login issues', 'account security']
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': 'We accept credit cards (Visa, MasterCard, AMEX), PayPal, and bank transfers for annual subscriptions.',
                'category': 'billing',
                'related': ['subscription', 'payment']
            },
            {
                'question': 'How do I upgrade my plan?',
                'answer': 'Log into your account, go to Subscription Settings, and click "Upgrade Plan". Choose your new plan and confirm the changes.',
                'category': 'billing',
                'related': ['plans', 'pricing']
            },
            # Add more FAQs as needed
        ]

    def _load_troubleshooting(self) -> Dict:
        return {
            'login_issues': {
                'symptoms': [
                    'Cannot log in',
                    'Password not working',
                    'Account locked'
                ],
                'solutions': [
                    'Clear browser cache and cookies',
                    'Reset password using forgot password link',
                    'Check caps lock is off',
                    'Use correct email address'
                ],
                'prevention': [
                    'Use a password manager',
                    'Enable two-factor authentication',
                    'Keep email address updated'
                ]
            },
            'performance_issues': {
                'symptoms': [
                    'Slow loading',
                    'Features not responding',
                    'Error messages'
                ],
                'solutions': [
                    'Check internet connection',
                    'Clear browser cache',
                    'Update browser to latest version',
                    'Disable browser extensions'
                ],
                'prevention': [
                    'Keep browser updated',
                    'Regular cache clearing',
                    'Check system requirements'
                ]
            }
        }

    def _load_policies(self) -> Dict:
        return {
            'privacy': {
                'summary': 'We protect your data and privacy',
                'key_points': [
                    'Data collection and usage',
                    'Information sharing',
                    'Security measures',
                    'User rights'
                ],
                'last_updated': '2024-01-01'
            },
            'refund': {
                'summary': 'Our refund policy ensures customer satisfaction',
                'terms': [
                    '30-day money-back guarantee',
                    'Pro-rated refunds for annual plans',
                    'Non-refundable custom development'
                ],
                'process': [
                    'Contact support',
                    'Provide order details',
                    'Specify reason',
                    'Choose refund method'
                ]
            },
            'security': {
                'summary': 'Enterprise-grade security measures',
                'features': [
                    'Data encryption',
                    'Regular backups',
                    'Access controls',
                    'Compliance standards'
                ],
                'certifications': [
                    'ISO 27001',
                    'SOC 2',
                    'GDPR compliant'
                ]
            }
        }

    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search the knowledge base for relevant information"""
        results = []
        search_terms = query.lower().split()
        
        # Search in specific category if provided
        if category and category in self.categories:
            results.extend(self._search_category(category, search_terms))
        else:
            # Search all categories
            for cat in self.categories:
                results.extend(self._search_category(cat, search_terms))
        
        return results

    def _search_category(self, category: str, search_terms: List[str]) -> List[Dict]:
        """Search within a specific category"""
        results = []
        data = self.categories[category]
        
        if isinstance(data, dict):
            for key, value in data.items():
                if self._matches_search(value, search_terms):
                    results.append({
                        'category': category,
                        'key': key,
                        'data': value
                    })
        elif isinstance(data, list):
            for item in data:
                if self._matches_search(item, search_terms):
                    results.append({
                        'category': category,
                        'data': item
                    })
        
        return results

    def _matches_search(self, data: Any, search_terms: List[str]) -> bool:
        """Check if data matches search terms"""
        data_str = json.dumps(data).lower()
        return all(term in data_str for term in search_terms)

    def get_product_comparison(self, products: List[str]) -> Dict:
        """Generate a comparison of specified products"""
        comparison = {}
        for product in products:
            if product in self.categories['products']:
                comparison[product] = self.categories['products'][product]['comparison_points']
        return comparison

    def get_related_articles(self, category: str, key: str) -> List[Dict]:
        """Get related articles for a specific item"""
        results = []
        if category in self.categories:
            # Implementation depends on your relationship logic
            pass
        return results