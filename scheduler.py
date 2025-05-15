import logging
import threading
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class ScheduleManager:
    """
    Manages scheduling of chart generation and delivery tasks.
    """
    def __init__(self):
        """
        Initialize the schedule manager with a background scheduler.
        """
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.job_map = {}  # To keep track of scheduled jobs
        logging.info("Schedule manager initialized")
        
    def add_job(self, job_id, func, trigger, **trigger_args):
        """
        Add a job to the scheduler.
        
        Args:
            job_id (str): Unique identifier for the job
            func (callable): The function to call when the job is triggered
            trigger: The trigger type (cron, interval, date)
            **trigger_args: Arguments specific to the trigger type
            
        Returns:
            bool: True if job was added successfully, False otherwise
        """
        try:
            job = self.scheduler.add_job(func, trigger, **trigger_args, id=job_id)
            self.job_map[job_id] = job
            logging.info(f"Added scheduled job: {job_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to add job {job_id}: {e}")
            return False
            
    def add_cron_job(self, job_id, func, day_of_week=None, hour=None, minute=None):
        """
        Add a job with a cron trigger for simplified scheduling.
        
        Args:
            job_id (str): Unique identifier for the job
            func (callable): The function to call when the job is triggered
            day_of_week (str, optional): Day of week (0-6 or mon,tue,wed,thu,fri,sat,sun)
            hour (int, optional): Hour (0-23)
            minute (int, optional): Minute (0-59)
            
        Returns:
            bool: True if job was added successfully, False otherwise
        """
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=hour,
            minute=minute
        )
        return self.add_job(job_id, func, trigger)
        
    def remove_job(self, job_id):
        """
        Remove a scheduled job.
        
        Args:
            job_id (str): Unique identifier for the job
            
        Returns:
            bool: True if job was removed successfully, False otherwise
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.job_map:
                del self.job_map[job_id]
            logging.info(f"Removed scheduled job: {job_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to remove job {job_id}: {e}")
            return False
            
    def shutdown(self):
        """
        Shut down the scheduler.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logging.info("Schedule manager shut down")

def create_schedule_manager_from_config(config, process_func):
    """
    Create a ScheduleManager and set up jobs based on configuration.
    
    Args:
        config (dict): Configuration containing schedule settings
        process_func (callable): The function to call for each scheduled job
        
    Returns:
        ScheduleManager: Initialized schedule manager
    """
    manager = ScheduleManager()
    
    if 'schedules' not in config:
        logging.warning("No schedules found in configuration")
        return manager
        
    for schedule in config['schedules']:
        job_id = schedule.get('id', f"job_{len(manager.job_map)}")
        day_of_week = schedule.get('day_of_week')
        hour = schedule.get('hour')
        minute = schedule.get('minute')
        
        manager.add_cron_job(job_id, process_func, day_of_week, hour, minute)
    
    return manager 