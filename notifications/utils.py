"""
Notification utilities for creating notifications throughout the application.
"""
from .models import Notification


def create_notification(user, notification_type, title, message, link='', 
                       related_job_id=None, related_application_id=None):
    """
    Create a notification for a user.
    
    Args:
        user: User object who will receive the notification
        notification_type: Type of notification (see Notification.NOTIFICATION_TYPES)
        title: Notification title (max 200 chars)
        message: Notification message content
        link: Optional URL link for the notification
        related_job_id: Optional ID of related job
        related_application_id: Optional ID of related application
    
    Returns:
        Notification object
    
    Example:
        create_notification(
            user=applicant_user,
            notification_type='application_status',
            title='Application Status Update',
            message='Your application for Software Engineer has been shortlisted',
            link='/dashboard/applicant/applications/',
            related_application_id=application.id
        )
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        related_job_id=related_job_id,
        related_application_id=related_application_id,
    )
    return notification


def notify_application_received(employer, applicant, job, application):
    """Notify employer when they receive a new job application."""
    return create_notification(
        user=employer,
        notification_type='application_received',
        title='New Application Received',
        message=f'{applicant.get_full_name() or applicant.email} applied for {job.title}',
        link=f'/dashboard/employer/jobs/{job.id}/applications/',
        related_job_id=job.id,
        related_application_id=application.id,
    )


def notify_application_status_change(applicant, job, new_status):
    """Notify applicant when their application status changes."""
    status_messages = {
        'reviewed': 'Your application is being reviewed',
        'interview': 'You have been invited for an interview',
        'rejected': 'Your application was not selected this time',
        'hired': 'Congratulations! You have been hired',
    }
    
    message = status_messages.get(new_status, f'Your application status changed to {new_status}')
    
    return create_notification(
        user=applicant,
        notification_type=f'application_{new_status}',
        title='Application Status Update',
        message=f'{message} for {job.title}',
        link='/dashboard/applicant/applications/',
        related_job_id=job.id,
    )


def notify_application_shortlisted(applicant, job, application):
    """Notify applicant when they are shortlisted."""
    return create_notification(
        user=applicant,
        notification_type='application_shortlist',
        title='Application Shortlisted! 🎉',
        message=f'Great news! You have been shortlisted for {job.title}',
        link='/dashboard/applicant/applications/',
        related_job_id=job.id,
        related_application_id=application.id,
    )


def notify_job_alert_match(user, job, alert_name):
    """Notify user when a new job matches their job alert."""
    return create_notification(
        user=user,
        notification_type='job_alert',
        title='New Job Match',
        message=f'A new job matching "{alert_name}" is available: {job.title}',
        link=f'/jobs/{job.id}/',
        related_job_id=job.id,
    )


def notify_job_posted_success(employer, job):
    """Notify employer when their job is successfully posted."""
    return create_notification(
        user=employer,
        notification_type='job_posted',
        title='Job Posted Successfully',
        message=f'Your job posting "{job.title}" is now live',
        link=f'/dashboard/employer/jobs/{job.id}/',
        related_job_id=job.id,
    )


def bulk_notify(users, notification_type, title, message, link=''):
    """
    Create the same notification for multiple users.
    
    Args:
        users: List or queryset of User objects
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        link: Optional URL link
    
    Returns:
        List of created Notification objects
    """
    notifications = []
    for user in users:
        notif = create_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )
        notifications.append(notif)
    return notifications
