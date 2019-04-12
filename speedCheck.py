"""
speedCheck - Program to test your Internet Connection, especially made for regular testing
Copyright (C) 2019  Maximilian Waidelich

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""


# Uses the speedtest-cli 2.1.1 from Matt Martz
# https://pypi.org/project/speedtest-cli/
# File is renamed to speedtest.py
import speedtest

from datetime import datetime
from sys import stdout
import time
from threading import Thread
from threading import Lock


"""
Variables to change for your system
"""

line_sep = '\r\n'  # use this one for linux
# line_sep = '\n'  # use this one for Windows

low_download_speed = 25  # what you consider to be a low Download Speed in Mbit/s
low_upload_speed = 1  # what you consider to be a low Upload Speed in Mbit/s

time_spend_file_name = "TimeSpend.txt"  # file name where the times for the progress bar are Stored
speed_test_results_file_name = "SpeedTestResults.txt"  # file name where all the speedtest results will be stored
low_speed_test_results_file_name = "SpeedTestResultsLow.txt"  # file name where the low speedtest results will be stored

# default time in sec if no time has been recorded before.
# I recommend changing these to the values that are near the real one at your machine
# Layout: [searching server time, Download speed check time, Upload speed check time]
times = [2, 10, 10]

"""
The MIT License (MIT)
Copyright (c) 2016 Vladimir Ignatev

Permission is hereby granted, free of charge, to any person obtaining 
a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software 
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


# Uses the Method of Vladimir Ignatev
# https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
# It is slightly changed
def progress(count, total, status='', empty=False):
    global last
    if empty:  # If status has changed and it is shorter than before
        empty_line(last)
    bar_len = 60  # If progress bar does not work properly because console window is to small try changing this value
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    output = '\r[%s] %s%s ...%s' % (bar, percents, '%', status)
    stdout.write(output)
    stdout.flush()
    last = len(output)


last = 0

# empty the line written by the Method progress
def empty_line(length):
    stdout.write('\r' + ' ' * length + '\r')
    stdout.flush


