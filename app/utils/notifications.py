from fastapi import BackgroundTasks
import boto3
from botocore.exceptions import ClientError

def send_notification(message: str, subject: str, recipient: str):
    """
    Send a notification using AWS Simple Notification Service (SNS).
    
    Args:
        message (str): The message to be sent.
        subject (str): The subject of the notification.
        recipient (str): The recipient's email address or phone number.
    """
    sns_client = boto3.client('sns')

    try:
        response = sns_client.publish(
            Message=message,
            Subject=subject,
            TargetArn=recipient  # This should be the ARN of the SNS topic or endpoint
        )
        return response
    except ClientError as e:
        print(f"Error sending notification: {e}")
        return None

def notify_on_deployment(deployment_info: dict, recipient: str):
    """
    Notify the recipient about a deployment event.
    
    Args:
        deployment_info (dict): Information about the deployment.
        recipient (str): The recipient's email address or phone number.
    """
    message = f"Deployment Notification:\n\nDetails: {deployment_info}"
    subject = "Deployment Successful"
    send_notification(message, subject, recipient)

def notify_on_error(error_info: dict, recipient: str):
    """
    Notify the recipient about an error event.
    
    Args:
        error_info (dict): Information about the error.
        recipient (str): The recipient's email address or phone number.
    """
    message = f"Error Notification:\n\nDetails: {error_info}"
    subject = "Error Occurred"
    send_notification(message, subject, recipient)