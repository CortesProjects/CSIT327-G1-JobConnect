from .models import Notification

def create_notification(user, notification_type, title, message, link='', 
                       related_job_id=None, related_application_id=None):
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
    return create_notification(
        user=user,
        notification_type='job_alert',
        title='New Job Match',
        message=f'A new job matching "{alert_name}" is available: {job.title}',
        link=f'/jobs/{job.id}/',
        related_job_id=job.id,
    )


def notify_job_posted_success(employer, job):
    return create_notification(
        user=employer,
        notification_type='job_posted',
        title='Job Posted Successfully',
        message=f'Your job posting "{job.title}" is now live',
        link=f'/dashboard/employer/jobs/{job.id}/',
        related_job_id=job.id,
    )


def bulk_notify(users, notification_type, title, message, link=''):
   
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