class SpeedTest:
    import time

    global line_sep, times, low_download_speed, low_upload_speed
    global time_spend_file_name, speed_test_results_file_name, low_speed_test_results_file_name

    state_lock = Lock()

    def __init__(self):
        # These Names wil be shown on the progress bar
        self.states = ["searching server", "testing Download Speed", "testing Upload Speed", "finished"]
        self.current_State = self.states[0]

    def progress_bar(self):
        # default time if no time has been recorded before.
        # I recommend changing these to the values that are near the real one at your machine
        # Layout: [searching server time, Download speed check time, Upload speed check time]
        times = self.times
        try:
            f = open(self.time_spend_file_name, "r")
            line = f.readline()
            times2 = line.split(";")
            f.close()
            for i in range(0, 3):
                times[i] = float(times2[i])
        except FileNotFoundError:
            pass
        total_time = times[0] + times[1] + times[2]  # total estimated time needed for the test
        # The different percentages of the 3 Steps
        percentage = [times[0] / total_time * 100, times[1] / total_time * 100, times[2] / total_time * 100]
        percentage[1] += percentage[0]
        percentage[2] += percentage[1]
        time_per_percentage = total_time / 100  # time to wait between 1%
        self.state_lock.acquire()
        used_state = self.current_State
        self.state_lock.release()
        i = 0
        while i <= 100:
            self.state_lock.acquire()
            if used_state == self.current_State:
                same = True
            else:  # if the state has changed since the last time
                same = False
                used_state = self.current_State
                # set the percentage to the beginning of the new stage
                if used_state == self.states[1]:
                    i = int(percentage[0]) + 1
                elif used_state == self.states[2]:
                    i = int(percentage[1]) + 1
            self.state_lock.release()
            if used_state == self.states[0]:  # searching Server state
                if i > int(percentage[0]) + 1:  # if test is taking longer than predicted freeze progress bar
                    i = int(percentage[0]) + 1
                progress(i, 100, used_state, not same)  # drawing new progress bar
            elif used_state == self.states[1]:  # Download speed test state
                if i > int(percentage[1]) + 1:  # if test is taking longer than predicted freeze progress bar
                    i = int(percentage[1]) + 1
                progress(i, 100, used_state, not same)  # drawing new progress bar
            elif used_state == self.states[2]:  # Upload speed test state
                if i == 100:  # if test is taking longer than predicted freeze progress bar
                    i = 99
                progress(i, 100, used_state, not same)  # drawing new progress bar
            elif used_state == self.states[3]:  # Finished speed test state
                progress(100, 100, used_state, True)  # drawing 100% progress bar
                print(self.line_sep)
                return
            else:  # This should never occur
                empty_line(last)
                print("something went terribly wrong")
                quit()
            i += 1
            time.sleep(time_per_percentage)

    def doSpeedTest(self, progressBar):
        # insert here the server id's where you want to test your connection
        # if empty it will search for the nearest server to your machine
        # for example all the Frankfurt, Germany Servers:
        # [3585, 10260, 7560, 9273, 8040, 18667, 10010, 19034, 19116, 18488, 17312, 21528, 23414, 23095, 23870]
        servers = []
        times = [0, 0, 0]  # the times that will be recorded in this session
        s = speedtest.Speedtest()
        progressBar.start()  # start the progressBar Thread

        begin = self.time.time()  # take the time the server search has started
        s.get_servers(servers)  # get all the server that match the filter
        s.get_best_server()  # get the best server from the server found previously
        times[0] = self.time.time() - begin  # compute the total time this action needed

        self.state_lock.acquire()
        self.current_State = self.states[1]  # change state to Download Speed Test state
        self.state_lock.release()
        begin = self.time.time()  # take the time the Download speed test has started
        s.download()  # make the Download Speed Test
        times[1] = self.time.time() - begin  # compute the total time this action needed

        self.state_lock.acquire()
        self.current_State = self.states[2]  # change state to Upload Speed Test state
        self.state_lock.release()
        begin = self.time.time()  # take the time the Upload speed test has started
        s.upload(pre_allocate=False)  # make the Upload Speed Test
        times[2] = self.time.time() - begin  # compute the total time this action needed

        results = s.results  # crawl all the results

        self.state_lock.acquire()
        self.current_State = self.states[3]  # change state to Finished state
        self.state_lock.release()
        progress_bar.join()  # wait for the progress bar to finish
        f = open(speed_test_results_file_name, "a+")  # open file to store speed results

        low_download_speed = self.low_download_speed
        low_upload_speed = self.low_upload_speed
        time = datetime.now().strftime('%d.%m.%Y %H:%M')  # get current Date and Time with the format: DD.MM.YYYY HH:MM

        # if result is at low Speed ad the prefix
        if int(results.download / 1000000) < low_download_speed or int(results.upload / 1000000) < low_upload_speed:
            output = "\t\tLOW SPEED" + self.line_sep
        else:
            output = self.line_sep

        # format all the result
        output2 = "\tDownload: " + str(int(results.download / 1000000)) + " Mbits/s" + self.line_sep
        output2 += "\tUpload: " + str(int(results.upload / 1000000)) + " Mbits/s" + self.line_sep
        output2 += "\tPing " + str(int(results.ping)) + " ms" + self.line_sep
        print(time, output, output2, "\tClient: see Text file", self.line_sep, "\tServer: see Text file", self.line_sep)
        output2 += "\tClient: " + str(results.client) + self.line_sep
        output2 += "\tServer: " + str(results.server) + self.line_sep

        f.write(time + output + output2)  # write results at the end of the file
        f.close()  # close the file

        # if speeds are low then add results to the special file
        if int(results.download / 1000000) < low_download_speed or int(results.upload / 1000000) < low_upload_speed:
            f2 = open(self.low_speed_test_results_file_name, "a+")  # open file
            f2.write(time + self.line_sep + output2)  # write results at the end of the file
            f2.close()  # close the file
        else:  # if speed are normal, store the time it took to the file
            f3 = open(self.time_spend_file_name, "a+")   # open file
            # write times at the end of the file
            f3.write(str(times[0]) + ";" + str(times[1]) + ";" + str(times[2]) + self.line_sep)
            f3.close()  # close file
            f3 = open(self.time_spend_file_name, "r")  # open file again
            all_lines = f3.readlines()  # get all the lines of the file
            f3.close()  # close the file
            if len(all_lines) > 1:  # if there where mor than 1 test stored compute average
                lines = []
                for i in range(1, len(all_lines)):  # get the times for each line
                    lines.append(all_lines[i].split(";"))
                for i in range(0, len(lines)):  # cast from String into float
                    for j in range(0, 3):
                        lines[i][j] = float(lines[i][j])
                avr = [lines[0][0], lines[0][1], lines[0][2]]  # begin to compute average
                for i in range(1, len(lines)):  # continue computing average
                    avr[0] += lines[i][0]
                    avr[1] += lines[i][1]
                    avr[2] += lines[i][2]
                for i in range(0, 3):  # finish computing average and cast into String
                    avr[i] /= len(lines)
                    avr[i] = str(avr[i])
                output = ";".join(avr) + self.line_sep
                # replace any unwanted line separators
                if self.line_sep == '\r\n':
                    not_correct = '\n'
                else:
                    not_correct = '\r\n'
                for i in range(1,len(all_lines)):
                    all_lines[i] = all_lines[i].replace(not_correct, self.line_sep)
                # put average to beginning of file
                all_lines[0] = output
                f3 = open(self.time_spend_file_name, "w")  # open file
                f3.writelines(all_lines)  # write new values into file
                f3.close()  # close file


# Starts the speed Check with 2 Threads
speedcheck = SpeedTest()
progress_bar = Thread(target=speedcheck.progress_bar, args=())
speedtest2 = Thread(target=speedcheck.doSpeedTest, args=(progress_bar,))
speedtest2.start()
speedtest2.join()
