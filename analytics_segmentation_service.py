"""
Analytics Segmentation Service
Provides segmented reporting for purchasing vs. non-purchasing user behavior
"""

from datetime import datetime, timedelta
from models import db, User
from sqlalchemy import text, func
import logging

logger = logging.getLogger(__name__)

class AnalyticsSegmentationService:
    """Service for segmented user analytics and reporting"""
    
    @classmethod
    def get_user_segments(cls):
        """Get basic user segmentation data"""
        try:
            # Users with purchases
            purchasing_users = db.session.query(User).filter(
                User.id.in_(
                    db.session.query(text('user_package.user_id'))
                    .select_from(text('user_package'))
                    .filter(text('user_package.user_id IS NOT NULL'))
                )
            ).all()
            
            # Users without purchases
            non_purchasing_users = db.session.query(User).filter(
                ~User.id.in_(
                    db.session.query(text('user_package.user_id'))
                    .select_from(text('user_package'))
                    .filter(text('user_package.user_id IS NOT NULL'))
                )
            ).all()
            
            return {
                'purchasing_users': purchasing_users,
                'non_purchasing_users': non_purchasing_users,
                'total_users': len(purchasing_users) + len(non_purchasing_users)
            }
            
        except Exception as e:
            logger.error(f"Error getting user segments: {e}")
            return {
                'purchasing_users': [],
                'non_purchasing_users': [],
                'total_users': 0
            }
    
    @classmethod
    def get_conversion_metrics(cls, days=30):
        """Get conversion metrics for specified period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total registrations in period
            total_registrations = db.session.query(User).filter(
                func.date(User.id) >= cutoff_date.date()  # Using id as proxy for registration date
            ).count()
            
            # Conversions in period (users who purchased)
            conversions = db.session.query(User).filter(
                func.date(User.id) >= cutoff_date.date(),
                User.id.in_(
                    db.session.query(text('user_package.user_id'))
                    .select_from(text('user_package'))
                    .filter(text('user_package.user_id IS NOT NULL'))
                )
            ).count()
            
            conversion_rate = (conversions / total_registrations * 100) if total_registrations > 0 else 0
            
            return {
                'period_days': days,
                'total_registrations': total_registrations,
                'conversions': conversions,
                'non_conversions': total_registrations - conversions,
                'conversion_rate': round(conversion_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating conversion metrics: {e}")
            return {
                'period_days': days,
                'total_registrations': 0,
                'conversions': 0,
                'non_conversions': 0,
                'conversion_rate': 0.0
            }
    
    @classmethod
    def get_engagement_analytics(cls):
        """Get engagement analytics segmented by purchasing behavior"""
        try:
            segments = cls.get_user_segments()
            
            # Calculate engagement for purchasing users
            purchasing_engagement = cls._calculate_engagement_metrics(segments['purchasing_users'])
            
            # Calculate engagement for non-purchasing users
            non_purchasing_engagement = cls._calculate_engagement_metrics(segments['non_purchasing_users'])
            
            return {
                'purchasing_users': {
                    'count': len(segments['purchasing_users']),
                    'engagement': purchasing_engagement
                },
                'non_purchasing_users': {
                    'count': len(segments['non_purchasing_users']),
                    'engagement': non_purchasing_engagement
                },
                'total_users': segments['total_users']
            }
            
        except Exception as e:
            logger.error(f"Error calculating engagement analytics: {e}")
            return {
                'purchasing_users': {'count': 0, 'engagement': {}},
                'non_purchasing_users': {'count': 0, 'engagement': {}},
                'total_users': 0
            }
    
    @classmethod
    def _calculate_engagement_metrics(cls, users):
        """Calculate engagement metrics for a list of users"""
        if not users:
            return {
                'avg_last_login_days': 0,
                'active_users_7d': 0,
                'active_users_30d': 0,
                'never_logged_in': 0
            }
        
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        # Calculate metrics
        last_login_days = []
        active_7d = 0
        active_30d = 0
        never_logged_in = 0
        
        for user in users:
            if hasattr(user, 'last_login') and user.last_login:
                days_since_login = (now - user.last_login).days
                last_login_days.append(days_since_login)
                
                if user.last_login >= seven_days_ago:
                    active_7d += 1
                if user.last_login >= thirty_days_ago:
                    active_30d += 1
            else:
                never_logged_in += 1
        
        avg_last_login = sum(last_login_days) / len(last_login_days) if last_login_days else 0
        
        return {
            'avg_last_login_days': round(avg_last_login, 1),
            'active_users_7d': active_7d,
            'active_users_30d': active_30d,
            'never_logged_in': never_logged_in
        }
    
    @classmethod
    def get_revenue_analytics(cls):
        """Get revenue analytics with user segmentation"""
        try:
            # Get package purchase data
            package_data = db.session.execute(text("""
                SELECT 
                    up.package_type,
                    COUNT(*) as purchase_count,
                    COUNT(DISTINCT up.user_id) as unique_buyers
                FROM user_package up 
                GROUP BY up.package_type
            """)).fetchall()
            
            total_revenue = len(package_data) * 25  # $25 per package
            unique_buyers = db.session.execute(text("""
                SELECT COUNT(DISTINCT user_id) as unique_buyers 
                FROM user_package
            """)).fetchone()[0]
            
            return {
                'total_revenue': total_revenue,
                'total_packages_sold': sum(row[1] for row in package_data),
                'unique_buyers': unique_buyers,
                'avg_revenue_per_user': round(total_revenue / unique_buyers, 2) if unique_buyers > 0 else 0,
                'package_breakdown': [
                    {
                        'package_type': row[0],
                        'sales_count': row[1],
                        'revenue': row[1] * 25
                    } for row in package_data
                ]
            }
            
        except Exception as e:
            logger.error(f"Error calculating revenue analytics: {e}")
            return {
                'total_revenue': 0,
                'total_packages_sold': 0,
                'unique_buyers': 0,
                'avg_revenue_per_user': 0,
                'package_breakdown': []
            }
    
    @classmethod
    def get_comprehensive_report(cls):
        """Get comprehensive analytics report with all segments"""
        try:
            user_segments = cls.get_user_segments()
            conversion_metrics = cls.get_conversion_metrics()
            engagement_analytics = cls.get_engagement_analytics()
            revenue_analytics = cls.get_revenue_analytics()
            
            return {
                'report_generated_at': datetime.utcnow().isoformat(),
                'user_segments': {
                    'total_users': user_segments['total_users'],
                    'purchasing_users_count': len(user_segments['purchasing_users']),
                    'non_purchasing_users_count': len(user_segments['non_purchasing_users']),
                    'purchase_conversion_rate': round(
                        (len(user_segments['purchasing_users']) / user_segments['total_users'] * 100) 
                        if user_segments['total_users'] > 0 else 0, 2
                    )
                },
                'conversion_metrics': conversion_metrics,
                'engagement_analytics': engagement_analytics,
                'revenue_analytics': revenue_analytics
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {
                'report_generated_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }

def generate_daily_analytics_report():
    """Generate daily analytics report for monitoring"""
    logger.info("Generating daily analytics report")
    
    report = AnalyticsSegmentationService.get_comprehensive_report()
    
    logger.info(f"Analytics Report Generated:")
    logger.info(f"- Total Users: {report.get('user_segments', {}).get('total_users', 0)}")
    logger.info(f"- Purchasing Users: {report.get('user_segments', {}).get('purchasing_users_count', 0)}")
    logger.info(f"- Conversion Rate: {report.get('user_segments', {}).get('purchase_conversion_rate', 0)}%")
    logger.info(f"- Total Revenue: ${report.get('revenue_analytics', {}).get('total_revenue', 0)}")
    
    return report