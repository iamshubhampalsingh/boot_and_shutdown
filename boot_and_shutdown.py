import unittest
import os
import sys
import time
import unittest
import subprocess
from shutil import copy,rmtree
from uiautomator2.exceptions import UiObjectNotFoundError
from androidutils.device import Device
from androidutils.error import RunWithManualStepsError
## Logs -start
from androidutils.pylogging import PyLogger

TAG = os.path.basename(__file__)
logger = PyLogger.getlogger(__name__)
logc = logger.critical
loge = logger.error
logw = logger.warning
logd = logger.debug
logi = logger.info
## Logs -end

class BSTest(unittest.TestCase):
    """
    A class to handle boot and shutdown test case
    """
    def __init__(self, *args, **kwargs):
      super(BSTest, self).__init__(*args, **kwargs)
      self.classname = self.__class__.__name__

    @classmethod
    def setUpClass(cls):
        logw("setup")
        cls.dev = Device()

    @classmethod
    def tearDownClass(cls):
        logw("teardown")
        cls.dev.adbclient.remote_disconnect()

    def msg(self, tag, msg):
       return ("[{}#{}]: {}".format(self.dev.name, tag, msg))

    def start(self, test_case_name):
      logw(self.msg(test_case_name, '---------------------------------'))
      logw(self.msg(test_case_name, "Start test: " + test_case_name))
      logw(self.msg(test_case_name, '---------------------------------'))
      self.dev.unlock_lockscreen()

    def test_System_BS_001_power_off(self):
        tag = self.classname + "." + self.test_System_BS_001_power_off.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        status = self.schedule_power_on_device(2)
        if status is False:
            self.fail("Schdeule power on failed to set")
        logi("Device is going to shutdown, please for 2 minutes till device power ON")
        is_device_off = self.shutdown_device()

        time.sleep(120)
        status = self.dev.wait_and_get_homescreen_status()
        if status['ret'] is not True :
            self.fail('The device is not booted properly')

        self.dev.unlock_lockscreen()
        if not is_device_off :
            self.fail("The device was not shutdown")

    def test_System_BS_002_power_on(self):
        tag = self.classname + "." + self.test_System_BS_002_power_on.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        status = self.schedule_power_on_device(2)
        if status is False:
            self.fail("Schdeule power on failed to set")
        logi("Device is going to shutdown, please for 2 minutes till device power ON")
        self.shutdown_device()

        time.sleep(120)
        status = self.dev.wait_and_get_homescreen_status()
        if status['ret'] is not True :
            self.fail('The device is not booted properly')
        self.dev.unlock_lockscreen()

    def test_System_BS_003_boot_animation(self):
        tag = self.classname + "." + self.test_System_BS_003_boot_animation.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        logi("Device is rebooting, please wait till it get powered ON")
        self.dev.adbdevice.reboot()
        status = self.dev.wait_and_get_homescreen_status()
        if status['ret'] is not True :
            self.fail('The device is not booted properly')
        self.dev.unlock_lockscreen()

    def test_System_BS_004_power_on_off(self):
        tag = self.classname + "." + self.test_System_BS_004_power_on_off.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        logi("Device is rebooting, please wait till it get powered ON")
        self.dev.adbdevice.reboot()
        status = self.dev.wait_and_get_homescreen_status()

        if status['ret'] is not True :
            self.fail('The device is not booted properly')
        self.dev.unlock_lockscreen()

    def test_System_BS_005_set_alarm(self):
        tag = self.classname + "." + self.test_System_BS_005_set_alarm.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        status,sleeptime,start_time = self.set_alarm(4)
        if status is False:
            self.fail("Alarm did not set properly")

        self.shutdown_device()
        end_time = round(time.time())
        total_sleeptime = sleeptime - (end_time - start_time) #calculate actual sleep time after alarm set
        logi("Device is going to shutdown, wait for %d seconds till device power ON for alarm"%(total_sleeptime))

        time.sleep(total_sleeptime)
        if self.dev.wait_and_get_boot_complete() is True :
            timeout = 0
            while True :
                if timeout > 60 :
                    self.fail('Alarm did not rang')
                if 'AlarmActivity' or 'net.oneplus.launcher' in self.dev.get_current_focused_activity() :
                    self.kill_alarm()
                    time.sleep(2)
                    break
                timeout +=1
                time.sleep(1)
        else :
            self.fail('Device did not boot properly')

    def test_System_BS_006_reboot_after_set_pin(self):
        tag = self.classname + "." + self.test_System_BS_006_reboot_after_set_pin.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        self.dev.set_lock_screen_pin()
        logi("Device is rebooting, please wait till it get powered ON")
        self.dev.adbdevice.reboot()
        status = self.dev.wait_and_get_boot_complete()
        if status is not True :
            self.fail('The device is not booted properly')
        status = self.dev.unlock_lockscreen_pin_after_reboot()
        if status is False :
            self.fail("Device is not able to unlock lockscreen")
        status = self.dev.remove_lock_screen_pin()
        if status is False :
            self.fail("Device is not able to unlock lockscreen")

    def test_System_BS_007_reboot_safe_mode(self):
        tag = self.classname + "." + self.test_System_BS_007_reboot_safe_mode.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        manual_steps = "\nPreconditions: None \n" \
                                     "Steps: \n" \
                                     "1. Long press power key until the popup menu appears \n" \
                                     "2. Long press power-off button or restart button, pop up prompt to reboot to safe mode \n" \
                                     "3. Click ok to reboot to safe mode \n" \
                                     "Expected result: \n" \
                                     "Device can boot into safe mode normally"

        raise RunWithManualStepsError(manual_steps)

    def test_System_BS_008_press_power_safe_mode(self):
        tag = self.classname + "." + self.test_System_BS_008_press_power_safe_mode.__name__
        self.dev.set_tag(tag)
        self.start(tag)

        manual_steps = "\nPreconditions: Device is in power off state \n" \
                                     "Steps: \n" \
                                     "1. Press power key to power on \n" \
                                     "2. Long press volume-down key when boot logo appears \n" \
                                     "3. When launcher boots up, check if there is a safe mode typeface in the lower left corner \n" \
                                     "Expected result: \n" \
                                     "Device can boot into safe mode normally"

        raise RunWithManualStepsError(manual_steps)

    def shutdown_device(self):
        """Shutdown the device from adb shell
            wait for for 2 seconds buffer time before rebooting
            wait for 5 seconds buffer time to get shutdown(the time may be more when proper shutdown is done)
            Args: None
        Returns:
            bool: Whether device is shutdown.
        """
        time.sleep(2) # borrow time to get set to shutdown
        subprocess.check_output("adb shell reboot -p", shell=True)
        time.sleep(5) # wait till device shutdown happens
        try:
            subprocess.check_output("adb shell ps", shell=True,stderr=subprocess.STDOUT)
        except :
            return True
        return False

    def schedule_power_on_device(self, time_min): #time in minutes from current time
        """Scheduled power on device

        Args:  Enter time in minutes, it will set schedule after adding time in current time

        """
        d = self.dev.uidevice
        d.app_stop("com.android.settings")
        d.app_start("com.android.settings", ".homepage.SettingsHomepageActivity")
        d.app_wait("com.android.settings", timeout=20.0)
        d(text="Search settings").click()
        d(className="android.widget.ImageButton")[1].click()
        d(text="Clear history").click()
        d.send_keys("Scheduled power on/off")
        d(text="Scheduled power on/off")[1].click()
        d(text="Scheduled power on/off").click()
        if(d(className='android.widget.Switch', resourceId="android:id/switch_widget").info['text'] == "ON"): #Check if it is still ON, make it off
            d(text='Power on').click()
        d(text="Set time to power on").click()
        d(className="android.widget.ImageButton", resourceId="com.android.settings:id/toggle_mode").click()

        hours, mins, timeframe = self.get_alarm_set_time(time_min)
        d(className="android.widget.EditText", resourceId="com.android.settings:id/input_hour").set_text(str(hours))
        d(className="android.widget.EditText", resourceId="com.android.settings:id/input_minute").set_text(str(mins))
        d(text=timeframe).click()
        d(text="OK").click()
        time.sleep(2)
        return self.is_schedule_power_on_set()

    def is_schedule_power_on_set(self):
        """Scheduled power on device

        Args:  Enter time in minutes, it will set schedule after adding time in current time
        Return:
            Boolean if schedule power on set
        """
        d = self.dev.uidevice
        d.app_stop("com.android.settings")
        d.app_start("com.android.settings", ".homepage.SettingsHomepageActivity")
        d.app_wait("com.android.settings", timeout=20.0)
        d(text="Search settings").click()
        d(className="android.widget.ImageButton")[1].click()
        d(text="Clear history").click()
        d.send_keys("Scheduled power on/off")
        d(text="Scheduled power on/off")[1].click()
        d(text="Scheduled power on/off").click()
        if(d(className='android.widget.Switch', resourceId="android:id/switch_widget").info['text'] == "ON"): #Check if it is ON
            return True
        return False

    def set_alarm(self,time_min): # set alram for a time in minutes from current time
        """Set alarm in the device

        Args:  Enter time in minutes, it will set schedule after adding time in current time
        Return:
            Boolean if alarm is set
        """
        d = self.dev.uidevice
        d.app_stop("com.oneplus.deskclock")
        d.app_start("com.oneplus.deskclock", ".DeskClock")
        d.app_wait("com.oneplus.deskclock", timeout=20.0)
        try:
            d(text="ALLOW").click()#if clock app is opened for the first time
            d(text="GOT IT").click()
        except:
            pass
        d(className="android.widget.RelativeLayout", resourceId="com.oneplus.deskclock:id/fab").click()
        d(className="android.widget.ImageButton", resourceId="com.oneplus.deskclock:id/toggle_mode").click()

        hours,mins,timeframe = self.get_alarm_set_time(time_min) # timeframe is AM/PM
        d(className="android.widget.EditText", resourceId="com.oneplus.deskclock:id/input_hour").set_text(str(hours))
        d(className="android.widget.EditText", resourceId="com.oneplus.deskclock:id/input_minute").set_text(str(mins))
        d(text=timeframe).click()
        d(className="android.widget.TextView", resourceId="com.oneplus.deskclock:id/menu_item_save").click()

        start_time = round(time.time())
        sleeptime = self.get_sleep_time_for_alarm(time_min) #get sleep time for alarm if given 4 minutes
        time.sleep(2)
        return self.is_alarm_set(), sleeptime+2, start_time

    def kill_alarm(self):
        """kill alarm while running

        Args:  None
        Return:
            Boolean : return True is successfully killed alarms
        """
        d = self.dev.uidevice
        d.app_stop("com.oneplus.deskclock")
        time.sleep(2)
        self.dev.unlock_lockscreen()
        d.app_stop("com.oneplus.deskclock")
        d.app_start("com.oneplus.deskclock", ".DeskClock")
        d.app_wait("com.oneplus.deskclock", timeout=20.0)
        try :
            for switch in d(className='android.widget.Switch'):
                if switch.info['text'] == "ON" :
                    switch.click()
            return True
        except:
            return False
        return False

    def get_sleep_time_for_alarm(self,time):
        """Get sleep time in seconds from current time

        Args:  Takes time in minutes, to which number of mintues alarm is going to set

        Returns: It will return time to sleep in seconds
        """
        time_arr_str = subprocess.check_output("adb shell date +%H:%M:%S", shell=True).decode('UTF-8').rstrip().split(':')
        time_arr_int = [int(num_str) for num_str in time_arr_str]
        secs = time_arr_int[2]
        return (4*60) - secs

    def is_alarm_set(self):
        """Check if alarm is set

        Args:  None
        Return:
            Boolean : return True if a single alarm is in set state
        """
        d = self.dev.uidevice
        d.app_stop("com.oneplus.deskclock")
        time.sleep(2)
        d.app_stop("com.oneplus.deskclock")
        d.app_start("com.oneplus.deskclock", ".DeskClock")
        d.app_wait("com.oneplus.deskclock", timeout=20.0)
        try :
            for switch in d(className='android.widget.Switch'):
                if switch.info['text'] == "ON" :
                    return True
        except:
            return False
        return False

    def get_alarm_set_time(self,time):
        """Get alarm time

        Args:  Takes time in minutes

        Returns: It will return tuple of hours, minutes and timeframe after adding time in minutes to current time
        """
        time_arr_str = subprocess.check_output("adb shell date +%H:%M", shell=True).decode('UTF-8').rstrip().split(':')
        time_arr_int = [int(num_str) for num_str in time_arr_str]
        hrs = time_arr_int[0]
        mins = time_arr_int[1]
        timeframe = 'AM'

        if mins+time > 59 :
            hrs = hrs+1
        mins = (mins+time)%60

        if hrs/12 >= 1 :
            timeframe = 'PM'
            if hrs > 12 :
                hrs = hrs%12
        if hrs == 0:
            hrs = 12
        return hrs, mins, timeframe
